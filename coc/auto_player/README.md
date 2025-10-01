# COC双模式自动化系统

基于YOLO目标检测和Feature-Driven架构的COC自动化系统，支持主村庄(Home Village)和建筑工人基地(Builder Base)双模式。

## 🏗️ 项目结构

```
auto_player/
├── main.py                    # 🚀 程序入口
├── gui_main.py                # 🖥️ GUI界面程序
├── README.md                  # 📖 项目文档
├── __init__.py                # 模块导入
├── core/                      # 🔧 核心业务逻辑
│   ├── __init__.py
│   ├── controller.py          # 主控制器
│   ├── mode_manager.py        # 🎮 模式管理器 (Home Village / Builder Base)
│   ├── state_machine.py       # 状态机和基类
│   ├── ui_manager.py          # UI管理器
│   └── states/               # 状态处理器 (按功能组织)
│       ├── __init__.py
│       ├── home_village/      # 🏠 主村庄状态处理器
│       │   ├── __init__.py
│       │   ├── village.py          # 主村庄村庄状态
│       │   ├── finding_opponent.py # 主村庄寻找对手状态
│       │   └── attacking.py        # 主村庄攻击状态
│       └── builder_base/      # 🏗️ 建筑工人基地状态处理器
│           ├── __init__.py
│           ├── village.py          # 建筑工人基地村庄状态
│           ├── finding_opponent.py # 建筑工人基地寻找对手状态
│           ├── versus_battle.py    # 建筑工人基地VS对战状态
│           └── auto_battle/        # 🎯 自动战斗功能状态集
│               ├── __init__.py
│               ├── state1_village.py      # State 1: 村庄界面
│               ├── state2_attack_menu.py  # State 2: 攻击菜单
│               ├── state3_battle_scene.py # State 3: 战斗场景
│               ├── state4_surrender_menu.py # State 4: 投降菜单
│               ├── state5_confirm_okay.py # State 5: 确认Okay
│               └── state6_return_home.py  # State 6: 返回主页
├── features/                  # 🌟 功能策略系统 (新架构)
│   ├── __init__.py
│   ├── base.py               # 策略基类和注册表
│   ├── home_village_features.py    # 🏠 主村庄功能策略
│   └── builder_base_features.py    # 🏗️ 建筑工人基地功能策略
├── config/                   # ⚙️ 配置文件 (按功能组织)
│   ├── README.md              # 配置说明文档
│   ├── main_config.yaml       # 🌍 全局配置
│   ├── ui_elements.yaml       # 🎨 UI元素通用配置
│   ├── home_village/          # 🏠 主村庄配置
│   │   ├── village_config.yaml    # 主村庄基础配置
│   │   └── states/                 # 主村庄状态配置
│   │       ├── village.yaml        # 村庄状态配置
│   │       └── attacking.yaml      # 攻击状态配置
│   └── builder_base/          # 🏗️ 建筑工人基地配置  
│       ├── village_config.yaml    # 建筑工人基地基础配置
│       ├── states/                 # 建筑工人基地基础状态配置
│       │   ├── village.yaml            # 村庄状态配置
│       │   ├── versus_battle.yaml      # VS对战状态配置
│       │   └── finding_opponent.yaml   # 寻找对手状态配置
│       └── auto_battle/            # 🎯 自动战斗功能配置
│           ├── state1_village.yaml      # State 1: 村庄界面配置
│           ├── state2_attack_menu.yaml  # State 2: 攻击菜单配置
│           ├── state3_battle_scene.yaml # State 3: 战斗场景配置
│           ├── state4_surrender_menu.yaml # State 4: 投降菜单配置
│           ├── state5_confirm_okay.yaml # State 5: 确认Okay配置
│           └── state6_return_home.yaml  # State 6: 返回主页配置
├── utils/                    # 🛠️ 工具函数
│   ├── __init__.py
│   └── helpers.py            # 通用工具函数
└── tests/                    # 🧪 测试文件
    └── __init__.py
```

## 🚀 快速开始

### 1. GUI界面 (推荐)
```bash
cd auto_player
python gui_main.py
```

### 2. 命令行使用
```bash
python main.py --model-path "你的模型路径.pt" --window "BlueStacks 5"
```

### 3. 测试模式（只检测不点击）
```bash
python main.py --dry-run
```

## 🎮 双模式架构

### Feature-Driven 设计
系统采用全新的**Feature-Driven**架构，替代了旧的Task-Driven设计：

**🏠 主村庄 (Home Village) 功能：**
- ✅ 收集资源 (金币、圣水、暗黑重油)
- ✅ 自动攻击 (找对手→攻击→返回)
- ✅ 部落都城 (可选)
- ✅ 训练部队 (可选) 
- ✅ 升级建筑 (可选)

**🏗️ 建筑工人基地 (Builder Base) 功能：**
- ✅ 收集资源 (金币、圣水)
- ✅ 自动攻击 (通过find_now按钮)
- ✅ 升级建筑 (可选)
- ✅ **自动战斗功能** (完整的6状态循环)
  - State 1: 村庄界面 → 寻找Attack按钮
  - State 2: 攻击菜单 → 点击Find Now开始匹配
  - State 3: 战斗场景 → 智能部署兵力直到可投降
  - State 4: 投降菜单 → 点击Surrender结束战斗
  - State 5: 确认对话 → 点击Okay确认操作
  - State 6: 返回主页 → 点击Return Home完成循环

### 智能模式检测
- 🔍 **自动识别**：系统会根据UI元素自动判断当前模式
- 🎯 **精确切换**：检测到`find_now`按钮 → Builder Base模式
- 🏠 **默认模式**：检测到`clan_capital_button`等 → Home Village模式

## 🎯 按功能组织的架构设计

### 核心设计原则
系统采用全新的**按功能组织**架构设计，每个想要实现的功能都在各自的文件夹下单独创建文件夹：

**🗂️ 功能文件夹结构：**
```
builder_base/
├── states/                 # 基础状态（通用）
├── auto_battle/            # 🎯 自动战斗功能
├── auto_upgrade/           # 🔧 自动升级功能 (未来)
├── resource_management/    # 💰 资源管理功能 (未来)
└── clan_games/            # 🏆 部落竞赛功能 (未来)
```

### 功能状态组织
每个功能包含该功能所需的所有状态：

**以auto_battle为例：**
- **State 1** - 村庄界面状态：识别村庄环境，寻找Attack按钮
- **State 2** - 攻击菜单状态：处理Find Now按钮，开始匹配
- **State 3** - 战斗场景状态：智能部署兵力，监控投降条件
- **State 4** - 投降菜单状态：处理投降按钮点击
- **State 5** - 确认对话状态：处理确认对话框
- **State 6** - 返回主页状态：完成循环返回村庄

### 架构优势

**1. 🎯 功能隔离**
- 每个功能的状态完全独立，互不干扰
- 新功能开发不会影响现有功能
- 功能可以独立启用/禁用

**2. 🔧 易于扩展**
- 添加新功能：创建新的功能文件夹
- 添加新状态：在功能文件夹内添加状态文件
- 配置和代码结构完全对应

**3. 📁 清晰管理**
- 功能相关的所有文件集中管理
- 避免不同功能间的状态混淆
- 便于团队协作开发

**4. 🎮 灵活配置**
- 每个功能有独立的配置文件集
- 支持功能级别的参数调优
- 配置文件结构与代码结构一致

## ⚙️ 配置说明

### 模型要求
你的YOLO模型需要能识别以下类别：

**核心UI元素：**
- `attack` / `attack_button` - 攻击按钮
- `find_now` - Find Now按钮（Builder Base特有）
- `clan_capital_button` - 部落都城按钮（Home Village特有）

**资源收集：**
- `gold_collector` / `bb_gold_collector` - 金币收集器
- `elixir_collector` / `bb_elixir_collector` - 圣水收集器  
- `dark_elixir_collector` - 暗黑重油收集器（仅Home Village）

**其他功能：**
- `barracks_button` - 兵营按钮
- `upgrade_available` / `bb_upgrade_available` - 升级提示
- `army_full_indicator` - 军队准备就绪指示器
- `surrender_button` - 投降按钮（攻击状态）

### 配置文件系统
采用**按模式分离**的配置系统，完美匹配新的Feature-Driven架构：

**🏠 主村庄配置** (`home_village/village_config.yaml`)：
- 5个功能的独立开关配置
- 主村庄特有UI元素识别
- 暗黑重油等专属资源配置

**🏗️ 建筑工人基地配置** (`builder_base/village_config.yaml`)：
- 3个功能的独立开关配置  
- find_now按钮位置计算
- 简化的资源收集配置

**🔄 通用状态配置** (`states/`)：
- `finding_config.yaml` - 寻找对手状态
- `attacking_config.yaml` - 攻击状态

**🌍 全局配置**：
- `main_config.yaml` - 系统级设置
- `ui_elements.yaml` - UI元素通用属性

**优势：**
- 🎮 **模式分离**：每个游戏模式有独立的配置空间
- 🎯 **功能导向**：基于Feature-Driven设计的配置结构
- 🔒 **降低风险**：模式间配置完全隔离
- 📁 **清晰结构**：配置文件结构与代码结构一致
- 🔄 **易于维护**：详细的配置说明文档

## 🎮 工作流程

### 自动化流程
1. **模式检测** → 自动识别当前是Home Village还是Builder Base
2. **功能执行** → 按优先级执行启用的功能：
   - 收集资源 (优先级最高)
   - 训练部队 / 升级建筑
   - 攻击循环
3. **状态转换** → 攻击功能触发状态切换：村庄→寻找对手→攻击→返回村庄
4. **循环继续** → 返回村庄后重新开始功能检查

### 双模式差异
**🏠 Home Village:**
- 更多功能选项 (5种功能)
- 支持暗黑重油收集
- 包含部落都城功能

**🏗️ Builder Base:**  
- 功能相对简单 (3种功能)
- 通过`find_now`按钮进行攻击
- 专注于基础的收集和攻击

## 🔧 扩展开发

### 添加新功能策略
系统采用策略模式，添加新功能非常简单：

**步骤1：创建功能策略类**
```python
# features/home_village_features.py 或 builder_base_features.py
from .base import FeatureStrategy, FeatureType, GameMode

class NewFeatureStrategy(FeatureStrategy):
    def __init__(self):
        super().__init__(FeatureType.NEW_FEATURE, GameMode.HOME_VILLAGE)
        self.description = "新功能描述"
        self.cooldown_seconds = 10
        
    def can_execute(self, detections, config):
        # 检查是否可以执行
        return self.is_enabled(config) and self.has_required_ui(detections)
        
    def execute(self, detections, window_info):
        # 执行功能逻辑
        print("执行新功能...")
        return None
```

**步骤2：注册功能策略**
```python
# 在对应的register_xxx_features()函数中添加
feature_registry.register(NewFeatureStrategy())
```

**步骤3：添加功能类型**
```python
# features/FeatureHandler.py 中的FeatureType枚举
class FeatureType(Enum):
    # 现有功能...
    NEW_FEATURE = "new_feature"  # 添加新类型
```

### 添加新状态处理器

**为特定模式添加状态处理器：**
```python
# core/states/home_village/custom.py
from ....features.base import GameMode
from ...state_machine import StateHandler, GameState
from ...mode_manager import mode_manager

class HomeVillageCustomHandler(StateHandler):
    def __init__(self):
        super().__init__(GameState.CUSTOM)
    
    def can_handle(self, detections):
        # 检查是否为主村庄环境
        clan_capital = [d for d in detections if d.class_name == "clan_capital_button"]
        return len(clan_capital) > 0
        
    def execute(self, detections, window_info):
        mode_manager.set_mode(GameMode.HOME_VILLAGE)
        # 执行主村庄特定逻辑
        return None
```

**添加通用状态处理器：**
```python
# core/states/custom.py
from ..state_machine import StateHandler, GameState

class GenericCustomHandler(StateHandler):
    def __init__(self):
        super().__init__(GameState.CUSTOM)
    
    def can_handle(self, detections):
        return False
        
    def execute(self, detections, window_info):
        return None
```

### 添加工具函数
在`utils/helpers.py`中添加通用工具函数：
```python
def your_utility_function():
    """你的工具函数"""
    pass
```

### 修改UI配置
现在每个状态都有独立的配置文件，比如修改村庄状态：

**编辑 `config/village_config.yaml`：**
```yaml
# 状态识别标识
indicators:
  required: ["find_now"]
  optional: ["attack"]
  
# 相对位置配置
relative_positions:
  attack_from_find_now: [0, -60]
  
# 时间配置
timing:
  max_duration: 30
  click_delay: 0.1
```

**创建新状态配置：**
```yaml
# config/custom_config.yaml
state_name: "custom_state"
indicators:
  required: ["custom_element"]
relative_positions:
  button_position: [100, 50]
```

## 🐛 调试技巧

1. **查看检测结果**：运行时会显示实时画面和检测框
2. **调整置信度**：修改`ui_config.yaml`中的`confidence_threshold`
3. **状态日志**：控制台会显示状态转换和操作日志
4. **测试模式**：使用`--dry-run`参数测试检测效果

## ⚠️ 注意事项

- 确保游戏窗口可见且未被遮挡
- 建议在1920x1080分辨率下使用
- 第一次使用建议用测试模式验证检测效果
- 游戏更新可能需要重新训练模型或调整配置

## 📝 TODO

### 🎯 短期计划
- [ ] 更新GUI界面支持Feature-Driven配置
- [ ] 完善auto_battle功能的错误恢复机制
- [ ] 添加战斗结果统计和性能监控
- [ ] 创建功能集成测试套件

### 🚀 中期计划
- [ ] 实现auto_upgrade自动升级功能
  - [ ] 建筑扫描状态
  - [ ] 升级优先级算法
  - [ ] 资源需求检查
- [ ] 实现resource_management资源管理功能
  - [ ] 智能资源分配
  - [ ] 资源收集优化
  - [ ] 存储容量监控

### 🌟 长期计划  
- [ ] 多分辨率适配系统
- [ ] Web界面监控面板
- [ ] 添加home_village专属功能
  - [ ] 部落都城自动化
  - [ ] 部落竞赛任务
  - [ ] 捐兵功能
- [ ] AI辅助部署策略
- [ ] 云端配置同步

## 🆕 版本历史

### v2.1.0 - 按功能组织架构 🎯
- ✅ **重构状态架构**：采用按功能组织的设计模式
- ✅ **实现自动战斗功能**：完整的6状态循环系统
  - State 1: 村庄界面 → State 2: 攻击菜单 → State 3: 战斗场景
  - State 4: 投降菜单 → State 5: 确认对话 → State 6: 返回主页
- ✅ **配置系统重构**：功能文件夹对应配置文件夹
- ✅ **状态机扩展**：新增6个专用GameState枚举
- ✅ **模块化设计**：每个功能独立管理所需状态
- ✅ **智能部署策略**：支持多种部署模式和战斗机器优先级

### v2.0.0 - Feature-Driven架构
- ✅ 重构为双模式支持 (Home Village + Builder Base)
- ✅ 采用Feature-Driven替代Task-Driven
- ✅ 实现策略模式，极大提升扩展性
- ✅ 智能模式检测和自动切换
- ✅ 模块化的功能配置系统

### v1.0.0 - 基础版本
- ✅ 基于状态机的Builder Base自动攻击
- ✅ YOLO目标检测集成
- ✅ 基础的UI配置系统