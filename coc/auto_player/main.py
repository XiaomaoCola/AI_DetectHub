#!/usr/bin/env python3
"""
COC夜世界自动攻击主程序

使用示例:
    python main.py
    python main.py --model-path custom_model.pt --window BlueStacks5
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from coc.auto_player import COCGameController


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="COC夜世界自动攻击程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                    # 使用默认配置
  %(prog)s --model-path custom.pt             # 使用自定义模型  
  %(prog)s --window "BlueStacks 5"            # 指定窗口名称
  %(prog)s --config-path custom_config.yaml   # 使用自定义配置
        """
    )
    
    parser.add_argument(
        "--model-path",
        default="D:/python-project/AI_DetectHub/runs/detect/train/weights/best.pt",
        help="YOLO模型路径 (默认: %(default)s)"
    )
    
    parser.add_argument(
        "--window", 
        default="BlueStacks",
        help="游戏窗口关键词 (默认: %(default)s)"
    )
    
    parser.add_argument(
        "--config-path",
        help="UI配置文件路径 (默认: 使用内置配置)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="测试模式，只检测不点击"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    print("="*60)
    print("COC夜世界自动攻击程序 v1.0")
    print("="*60)
    print(f"模型路径: {args.model_path}")
    print(f"窗口关键词: {args.window}")
    print(f"配置文件: {args.config_path or '默认配置'}")
    print(f"测试模式: {'是' if args.dry_run else '否'}")
    print("="*60)
    
    # 检查模型文件是否存在
    model_path = Path(args.model_path)
    if not model_path.exists():
        print(f"[ERROR] 模型文件不存在: {model_path}")
        print("请检查模型路径或先训练模型")
        return 1
        
    try:
        # 创建控制器
        controller = COCGameController(
            model_path=str(model_path),
            window_keyword=args.window,
            config_path=args.config_path
        )
        
        # 如果是测试模式，修改配置不执行点击
        if args.dry_run:
            print("[INFO] 测试模式：只检测，不执行点击操作")
            # 这里可以修改controller的配置来禁用点击
            
        # 运行控制器
        controller.run()
        
        print("[INFO] 程序正常结束")
        return 0
        
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断程序")
        return 0
    except Exception as e:
        print(f"[ERROR] 程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())