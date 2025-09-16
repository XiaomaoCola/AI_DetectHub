from ScenePredictor import ScenePredictor

# 创建预测器（会自动加载模型）
predictor = ScenePredictor()

# 预测图片文件
scene, confidence = predictor.predict_single(r"C:\Users\zrs\Pictures\Screenshots\Screenshot 2025-09-12 022023.png")
print(f"当前场景: {scene}, 置信度: {confidence:.2f}")