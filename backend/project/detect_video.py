import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time

def load_yolo():
    # 加载YOLO模型及配置文件，读取COCO数据集中的类别名称，并初始化颜色和输出层信息
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    return net, classes, colors, output_layers

def video_detect(video_path, output_path):
    net, classes, colors, output_layers = load_yolo()
    tracked_objects = []
    cap = cv2.VideoCapture(video_path)
    target_fps = 30
    frame_delay = int(1000 / target_fps)

    if not cap.isOpened():
        print("无法打开视频")
        return

    # 获取视频的原始宽度和高度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"原始视频分辨率: {width}x{height}")

    # 设置处理后的分辨率
    target_width, target_height = 640, 480

    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out_1 = cv2.VideoWriter(output_path, fourcc, target_fps, (target_width, target_height))

    if not out_1.isOpened():
        print("无法创建视频写入对象")
        cap.release()
        return

    window_name = "videoP"
    #cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    next_id = 0

    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法获取帧，视频结束")
                break

            # 调整帧大小
            frame = cv2.resize(frame, (target_width, target_height))
            height, width, channels = frame.shape

            # YOLO 检测
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5 and class_id == 0:  # 只检测 person
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
            font_path = "simhei.ttf"
            font = ImageFont.truetype(font_path, 20)
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    aspect_ratio = w / h
                    max_h = max([box[3] for box in boxes] or [h])
                    relative_size = h / max_h
                    distance_category = "近" if relative_size > 0.7 else "远"
                    height_category = "高" if h > 100 else "矮"
                    body_type = "胖" if aspect_ratio > 0.85 else "瘦"
                    label = f"Person ({distance_category}, {height_category}, {body_type})"

                    # 使用 PIL 绘制中文标签
                    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_img)
                    draw.text((x, y - 25), label, font=font, fill=(0, 0, 255))
                    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

                    color = (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                    # 跟踪逻辑
                    if classes[class_ids[i]] == "person":
                        center = (int(x + w / 2), int(y + h / 2))
                        min_dist = 50
                        matched_obj = None
                        for obj in tracked_objects:
                            last_pos = obj['trajectory'][-1]
                            distance = np.sqrt((center[0] - last_pos[0]) ** 2 + (center[1] - last_pos[1]) ** 2)
                            if distance < min_dist:
                                min_dist = distance
                                matched_obj = obj
                        if matched_obj:
                            matched_obj['trajectory'].append(center)
                            if len(matched_obj['trajectory']) > 50:
                                matched_obj['trajectory'].pop(0)
                        else:
                            tracked_objects.append({
                                'id': next_id,
                                'color': tuple(np.random.randint(0, 255, 3).tolist()),
                                'trajectory': [center]
                            })
                            next_id += 1

            # 绘制跟踪轨迹
            for obj in tracked_objects:
                for point in obj['trajectory']:
                    cv2.circle(frame, point, 2, obj['color'], -1)

            # 写入帧到输出视频
            out_1.write(frame)
            frame_count += 1
            print(f"已写入帧: {frame_count}")

            # 显示帧
            #cv2.imshow(window_name, frame)

            # 按 'q' 退出
            #if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                #break

    finally:
        print(f"总共写入 {frame_count} 帧")
        cap.release()
        out_1.release()
        #cv2.destroyAllWindows()

        # 验证输出文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"视频已保存至: {output_path}")
        else:
            print("视频文件未正确生成或为空")


    net, classes, colors, output_layers = load_yolo()
    tracked_objects = []
    cap = cv2.VideoCapture(video_path)
    target_fps = 30
    frame_delay = int(1000 / target_fps)

    if not cap.isOpened():
        print("无法打开视频")
        return

    # 获取视频的原始宽度和高度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"原始视频分辨率: {width}x{height}")

    # 设置处理后的分辨率
    target_width, target_height = 640, 480

    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out_1 = cv2.VideoWriter(output_path, fourcc, target_fps, (target_width, target_height))

    if not out_1.isOpened():
        print("无法创建视频写入对象")
        cap.release()
        return

    window_name = "1111"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    next_id = 0

    try:
        frame_count = 0
        start_time = time.time()  # 记录开始时间
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 获取总帧数

        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法获取帧，视频结束")
                break

            frame_start_time = time.time()  # 记录当前帧的开始时间

            # 调整帧大小
            frame = cv2.resize(frame, (target_width, target_height))
            height, width, channels = frame.shape

            # YOLO 检测
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5 and class_id == 0:  # 只检测 person
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
            font_path = "simhei.ttf"
            font = ImageFont.truetype(font_path, 20)
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    aspect_ratio = w / h
                    max_h = max([box[3] for box in boxes] or [h])
                    relative_size = h / max_h
                    distance_category = "近" if relative_size > 0.7 else "远"
                    height_category = "高" if h > 100 else "矮"
                    body_type = "胖" if aspect_ratio > 0.85 else "瘦"
                    label = f"Person ({distance_category}, {height_category}, {body_type})"

                    # 使用 PIL 绘制中文标签
                    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_img)
                    draw.text((x, y - 25), label, font=font, fill=(0, 0, 255))
                    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

                    color = (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                    # 跟踪逻辑
                    if classes[class_ids[i]] == "person":
                        center = (int(x + w / 2), int(y + h / 2))
                        min_dist = 50
                        matched_obj = None
                        for obj in tracked_objects:
                            last_pos = obj['trajectory'][-1]
                            distance = np.sqrt((center[0] - last_pos[0]) ** 2 + (center[1] - last_pos[1]) ** 2)
                            if distance < min_dist:
                                min_dist = distance
                                matched_obj = obj
                        if matched_obj:
                            matched_obj['trajectory'].append(center)
                            if len(matched_obj['trajectory']) > 50:
                                matched_obj['trajectory'].pop(0)
                        else:
                            tracked_objects.append({
                                'id': next_id,
                                'color': tuple(np.random.randint(0, 255, 3).tolist()),
                                'trajectory': [center]
                            })
                            next_id += 1

            # 绘制跟踪轨迹
            for obj in tracked_objects:
                for point in obj['trajectory']:
                    cv2.circle(frame, point, 2, obj['color'], -1)

            # 计算当前帧的处理时间
            frame_end_time = time.time()
            frame_processing_time = frame_end_time - frame_start_time

            # 计算总处理时间
            total_processing_time = frame_end_time - start_time

            # 计算每帧的平均处理时间
            average_frame_processing_time = total_processing_time / (frame_count + 1)

            # 计算剩余帧数
            remaining_frames = total_frames - (frame_count + 1)

            # 计算剩余时间
            remaining_time = remaining_frames * average_frame_processing_time

            # 格式化时间
            total_time_str = time.strftime('%H:%M:%S', time.gmtime(total_processing_time))
            remaining_time_str = time.strftime('%H:%M:%S', time.gmtime(remaining_time))

            # 在帧上绘制处理时间和剩余时间
            cv2.putText(frame, f"total_time: {total_time_str}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"left_time: {remaining_time_str}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 写入帧到输出视频
            out_1.write(frame)
            frame_count += 1
            print(f"已写入帧: {frame_count}")

            # 显示帧
            cv2.imshow(window_name, frame)

            # 按 'q' 退出
            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break

    finally:
        print(f"总共写入 {frame_count} 帧")
        cap.release()
        out_1.release()
        cv2.destroyAllWindows()

        # 验证输出文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"视频已保存至: {output_path}")
        else:
            print("视频文件未正确生成或为空")
