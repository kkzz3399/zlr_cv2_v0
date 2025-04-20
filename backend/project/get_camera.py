import cv2
import os
import pandas as pd


def get_connected_cameras():
    """检测所有连接的摄像头并返回ID列表"""
    camera_ids = []
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            cap.release()
            break
        else:
            camera_ids.append(index)
            cap.release()
        index += 1
    return camera_ids
if __name__ == "__main__":
    # 创建保存目录
    save_dir = 'saved_cameras'
    os.makedirs(save_dir, exist_ok=True)

    # 获取摄像头列表
    camera_list = get_connected_cameras()

    # 创建DataFrame并保存Excel
    if camera_list:
        df = pd.DataFrame({
            'id': range(1, len(camera_list) + 1),  # 自增序号
            '摄像头id号': camera_list  # 实际检测到的摄像头ID
        })

        # 保存路径
        file_path = os.path.join(save_dir, 'camera_list.xlsx')
        df.to_excel(file_path, index=False)
        print(f"成功检测到 {len(camera_list)} 个摄像头，信息已保存至：{file_path}")
    else:
        print("未检测到任何摄像头！")