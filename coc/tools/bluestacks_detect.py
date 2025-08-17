import time
import ctypes
from ctypes import wintypes
import re

import cv2
import numpy as np
import pyautogui
from mss import mss
from ultralytics import YOLO

import win32gui
import win32con


class BlueStacksDetector:
    def __init__(self, model_path=None, window_keyword="BlueStacks", conf_thres=0.55, 
                 cls_id=0, do_click=False, show_fps=True):
        # ====== 配置 ======
        self.model_path = model_path or r"D:\python-project\AI_DetectHub\runs\detect\train2\weights\best.pt"
        self.window_keyword = window_keyword
        self.conf_thres = conf_thres
        self.cls_id = cls_id
        self.do_click = do_click
        self.show_fps = show_fps
        
        # 处理高DPI缩放（确保坐标与屏幕一致）
        ctypes.windll.user32.SetProcessDPIAware()
        
        # 初始化
        self.model = None
        self.sct = None

    def find_window_rect(self, keyword: str):
        """
        返回匹配窗口的客户区矩形 (left, top, right, bottom)。找不到返回 None。
        只抓客户区（不含边框标题栏，适合直接截图/点击）。
        """
        target_hwnd = None
        hwnd_list = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and re.search(keyword, title, flags=re.I):
                    hwnd_list.append((hwnd, title))
        win32gui.EnumWindows(enum_handler, None)
        #  win32gui.EnumWindows的作用：把当前系统中所有的“顶层窗口（top-level windows）”全部枚举（列出来）一遍，然后对每一个窗口调用提供的处理函数（callback function）。
        # 如下代码输出的是匹配成功，这是re的一个例子。
        # import re
        #
        # keyword = "bluestacks"
        # title = "BlueStacks App Player"
        #
        # if re.search(keyword, title, flags=re.I):
        #     print("匹配成功！")
        # else:
        #     print("没有匹配到")

        # 优先选活动窗口里的第一个匹配
        if hwnd_list:
            target_hwnd, _ = hwnd_list[0]
        else:
            return None

        # 获取客户区尺寸（相对窗口客户区坐标）
        rect = win32gui.GetClientRect(target_hwnd)  # (0,0,w,h) in client coords
        # 左上角客户区点 -> 屏幕坐标
        pt = win32gui.ClientToScreen(target_hwnd, (0, 0))
        left, top = pt
        right, bottom = left + rect[2], top + rect[3]
        return (left, top, right, bottom), target_hwnd

    def run_detection(self):
        print("[INFO] Loading model...")
        self.model = YOLO(self.model_path)
        self.sct = mss()

        ok = self.find_window_rect(self.window_keyword)
        if not ok:
            print(f"[ERR] 未找到标题包含 '{self.window_keyword}' 的窗口。请先打开 BlueStacks，或修改 window_keyword。")
            return
        (L, T, R, B), hwnd = ok
        W, H = R - L, B - T
        print(f"[INFO] 捕获客户区: ({L},{T})-({R},{B}) size={W}x{H}")

        print("[INFO] 按 ESC 退出。")
        prev = time.time()
        frame_cnt = 0

        while True:
            # 1) 截客户区
            region = {"left": L, "top": T, "width": W, "height": H}
            frame = np.array(self.sct.grab(region))[:, :, :3]  # BGRA -> BGR

            # 2) 推理
            results = self.model.predict(frame, imgsz=640, conf=self.conf_thres, verbose=False)[0]

            det = []
            if results.boxes is not None and len(results.boxes) > 0:
                xyxy = results.boxes.xyxy.cpu().numpy().astype(int)
                cls = results.boxes.cls.cpu().numpy().astype(int)
                conf = results.boxes.conf.cpu().numpy()
                for (x1, y1, x2, y2), c, p in zip(xyxy, cls, conf):
                    if c == self.cls_id:
                        det.append((float(p), x1, y1, x2, y2))

            # 3) 可视化 & 点击
            overlay = frame.copy()
            if det:
                det.sort(key=lambda x: x[0], reverse=True)
                p, x1, y1, x2, y2 = det[0]
                xc, yc = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(overlay, f"attack {p:.2f}", (x1, max(0, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                if self.do_click:
                    # 将客户区坐标转为全局屏幕坐标=客户区左上角偏移
                    screen_x, screen_y = L + xc, T + yc
                    pyautogui.moveTo(screen_x, screen_y, duration=0.05)
                    pyautogui.click()
                    time.sleep(0.15)  # 简单节流

            if self.show_fps:
                frame_cnt += 1
                now = time.time()
                if now - prev >= 1.0:
                    fps = frame_cnt / (now - prev)
                    prev, frame_cnt = now, 0
                else:
                    fps = None
                if fps:
                    cv2.putText(overlay, f"FPS: {fps:.1f}", (8, 22),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow("BlueStacks - Attack detect", overlay)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

            # 若用户切窗口或移动窗口，动态刷新客户区坐标
            ok2 = self.find_window_rect(self.window_keyword)
            if ok2:
                (L, T, R, B), _ = ok2
                W, H = R - L, B - T

        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = BlueStacksDetector()
    detector.run_detection()
