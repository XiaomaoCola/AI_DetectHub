# 模型说明文档  
  
| 模型文件名             | 用途       | 类别数 | Class Name       | 数据来源           |     |
| ----------------- | -------- | --- | ---------------- | -------------- | --- |
| builder_base_1.pt | 主村庄的界面识别 | 2   | attack, find_now | coc_dataset/v3 |     |
| builder_base_2.pt | 战斗中识别    | 4   | 2025/09/11       | coc_dataset/v4 |     |
| home_village_1.pt | 主村庄的界面识别 | 2   | 2025/09/12       | coc_dataset/v2 |     |
  



## 备注  
  
目前只有builder_base_1.pt训练好了，其他的pt都是过来凑数，  
未来训练的时候留个结构规范，然后直接替换掉。  
  
## 文件夹的说明  
  
  - weights/ ： 存放训练好的模型权重  
  - region_configs/ ： 存放对应模型的区域判断配置，也就是识别出来的方框应该落在的区域。