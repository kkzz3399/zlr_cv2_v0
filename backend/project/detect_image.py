import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

def picture_detect(image_path):
    # 使用YOLO模型检测单张图像中的目标，并在图像上绘制检测结果
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # 将图像转换为模型输入格式的blob
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    # 设置模型输入并获取输出层结果
    net.setInput(blob)
    output_layers = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers)

    # 解析模型输出，提取检测框、置信度和类别ID
    # 过滤掉置信度低于0.5且类别不是人的检测结果
    boxes = []
    confidences = []
    class_ids = []
    for output in layerOutputs:
        for detection in output:
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

    # 使用非极大值抑制去除重复的检测框
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    font_path = "simhei.ttf"
    font = ImageFont.truetype(font_path, 20)

    # 在图像上绘制检测到的人的检测框和置信度标签
    for i in indexes.flatten():
        x, y, w, h = boxes[i]
        label = f"Person: {confidences[i]:.2f}"

        aspect_ratio = w / h
        max_h = max([box[3] for box in boxes])
        relative_size = h / max_h
        distance_category = "近" if relative_size > 0.7 else "远"
        height_category = "高" if h > 300 else "矮"
        body_type = "胖" if aspect_ratio > 0.85 else "瘦"
        label = f"Person ({distance_category}, {height_category}, {body_type})"

        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        draw.text((x, y - 25), label, font=font, fill=(0, 0, 255))
        image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        color = (0, 0, 255)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 显示结果图像，等待按键按下后关闭窗口
    #cv2.imshow("Image", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    output_path = image_path.replace(".", "_processed.")
    cv2.imwrite(output_path, image)
    return output_path


