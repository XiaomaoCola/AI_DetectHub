from ClickTracker import BlueStacksClickCalibrator

def get_specific_region():
    """
    获取BlueStacks窗口中指定区域的相对坐标
    标准坐标左上角为（0，0.75），右下角为（0.15，1）的区域
    """
    calibrator = BlueStacksClickCalibrator()
    result = calibrator.find_bluestacks_window()
    
    if not result[0]:  # 如果没找到窗口
        print("未找到BlueStacks窗口")
        return None
    
    found, title, rect, debug_info = result
    client_left, client_top, client_right, client_bottom = rect
    
    # 计算窗口大小
    window_width = client_right - client_left
    window_height = client_bottom - client_top
    
    # 根据标准化坐标计算具体区域
    # 左上角：(0, 0.75) -> 相对坐标
    region_left = int(0 * window_width)
    region_top = int(0.75 * window_height)
    
    # 右下角：(0.15, 1) -> 相对坐标
    region_right = int(0.15 * window_width)
    region_bottom = int(1.0 * window_height)
    
    # 返回区域信息
    region_info = {
        'window_title': title,
        'window_rect': rect,
        'window_size': (window_width, window_height),
        'region_relative': (region_left, region_top, region_right, region_bottom),
        'region_absolute': (
            client_left + region_left,
            client_top + region_top,
            client_left + region_right,
            client_top + region_bottom
        )
    }
    
    return region_info

def main():
    region = get_specific_region()
    
    if region:
        print(f"窗口标题: {region['window_title']}")
        print(f"窗口大小: {region['window_size']}")
        print(f"目标区域相对坐标: {region['region_relative']}")
        print(f"目标区域绝对坐标: {region['region_absolute']}")
        
        # 计算区域大小
        rel_left, rel_top, rel_right, rel_bottom = region['region_relative']
        region_width = rel_right - rel_left
        region_height = rel_bottom - rel_top
        print(f"区域大小: {region_width} x {region_height}")
    else:
        print("获取区域失败")

if __name__ == "__main__":
    main()