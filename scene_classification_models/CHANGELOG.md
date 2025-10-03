## 2025/10/1
这个模块的改进方向是：

1. 每一个feature都应该对应一个场景识别模组。
2. 或者可以用注册表注册多个模组进入一个feature里面。（比如一个场景识别模组加上一个yolo兵种识别模组。）
3. 得把所有场景识别模组加入枚举类里，便于管理。

## 2025/10/4
已经改好了SceneClassifierTrainer.py。
然后用BBAutoAttack的数据又造了`bb_collect_resources/BBCollectResources_scene_classifier.pt`，
就是暂时凑个数，未来改。 因为现在的目标是把枚举类造出来。

至于注册表为什么不需要，也就是10月1日日记里的任务2，因为注册表是提取枚举类里的个体的对应的东西的，
比如StateHandlerRegistry.py里面其实是为了调用枚举类里个体对应的handler的。