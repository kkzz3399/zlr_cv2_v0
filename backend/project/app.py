import time
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from models import User
import hashlib  # 用于密码哈希
import jwt
import datetime
import os
import threading
import base64
import cv2
import numpy as np
import traceback
from detect_image import picture_detect
from detect_video import video_detect
from get_camera import get_connected_cameras
from flask import Flask, request, jsonify
import os
from datetime import datetime
import uuid








app = Flask(__name__, static_folder='../../vue-project1/dist')
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading',
                   logger=True,
                   engineio_logger=True)
# 确保保存目录存在
SAVED_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), 'saved_videos')
os.makedirs(SAVED_VIDEOS_DIR, exist_ok=True)



# 全局摄像头对象
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def generate_raw_feed():
    """生成原始视频流"""
    print("原始视频流生成器启动")
    while True:
        success, frame = camera.read()
        if not success:
            print("无法从摄像头读取帧")
            break
        print(f"成功读取帧，尺寸: {frame.shape if frame is not None else '无帧'}")
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("帧编码失败")
            break
        print(f"帧编码成功，大小: {len(buffer)}字节")
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_processed_feed():
    """生成处理后视频流"""
    print("处理后视频流生成器启动")
    try:
        # 加载YOLO模型
        net, classes, _, output_layers = load_yolo()
        print("YOLO模型加载成功")
        
        while True:
            try:
                # 初始化每帧的检测变量
                boxes = []
                confidences = []
                class_ids = []
                
                success, frame = camera.read()
                if not success:
                    print("无法从摄像头读取帧(处理后)")
                    break
                print(f"成功读取帧(处理后)，尺寸: {frame.shape}")
                    
                # 行人检测处理
                height, width = frame.shape[:2]
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)
                print(f"完成YOLO检测，输出层数: {len(outs)}")
                
                # 收集检测结果
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        # 提高置信度阈值到0.7，且只检测person类(class_id=0)
                        if confidence > 0.7 and class_id == 0:  
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
                
                # 应用NMS抑制
                if len(boxes) > 0:
                    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.4)
                    print(f"检测到{len(indexes)}个有效行人")
                    
                    # 绘制检测框
                    for i in indexes:
                        x, y, w, h = boxes[i]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, f'Person {confidences[i]:.2f}', (x, y - 5), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                else:
                    print("未检测到符合要求的行人")

                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    print("处理后帧编码失败")
                    break
                print(f"处理后帧编码成功，大小: {len(buffer)}字节")
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            except Exception as e:
                print(f"处理视频帧时出错: {str(e)}")
                traceback.print_exc()
                break
                
    except Exception as e:
        print(f"初始化视频处理时出错: {str(e)}")
        traceback.print_exc()

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("处理后帧编码失败")
            
        print(f"处理后帧编码成功，大小: {len(buffer)}字节")
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 视频流端点
@app.route('/video/raw')
def video_raw():
    return Response(generate_raw_feed(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video/processed')
def video_processed():
    return Response(generate_processed_feed(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# WebSocket连接测试端点
@app.route('/api/ws-test')
def ws_test():
    return jsonify({"status": "WebSocket服务运行正常"}), 200
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/video/*": {
        "origins": "*",
        "methods": ["GET"],
        "allow_headers": []
    }
})

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # 处理API请求
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
        
    # 处理静态文件请求
    static_file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(static_file_path) and not os.path.isdir(static_file_path):
        return send_from_directory(app.static_folder, path)
    
    # 处理前端路由请求
    return send_from_directory(app.static_folder, 'index.html')
print("Server started")

# 密钥用于生成和验证 JWT
SECRET_KEY = 'your_secret_key'

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    if not username or not email or not password or not confirmPassword:
        return jsonify({"error": "用户名、邮箱和密码不能为空"}), 400

    # 检查密码是否一致
    if password != confirmPassword:
        return jsonify({"error": "两次输入的密码不一致"}), 400

    # 创建用户
    try:
        user_id = User.create_user(username, email, password)
        token = generate_jwt_token(user_id)
        return jsonify({
            "message": "注册成功",
            "user": {
                "id": user_id,
                "username": username,
                "email": email
            },
            "token": token
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    user = User.get_user_by_username(username)
    if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
        token = generate_jwt_token(user['id'])
        return jsonify({
            "message": "登录成功",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            },
            "token": token
        }), 200
    else:
        return jsonify({"error": "用户名或密码错误"}), 401

# 获取当前登录用户的信息
@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "未提供令牌"}), 401

    user_id = verify_jwt_token(token)
    if not user_id:
        return jsonify({"error": "无效的令牌"}), 401

    user = User.get_user_by_id(user_id)
    if user:
        return jsonify({
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            }
        }), 200
    return jsonify({"error": "未找到用户"}), 404

# 获取单个用户
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.get_user_by_id(user_id)
    if user:
        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "email": user['email']
        }), 200
    return jsonify({"error": "该用户不存在"}), 404

# 添加新用户
@app.route('/api/users', methods=['POST'])
def add_user():
    # 假设这里有一个管理员验证逻辑
    # if not is_admin():
    #     return jsonify({"error": "无权限访问"}), 403
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "用户名、邮箱和密码不能为空"}), 400

    # 创建用户
    try:
        user_id = User.create_user(username, email, password)
        return jsonify({
            "message": "用户添加成功",
            "user": {
                "id": user_id,
                "username": username,
                "email": email
            }
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# 修改用户信息
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # 假设这里有一个管理员验证逻辑
    # if not is_admin():
    #     return jsonify({"error": "无权限访问"}), 403
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 检查是否提供有效的更新数据
    if not username and not email and not password:
        return jsonify({"error": "需要提供有效的更新数据"}), 400

    # 更新用户
    try:
        User.update_user(user_id, username, email, password)
        return jsonify({"message": "修改成功"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# 删除用户
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    data = request.get_json(force=True)
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "需要提供用户名和密码"}), 400

    user = User.get_user_by_id(user_id)

    if not user:
        return jsonify({"error": "未找到用户"}), 404

    # 双重验证：用户名和密码
    if user['username'] != data['username']:
        return jsonify({"error": "用户名不匹配"}), 401
        
    # 从嵌套字典中获取实际密码字符串
    actual_password = data['password']['password']
    if user['password'] != hashlib.sha256(actual_password.encode()).hexdigest():
        return jsonify({"error": "密码不正确"}), 401

    try:
        User.delete_user(user_id)
        return jsonify({"message": "用户删除成功"}), 200
    except Exception as e:
        # 记录数据库操作异常
        app.logger.error(f"删除用户失败: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500

# 图片检测API
@app.route('/api/detect/image', methods=['POST'])
def detect_image():
    if 'file' not in request.files:
        return jsonify({"error": "未上传文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400
    
    # 保存上传的图片 - 使用绝对路径
    upload_dir = os.path.abspath(os.path.join(app.static_folder, 'uploads'))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.abspath(os.path.join(upload_dir, file.filename))
    try:
        file.save(file_path)
    except Exception as e:
        app.logger.error(f"文件保存失败: {str(e)}")
        return jsonify({"error": "文件保存失败"}), 500
    
    try:
        # 处理图片
        result_path = picture_detect(file_path)
        # 返回处理后的图片URL
        result_url = f"/uploads/{os.path.basename(result_path)}"
        return jsonify({"result_url": result_url}), 200
    except Exception as e:
        app.logger.error(f"图片处理失败: {str(e)}")
        app.logger.error(f"文件路径: {file_path}")
        app.logger.error(f"堆栈跟踪: {traceback.format_exc()}")
        return jsonify({"error": "图片处理失败，请检查服务器日志"}), 500

# 视频检测API
@app.route('/api/detect/video', methods=['POST'])
def detect_video():
    if 'file' not in request.files:
        return jsonify({"error": "未上传文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400
    
    # 确保上传目录存在
    upload_dir = os.path.abspath(os.path.join(app.static_folder, 'uploads'))
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存上传的视频
    input_path = os.path.abspath(os.path.join(upload_dir, file.filename))
    output_path = os.path.abspath(os.path.join(upload_dir, f"processed_{file.filename}"))
    
    try:
        file.save(input_path)
        
        # 调用视频处理函数
        video_detect(input_path, output_path)
        
        # 验证视频文件
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return jsonify({
                "success": False,
                "error": "视频处理失败，输出文件为空"
            }), 500
            
        # 返回处理后的视频URL（使用完整URL）
        return jsonify({
            "success": True,
            "processed_url": f"http://{request.host}/uploads/processed_{file.filename}",
            "message": "视频处理成功"
        })
    except Exception as e:
        return jsonify({
            "error": f"视频处理失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

# 摄像头列表API
@app.route('/api/cameras/list', methods=['GET'])
def get_camera_list():
    try:
        camera_ids = get_connected_cameras()
        return jsonify({
            "status": "success",
            "cameras": [{"id": idx, "camera_id": cam_id} for idx, cam_id in enumerate(camera_ids)]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# 摄像头检测API
@app.route('/api/camera/control', methods=['POST'])
def detect_camera():
    try:
        # 启动摄像头检测
        camera_thread = threading.Thread(target=camera_detect, daemon=True)
        camera_thread.start()
        return jsonify({"message": "摄像头检测已启动"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 保存监控API
@app.route('/api/save_video', methods=['POST'])
def save_video():
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': 'No video file provided'}), 400

        video_file = request.files['video']
        camera_id = request.form.get('cameraId', 'unknown')

        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"video_{timestamp}_{camera_id}_{unique_id}.webm"
        save_path = os.path.join(SAVED_VIDEOS_DIR, filename)

        # 保存视频文件
        video_file.save(save_path)

        return jsonify({
            'success': True,
            'filePath': save_path,
            'message': 'Video saved successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving video: {str(e)}'
        }), 500

# 历史视频查询API
@app.route('/api/history/videos', methods=['GET'])
def get_history_videos():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "日期参数缺失"}), 400
    
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "日期格式错误，请使用YYYY-MM-DD格式"}), 400
    
    videos = []
    for filename in os.listdir(SAVED_VIDEOS_DIR):
        if filename.endswith('.webm'):
            # 解析文件名中的日期部分
            try:
                date_part = filename.split('_')[1]  # video_20250420_...
                file_date = datetime.strptime(date_part[:8], "%Y%m%d").date()
                if file_date == target_date:
                    videos.append({
                        'id': filename,
                        'name': filename,
                        'date': date_part[:8],
                        'time': date_part[8:],
                        'url': f'/api/history/videos/{filename}'
                    })
            except (IndexError, ValueError):
                continue
    
    return jsonify({"data": videos})

# 视频文件下载API
@app.route('/api/history/videos/<filename>', methods=['GET'])
def download_video(filename):
    return send_from_directory(SAVED_VIDEOS_DIR, filename)

# 生成 JWT 令牌
def generate_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        #'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# 验证 JWT 令牌
def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# 初始化全局变量
classes = []
output_layers = []
def load_yolo():
    # 获取当前脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    weights_path = os.path.join(script_dir, "yolov3.weights")
    cfg_path = os.path.join(script_dir, "yolov3.cfg")
    names_path = os.path.join(script_dir, "coco.names")

    # 检查文件是否存在
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"权重文件不存在: {weights_path}")
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"配置文件不存在: {cfg_path}")
    if not os.path.exists(names_path):
        raise FileNotFoundError(f"类别文件不存在: {names_path}")

    # 加载模型
    net = cv2.dnn.readNet(weights_path, cfg_path)
    with open(names_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    return net, classes, colors, output_layers





def send_frame(frame, frame_type):
    """发送帧数据到WebSocket客户端"""
    try:
        # 检查帧是否有效
        if frame is None or frame.size == 0:
            print("无效的帧数据")
            return

        # 编码帧为JPEG
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            print("帧编码失败")
            return

        # 转换为base64
        frame_data = base64.b64encode(buffer).decode('utf-8')

        # 发送帧数据
        socketio.emit('frame', {
            'type': frame_type,
            'data': frame_data
        })
        print(f"已发送{frame_type}帧数据, 大小: {len(frame_data)}字节")
    except Exception as e:
        print(f"发送帧数据时出错: {str(e)}")

def camera_detect():
    """实时摄像头检测并发送双流数据"""
    net, classes, colors, output_layers = load_yolo()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法获取帧")
                break

            # 原始帧
            original_frame = cv2.resize(frame, (640, 480))
            send_frame(original_frame, 'original')

            # 处理后的帧
            processed_frame = original_frame.copy()
            height, width, channels = processed_frame.shape

            # YOLO处理
            blob = cv2.dnn.blobFromImage(processed_frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # 检测结果处理
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # 绘制检测结果
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = (0, 0, 255)
                    cv2.rectangle(processed_frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(processed_frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            send_frame(processed_frame, 'processed')

            time.sleep(0.05)  # 控制帧率

    finally:
        cap.release()

@socketio.on('connect')
def handle_connect():
    print('客户端连接, ID:', request.sid)
    try:
        # 启动摄像头检测线程
        if not hasattr(app, 'camera_thread') or not app.camera_thread.is_alive():
            app.camera_thread = threading.Thread(target=camera_detect, daemon=True)
            app.camera_thread.start()
            print("摄像头检测线程已启动")
        # 发送连接确认消息
        emit('connection_ack', {'message': 'WebSocket连接成功'})
    except Exception as e:
        print(f"启动摄像头线程时出错: {str(e)}")
        emit('connection_error', {'error': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端断开连接, ID:', request.sid)


def check_port_available(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def run_flask_app():
    if not check_port_available(5000):
        print("错误：端口5000已被占用，请关闭占用该端口的程序或使用其他端口")
        return
    
    print("启动WebSocket服务...")
    print(f"WebSocket测试端点: http://localhost:5000/api/ws-test")
    print(f"WebSocket连接地址: ws://localhost:5000/ws/camera")
    
    socketio.run(app, 
                debug=True, 
                port=5000, 
                allow_unsafe_werkzeug=True,
                use_reloader=False)

if __name__ == '__main__':
    run_flask_app()
