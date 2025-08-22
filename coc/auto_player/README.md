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
│   └── states/               # 状态处理器
│       ├── __init__.py
│       ├── village.py         # 村庄状态 (支持双模式)
│       ├── finding.py         # 寻找对手状态
│       └── attacking.py       # 攻击状态
├── features/                  # 🌟 功能策略系统 (新架构)
│   ├── __init__.py
│   ├── base.py               # 策略基类和注册表
│   ├── home_village_features.py    # 🏠 主村庄功能策略
│   └── builder_base_features.py    # 🏗️ 建筑工人基地功能策略
├── config/                   # ⚙️ 配置文件
│   ├── main_config.yaml       # 全局配置
│   ├── village_config.yaml    # 村庄状态配置
│   ├── finding_config.yaml    # 寻找对手配置
│   ├── attacking_config.yaml  # 攻击状态配置
│   └── ui_elements.yaml      # UI元素通用配置
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

### 智能模式检测
- 🔍 **自动识别**：系统会根据UI元素自动判断当前模式
- 🎯 **精确切换**：检测到`find_now`按钮 → Builder Base模式
- 🏠 **默认模式**：检测到`clan_capital_button`等 → Home Village模式

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
现在使用模块化配置，每个状态都有独立的配置文件：

- **`main_config.yaml`** - 全局设置（模型路径、窗口配置等）
- **`village_config.yaml`** - 村庄状态专用配置  
- **`finding_config.yaml`** - 寻找对手状态配置
- **`attacking_config.yaml`** - 攻击状态配置
- **`ui_elements.yaml`** - UI元素通用属性

**优势：**
- 🎯 **精确修改**：只需编辑相关状态的配置文件
- 🔒 **降低风险**：不会误改其他状态的设置
- 📁 **易于管理**：配置职责清晰分离
- 🔄 **便于更新**：游戏UI更新只需调整对应文件

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
# features/base.py 中的FeatureType枚举
class FeatureType(Enum):
    # 现有功能...
    NEW_FEATURE = "new_feature"  # 添加新类型
```

### 添加新状态处理器
```python
# core/states/custom.py
from ..state_machine import StateHandler, GameState

class CustomHandler(StateHandler):
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
- [ ] 完善Builder Base攻击策略
- [ ] 添加更详细的执行日志

### 🚀 长期计划  
- [ ] 智能部队部署策略
- [ ] 多分辨率适配
- [ ] 战斗结果统计
- [ ] Web界面监控
- [ ] 添加更多功能策略（捐兵、商人购买等）

## 🆕 版本历史

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