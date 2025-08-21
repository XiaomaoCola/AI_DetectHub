# COC夜世界自动攻击系统

基于YOLO目标检测和状态机的COC夜世界自动化攻击系统。

## 🏗️ 项目结构

```
auto_player/
├── main.py                  # 🚀 程序入口
├── README.md                # 📖 项目文档
├── __init__.py              # 模块导入
├── core/                    # 🔧 核心业务逻辑
│   ├── __init__.py
│   ├── controller.py        # 主控制器
│   ├── state_machine.py     # 状态机和基类
│   ├── ui_manager.py        # UI管理器
│   └── states/             # 状态处理器
│       ├── __init__.py
│       ├── village.py       # 村庄状态
│       ├── finding.py       # 寻找对手状态
│       └── attacking.py     # 攻击状态
├── config/                 # ⚙️ 配置文件
│   ├── main_config.yaml     # 全局配置
│   ├── village_config.yaml  # 村庄状态配置
│   ├── finding_config.yaml  # 寻找对手配置
│   ├── attacking_config.yaml # 攻击状态配置
│   └── ui_elements.yaml     # UI元素通用配置
├── utils/                  # 🛠️ 工具函数
│   ├── __init__.py
│   └── helpers.py          # 通用工具函数
└── tests/                  # 🧪 测试文件
    └── __init__.py
```

## 🚀 快速开始

### 1. 基本使用
```bash
cd auto_player
python main.py
```

### 2. 自定义参数
```bash
python main.py --model-path "你的模型路径.pt" --window "BlueStacks 5"
```

### 3. 测试模式（只检测不点击）
```bash
python main.py --dry-run
```

## ⚙️ 配置说明

### 模型要求
你的YOLO模型需要能识别以下类别：
- `attack` - 攻击按钮
- `find_now` - Find Now按钮（Builder Base特有）
- `surrender_button` - 投降按钮（可选）
- `empty_space` - 空地/部署区域（可选）

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

1. **村庄状态** → 检测到`find_now`按钮，点击`attack`
2. **寻找对手** → 等待匹配完成，进入攻击界面
3. **攻击状态** → 部署部队，完成后投降
4. **返回村庄** → 点击返回按钮，开始下一轮

## 🔧 扩展开发

### 添加新状态
1. 在`core/states/`目录创建新的处理器类
2. 继承`StateHandler`基类
3. 实现`can_handle()`和`execute()`方法
4. 在`core/controller.py`中注册

### 示例：
```python
# core/states/custom.py
from ..state_machine import StateHandler, GameState

class CustomHandler(StateHandler):
    def __init__(self):
        super().__init__(GameState.CUSTOM)
    
    def can_handle(self, detections):
        # 实现状态判断逻辑
        return False
        
    def execute(self, detections, window_info):
        # 实现状态操作逻辑
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

- [ ] 添加更多状态（投降确认、返回村庄等）
- [ ] 智能部队部署策略
- [ ] 多分辨率适配
- [ ] 战斗结果统计
- [ ] Web界面监控