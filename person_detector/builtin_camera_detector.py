from ultralytics import YOLO
import cv2

# 1. 加载YOLOv8的预训练模型（nano版本体积小速度快，也可以用 yolov8s.pt/yolov8m.pt）
model = YOLO('yolov8m.pt')

# 2. 检测图片中的所有目标
results = model(0, conf=0.7, stream=True)
# 这边的0的意思是第一个摄像头，我现在在mac上测试了，内置摄像头的调用是没问题的。


# 3. 只保留“person”类别，并计数
for result in results:
    boxes = result.boxes
    num_person = 0
    for box in boxes:
        print(box)
        cls_id = int(box.cls[0])
        if model.names[cls_id] == 'person':
            num_person += 1
    print(f"本图片检测到 {num_person} 个 'person'（人）")


    # 获取当前帧带框画面
    frame = result.plot()

    # 在画面左上角加人数统计
    cv2.putText(frame, f'Person: {num_person}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 实时显示窗口
    cv2.imshow('YOLOv8 Camera Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()