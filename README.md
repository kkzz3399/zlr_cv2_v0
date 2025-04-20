# 行人检测视频流系统

基于Vue和Flask的双视频流行人检测系统，实时显示原始摄像头画面和YOLOv3处理后的行人检测画面。

## 功能特点

- 实时双视频流显示
- 基于YOLOv3的行人检测
- 响应式前端界面
- RESTful API接口
- WebSocket实时通信

## 技术栈

- 前端：Vue 3 + Vite
- 后端：Python Flask
- 模型：YOLOv3 (基于OpenCV DNN模块)
- 通信：HTTP + WebSocket

## 安装指南

### 前置要求

- Python 3.8+
- Node.js 16+
- OpenCV 4.5+
- 摄像头设备

### 后端安装

```bash
cd backend/project
pip install -r requirements.txt
```

### 前端安装

```bash
cd vue-project1
npm install
```

## 运行项目

1. 启动后端服务：

```bash
cd backend/project
python app.py
```

2. 启动前端开发服务器：

```bash
cd vue-project1
npm run dev
```

3. 访问 `http://localhost:5173` 查看应用

## 项目结构

```
vue1/
├── backend/              # Flask后端
│   ├── project/
│   │   ├── app.py        # 主应用文件
│   │   ├── yolov3.weights # YOLO权重文件
│   │   └── ...           # 其他模型文件
├── vue-project1/         # Vue前端
│   ├── src/
│   │   ├── components/   # Vue组件
│   │   ├── views/        # 页面视图
│   │   └── ...           # 其他前端代码
│   └── ...               # 前端配置文件
```

## 配置选项

后端配置 (`backend/project/config.py`):

```python
# 摄像头设置
CAMERA_INDEX = 0  # 默认摄像头

# YOLO模型配置
YOLO_WEIGHTS = "yolov3.weights"
YOLO_CONFIG = "yolov3.cfg"
YOLO_CLASSES = "coco.names"

# 服务器设置
HOST = "0.0.0.0"
PORT = 5000
```

## 常见问题

Q: 视频流显示黑屏怎么办？
A: 
1. 检查摄像头是否正确连接
2. 验证后端服务是否正常运行
3. 查看浏览器控制台是否有错误

Q: 行人检测不准确？
A:
1. 调整检测阈值 (app.py中的confidence参数)
2. 确保模型文件完整
3. 检查OpenCV版本兼容性
