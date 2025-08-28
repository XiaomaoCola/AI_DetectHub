# 配置文件说明

## 📁 配置文件结构（按功能组织）

```
config/
├── README.md                    # 配置说明文档
├── main_config.yaml             # 🌍 全局配置
├── ui_elements.yaml             # 🎨 UI元素通用配置
├── home_village/                # 🏠 主村庄配置
│   ├── village_config.yaml     # 主村庄基础配置
│   └── states/                  # 主村庄状态配置
│       ├── village.yaml         # 村庄状态
│       └── attacking.yaml       # 攻击状态
└── builder_base/                # 🏗️ 建筑工人基地配置
    ├── village_config.yaml     # 建筑工人基地基础配置
    ├── states/                  # 建筑工人基地基础状态配置
    │   ├── village.yaml         # 村庄状态
    │   ├── versus_battle.yaml   # VS对战状态
    │   └── finding_opponent.yaml # 寻找对手状态
    └── auto_battle/             # 🎯 自动战斗功能配置
        ├── state1_village.yaml      # State 1: 村庄界面
        ├── state2_attack_menu.yaml  # State 2: 攻击菜单
        ├── state3_battle_scene.yaml # State 3: 战斗场景
        ├── state4_surrender_menu.yaml # State 4: 投降菜单
        ├── state5_confirm_okay.yaml # State 5: 确认Okay
        └── state6_return_home.yaml  # State 6: 返回主页
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

### 🎯 自动战斗功能配置 (`builder_base/auto_battle/`)

建筑工人基地自动战斗功能包含6个状态的完整战斗循环：

- **State 1** (`state1_village.yaml`) - 村庄界面状态
  - 识别村庄建筑
  - 资源收集配置
  - Attack按钮搜索区域

- **State 2** (`state2_attack_menu.yaml`) - 攻击菜单状态  
  - Find Now按钮检测
  - 部队配置检查
  - 匹配开始等待时间

- **State 3** (`state3_battle_scene.yaml`) - 战斗场景状态
  - 智能部署策略配置
  - 战斗机器部署优先级
  - 投降条件设置

- **State 4** (`state4_surrender_menu.yaml`) - 投降菜单状态
  - 投降按钮搜索区域
  - 点击间隔控制
  - 备用位置配置

- **State 5** (`state5_confirm_okay.yaml`) - 确认Okay状态
  - 对话框检测配置
  - 确认按钮搜索策略
  - 智能点击区域

- **State 6** (`state6_return_home.yaml`) - 返回主页状态
  - 战斗结果收集
  - 返回按钮检测
  - 循环完成验证

## 🎯 配置架构优势

### 1. **按功能组织**
- 每个想做的功能在各自的文件夹下单独创建文件夹
- 功能相关的所有states集中管理
- 避免不同功能间的状态混淆

### 2. **模块化设计**
- 每个功能模块独立配置
- 添加新功能时不影响现有功能
- 便于功能的启用/禁用控制

### 3. **状态细分**
- 复杂功能按状态机划分为多个细分状态
- 每个状态都有专门的配置文件
- 支持精确的状态转换控制

### 4. **扩展性强**
- 添加新功能：在对应模式下创建功能文件夹
- 添加新状态：在功能文件夹下添加状态配置
- 不影响现有配置结构

## 🔧 配置修改示例

### 启用主村庄的部落都城功能：
```yaml
# home_village/village_config.yaml
features:
  hv_clan_capital: true  # 改为true
```

### 调整自动战斗部署策略：
```yaml
# builder_base/auto_battle/state3_battle_scene.yaml
deployment:
  max_troops: 18
  deploy_interval: 0.4      # 更快的部署间隔
  strategy: "aggressive"    # 改为激进策略
```

### 修改投降条件：
```yaml
# builder_base/auto_battle/state3_battle_scene.yaml
surrender_conditions:
  min_troops_deployed: 15   # 增加最小部署兵力
  max_battle_time: 60       # 延长战斗时间
```

### 调整确认按钮搜索区域：
```yaml
# builder_base/auto_battle/state5_confirm_okay.yaml
okay_button_detection:
  min_confidence: 0.8       # 提高置信度要求
  search_areas:
    primary: [0.2, 0.3, 0.8, 0.9]  # 扩大搜索区域
```

## 🆕 添加新功能指南

### 1. 创建功能文件夹
在对应的游戏模式下创建新功能文件夹：
```
builder_base/
└── auto_upgrade/           # 新功能：自动升级
    ├── state1_scan_buildings.yaml
    ├── state2_select_building.yaml
    └── state3_confirm_upgrade.yaml
```

### 2. 定义功能状态
为新功能创建状态配置文件，每个状态包含：
- 状态识别标识
- 操作配置
- 转换条件
- 错误处理

### 3. 功能集成
在对应的core/states目录下创建相应的状态处理器。

## ⚠️ 注意事项

1. **配置优先级**：功能配置 > 模式配置 > 全局配置
2. **路径引用**：所有路径都使用相对路径
3. **备份建议**：修改前建议备份原始配置
4. **重启生效**：配置修改后需要重启程序才能生效
5. **功能隔离**：每个功能的状态应该在独立的文件夹中管理
6. **状态命名**：建议使用有意义的状态名称，如state1_description格式