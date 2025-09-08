"""
这个类的功能是，给出区域的左上角和右下角的标准坐标，
可以返回区域左上角和右上角的相对坐标。
简单说就跟计算器一样，把窗口的长和高取出来跟标准坐标相乘。
"""

import ctypes
import re
import win32gui


class RegionCalculator:
    def __init__(self, window_keyword="BlueStacks"):
        self.window_keyword = window_keyword
        ctypes.windll.user32.SetProcessDPIAware()
    
    def find_bluestacks_window(self):
        """查找BlueStacks窗口"""
        hwnd_list = []
        
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(self.window_keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))
        
        win32gui.EnumWindows(enum_handler, None)
        
        if hwnd_list:
            target_hwnd, title = hwnd_list[0]
            client_rect = win32gui.GetClientRect(target_hwnd)
            client_screen_pos = win32gui.ClientToScreen(target_hwnd, (0, 0))
            client_left, client_top = client_screen_pos
            client_right = client_left + client_rect[2]
            client_bottom = client_top + client_rect[3]
            
            return True, title, (client_left, client_top, client_right, client_bottom)
        else:
            return False, None, None
    
    def get_region_coords(self, norm_left, norm_top, norm_right, norm_bottom):
        """
        根据标准化坐标计算相对坐标
        
        Args:
            norm_left, norm_top: 左上角标准化坐标 (0-1范围)
            norm_right, norm_bottom: 右下角标准化坐标 (0-1范围)
            
        Returns:
            tuple: (region_left, region_top, region_right, region_bottom) 或 None
        """
        found, title, rect = self.find_bluestacks_window()
        
        if not found:
            return None
        
        client_left, client_top, client_right, client_bottom = rect
        window_width = client_right - client_left
        window_height = client_bottom - client_top
        
        region_left = int(norm_left * window_width)
        region_top = int(norm_top * window_height)
        region_right = int(norm_right * window_width)
        region_bottom = int(norm_bottom * window_height)
        
        return (region_left, region_top, region_right, region_bottom)

def main():
    calculator = RegionCalculator()
    # 标准坐标左上角为（0，0.75），右下角为（0.15，1）
    coords = calculator.get_region_coords(0, 0.75, 0.15, 1)
    
    if coords:
        print(f"相对坐标: {coords}")
    else:
        print("获取坐标失败")

if __name__ == "__main__":
    main()