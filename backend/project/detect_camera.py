import cv2
import numpy as np


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

def camera_detect():
    # 打开摄像头并使用YOLO模型进行实时目标检测，检测结果在窗口中显示
    net, classes, colors, output_layers = load_yolo()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    target_fps = 60
    frame_delay = int(1000 / target_fps)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    window_name = "摄像头画面"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("无法获取帧")
                break

            frame = cv2.resize(frame, (640, 480))
            height, width, channels = frame.shape

            # 将图像输入YOLO模型进行处理，并获取检测结果
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # 解析检测结果，过滤掉置信度低于阈值的检测框，并进行非极大值抑制以去除重复框
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5 and class_id == 0:
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

            # 在图像上绘制检测框和类别标签，并显示图像
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            cv2.imshow(window_name, frame)

            # 按'q'键退出程序
            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break
    finally:
        # 释放摄像头资源并关闭所有OpenCV窗口
        cap.release()
        cv2.destroyAllWindows()




    # 加载YOLO模型及配置文件，读取COCO数据集中的类别名称，并初始化颜色和输出层信息
    net, classes, colors, output_layers = load_yolo()

    # 读取视频并调整大小
    cap = cv2.VideoCapture(video_path)
    target_fps = 60
    frame_delay = int(1000 / target_fps)

    if not cap.isOpened():
        print("无法打开视频")
        return

    # 获取视频的原始宽高和帧率
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 设置视频写入器，使用 mp4v 编码格式
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用mp4v编码器，兼容.mp4文件
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))


    window_name = "dected video"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("无法获取帧")
                break

            frame = cv2.resize(frame, (640, 480))
            height, width, channels = frame.shape

            # 将图像输入YOLO模型进行处理，并获取检测结果
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # 解析检测结果，过滤掉置信度低于阈值的检测框，并进行非极大值抑制以去除重复框
            class_ids = []
            confidences = []
            boxes = []
            for layer_output in outs:
                for detection in layer_output:
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

            # 在图像上绘制检测框和类别标签，并显示图像
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[class_ids[i]]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 写入视频文件
            out.write(frame)
            cv2.imshow(window_name, frame)
            # 按'q'键退出程序
            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break
    finally:
        # 确保 `out` 是 `cv2.VideoWriter` 对象
        if isinstance(out, cv2.VideoWriter):
            out.release()  # 释放视频写入器资源
        cap.release()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    camera_detect()
