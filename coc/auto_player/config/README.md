# 配置文件说明

## 📁 配置文件结构

```
config/
├── README.md                    # 配置说明文档
├── main_config.yaml             # 🌍 全局配置
├── ui_elements.yaml             # 🎨 UI元素通用配置
├── home_village/                # 🏠 主村庄配置
│   └── village_config.yaml     # 主村庄状态配置
├── builder_base/                # 🏗️ 建筑工人基地配置
│   └── village_config.yaml     # 建筑工人基地状态配置
└── states/                      # 🔄 通用状态配置
    ├── finding_config.yaml      # 寻找对手状态配置
    └── attacking_config.yaml    # 攻击状态配置
```

## ⚙️ 配置文件说明

### 🌍 全局配置 (`main_config.yaml`)
- 模型路径
- 窗口配置
- 全局开关
- 系统级设置

### 🎨 UI元素配置 (`ui_elements.yaml`)
- 通用UI元素属性
- 置信度阈值
- 尺寸限制
- 颜色配置

### 🏠 主村庄配置 (`home_village/village_config.yaml`)
- **功能开关**：5个功能的启用/禁用
  - `hv_collect_resources` - 收集资源
  - `hv_attack` - 自动攻击
  - `hv_clan_capital` - 部落都城
  - `hv_train_troops` - 训练部队
  - `hv_upgrade_buildings` - 升级建筑

- **识别标识**：主村庄特有UI元素
  - `clan_capital_button` - 部落都城按钮
  - `barracks_button` - 兵营按钮

- **资源收集**：支持3种资源类型
  - 金币、圣水、暗黑重油

### 🏗️ 建筑工人基地配置 (`builder_base/village_config.yaml`)
- **功能开关**：3个功能的启用/禁用
  - `bb_collect_resources` - 收集资源
  - `bb_attack` - 自动攻击
  - `bb_upgrade_buildings` - 升级建筑

- **识别标识**：建筑工人基地特有UI元素
  - `find_now` - Find Now按钮（BB特有）

- **位置计算**：通过find_now计算attack位置
  - `attack_from_find_now: [0, -50]`

- **资源收集**：支持2种资源类型
  - 金币、圣水

### 🔄 通用状态配置
- **寻找对手** (`states/finding_config.yaml`)
  - 匹配等待时间
  - 重试机制
  - 超时处理

- **攻击状态** (`states/attacking_config.yaml`)
  - 部队部署策略
  - 投降条件
  - 攻击持续时间

## 🎯 配置优势

### 1. **模式分离**
- 每个游戏模式有独立的配置文件
- 避免配置混乱和冲突
- 便于针对性调优

### 2. **功能导向**
- 基于Feature-Driven架构设计
- 每个功能都有独立的开关和配置
- 支持细粒度控制

### 3. **易于维护**
- 清晰的文件结构
- 详细的注释说明
- 版本化管理友好

### 4. **扩展性强**
- 添加新模式只需新建对应文件夹
- 添加新功能只需修改对应配置
- 不影响现有配置

## 🔧 配置修改示例

### 启用主村庄的部落都城功能：
```yaml
# home_village/village_config.yaml
features:
  hv_clan_capital: true  # 改为true
```

### 调整建筑工人基地攻击按钮位置：
```yaml
# builder_base/village_config.yaml  
relative_positions:
  attack_from_find_now: [0, -60]  # 调整Y偏移
```

### 修改资源收集频率：
```yaml
# home_village/village_config.yaml 或 builder_base/village_config.yaml
resource_collection:
  max_collections_per_cycle: 10  # 增加收集数量
  collection_interval: 0.3       # 减少收集间隔
```

## ⚠️ 注意事项

1. **配置优先级**：功能配置 > 模式配置 > 全局配置
2. **路径引用**：所有路径都使用相对路径
3. **备份建议**：修改前建议备份原始配置
4. **重启生效**：配置修改后需要重启程序才能生效