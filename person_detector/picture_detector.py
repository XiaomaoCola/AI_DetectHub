from ultralytics import YOLO

# 1. 加载YOLOv8的预训练模型（nano版本体积小速度快，也可以用 yolov8s.pt/yolov8m.pt）
model = YOLO('yolov8l.pt')

# 2. 检测图片中的所有目标
results = model('/Users/a111/Desktop/testing.png', conf=0.7)

# 3. 只保留“person”类别，并计数
for result in results:
    boxes = result.boxes
    num_person = 0
    for box in boxes:
        cls_id = int(box.cls[0])
        if model.names[cls_id] == 'person':
            num_person += 1
    print(f"本图片检测到 {num_person} 个 'person'（人）")

# 4. 显示检测结果图片（带框）
for r in results:
    r.show()