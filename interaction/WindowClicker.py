"""
点击器
输入标准坐标，自动转换并点击区域中心点附近。


调用的话很简单，只需要如下三行代码：
from clicker import WindowClicker
clicker = WindowClicker()
clicker.click_button("BB_find_now")
"""

import time
import win32gui
import pyautogui
import yaml
import random
from typing import Tuple, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yolo_detect_and_judge.RegionCalculator import RegionCalculator


class WindowClicker:
    """窗口点击器类"""

    def __init__(self, window_keyword: str = "BlueStacks"):
        """
        初始化点击器

        Args:
            window_keyword: 目标窗口关键词，默认为BlueStacks
        """
        self.window_keyword = window_keyword
        self.region_calculator = RegionCalculator(window_keyword)

        # pyautogui设置
        pyautogui.FAILSAFE = True  # 移动鼠标到左上角可以停止
        pyautogui.PAUSE = 0.1     # 每次操作间隔

    def bring_window_to_front(self) -> bool:
        """
        将目标窗口置顶

        Returns:
            bool: 是否成功置顶窗口
        """
        try:
            found, title, rect = self.region_calculator.find_bluestacks_window()
            if not found:
                print(f"[ERROR] 未找到包含 '{self.window_keyword}' 的窗口")
                return False

            # 获取窗口句柄
            def enum_handler(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title == title:
                        # 置顶窗口
                        win32gui.SetForegroundWindow(hwnd)
                        win32gui.BringWindowToTop(hwnd)
                        print(f"[INFO] 窗口已置顶: {title}")
                        return False  # 停止枚举
                return True

            win32gui.EnumWindows(enum_handler, None)
            time.sleep(0.5)  # 等待窗口置顶
            return True

        except Exception as e:
            print(f"[ERROR] 置顶窗口失败: {e}")
            return False

    def click_region(self, norm_left: float, norm_top: float,
                    norm_right: float, norm_bottom: float,
                    bring_to_front: bool = True, offset_range: int = 0) -> bool:
        """
        点击指定标准坐标区域的中心点，可带随机偏移

        Args:
            norm_left: 左上角X坐标 (0-1范围)
            norm_top: 左上角Y坐标 (0-1范围)
            norm_right: 右下角X坐标 (0-1范围)
            norm_bottom: 右下角Y坐标 (0-1范围)
            bring_to_front: 是否先置顶窗口
            offset_range: 随机偏移范围（像素），0表示无偏移

        Returns:
            bool: 是否成功点击
        """
        try:
            # 置顶窗口
            if bring_to_front:
                if not self.bring_window_to_front():
                    return False

            # 获取区域坐标
            coords = self.region_calculator.get_region_coords(
                norm_left, norm_top, norm_right, norm_bottom
            )

            if coords is None:
                print("[ERROR] 无法获取区域坐标")
                return False

            region_left, region_top, region_right, region_bottom = coords

            # 计算中心点
            center_x = (region_left + region_right) // 2
            center_y = (region_top + region_bottom) // 2

            # 应用随机偏移（如果指定）
            final_x = center_x
            final_y = center_y
            offset_x = 0
            offset_y = 0

            if offset_range > 0:
                offset_x = random.randint(-offset_range, offset_range)
                offset_y = random.randint(-offset_range, offset_range)

                # 应用偏移
                final_x = center_x + offset_x
                final_y = center_y + offset_y

                # 确保偏移后的坐标仍在区域内
                final_x = max(region_left + 5, min(final_x, region_right - 5))
                final_y = max(region_top + 5, min(final_y, region_bottom - 5))

            # 获取窗口屏幕坐标
            found, title, window_rect = self.region_calculator.find_bluestacks_window()
            if not found:
                return False

            window_left, window_top, _, _ = window_rect

            # 计算屏幕绝对坐标
            screen_x = window_left + final_x
            screen_y = window_top + final_y

            print(f"[INFO] 点击区域: ({norm_left:.3f}, {norm_top:.3f}) -> ({norm_right:.3f}, {norm_bottom:.3f})")
            print(f"[INFO] 相对坐标: ({region_left}, {region_top}) -> ({region_right}, {region_bottom})")
            if offset_range > 0:
                print(f"[INFO] 中心坐标: ({center_x}, {center_y})")
                print(f"[INFO] 随机偏移: ({offset_x:+d}, {offset_y:+d})")
            print(f"[INFO] 最终点击: ({final_x}, {final_y}) -> 屏幕坐标: ({screen_x}, {screen_y})")

            # 移动鼠标并点击
            pyautogui.moveTo(screen_x, screen_y, duration=0.2)
            pyautogui.click()

            print("[SUCCESS] 点击完成")
            return True

        except Exception as e:
            print(f"[ERROR] 点击失败: {e}")
            return False

    def click_point(self, norm_x: float, norm_y: float,
                   bring_to_front: bool = True) -> bool:
        """
        点击指定标准坐标点

        Args:
            norm_x: X坐标 (0-1范围)
            norm_y: Y坐标 (0-1范围)
            bring_to_front: 是否先置顶窗口

        Returns:
            bool: 是否成功点击
        """
        return self.click_region(norm_x, norm_y, norm_x, norm_y, bring_to_front)

    def get_window_info(self) -> Optional[dict]:
        """
        获取窗口信息

        Returns:
            dict: 窗口信息字典或None
        """
        found, title, rect = self.region_calculator.find_bluestacks_window()
        if found:
            left, top, right, bottom = rect
            return {
                "title": title,
                "rect": rect,
                "width": right - left,
                "height": bottom - top
            }
        return None

    def load_region_config(self, config_file: str) -> Optional[dict]:
        """
        加载区域配置文件

        Args:
            config_file: yaml配置文件路径

        Returns:
            dict: 配置数据或None
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"[ERROR] 加载配置文件失败: {e}")
            return None

    def click_button(self, button_name: str, bring_to_front: bool = True,
                    offset_range: int = 10) -> bool:
        """
        根据按钮名称点击长方形区域，带随机偏移防止游戏检测
        由于默认用的是click_config.yaml里面的rect_region。

        Args:
            button_name: 按钮名称 (如 "BB_attack", "BB_find_now")
            bring_to_front: 是否先置顶窗口
            offset_range: 随机偏移范围（像素），默认10像素

        Returns:
            bool: 是否成功点击
        """
        # 使用本地配置文件
        config_file = os.path.join(os.path.dirname(__file__), "click_config.yaml")
        config = self.load_region_config(config_file)
        if not config:
            return False

        # 查找rect_regions中的按钮
        rect_regions = config.get('rect_regions', {})
        if button_name not in rect_regions:
            print(f"[ERROR] 按钮 '{button_name}' 不存在")
            print(f"[INFO] 可用按钮: {list(rect_regions.keys())}")
            return False

        region = rect_regions[button_name]
        print(f"[INFO] 点击按钮: {button_name} (偏移范围: ±{offset_range}px)")

        return self.click_region(
            norm_left=region['left'],
            norm_top=region['top'],
            norm_right=region['right'],
            norm_bottom=region['bottom'],
            bring_to_front=bring_to_front,
            offset_range=offset_range
        )


def main():
    """示例使用 - 点击Builder Base的Attack按钮"""
    clicker = WindowClicker("BlueStacks")

    # 获取窗口信息
    window_info = clicker.get_window_info()
    if window_info:
        print(f"找到窗口: {window_info['title']}")
        print(f"窗口大小: {window_info['width']} x {window_info['height']}")
        print(f"窗口位置: {window_info['rect']}")
    else:
        print("未找到目标窗口")
        return

    # 示例：点击Builder Base Attack按钮
    # 现在只需要按钮名称，配置都在 click_config.yaml 中
    print("\n3秒后点击Attack按钮...")
    time.sleep(3)

    # 简单调用：只需要按钮名称
    success = clicker.click_button("BB_attack")

    if success:
        print("Attack按钮点击成功！")
    else:
        print("Attack按钮点击失败！")


if __name__ == "__main__":
    main()