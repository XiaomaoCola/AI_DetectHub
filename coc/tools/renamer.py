from pathlib import Path
import os

class Renamer:
    def __init__(self, img_dir, labels_dir=None, prefix="attack", start=1, zfill=0, ext=".png"):
        self.img_dir = Path(img_dir)
        self.labels_dir = Path(labels_dir) if labels_dir else None
        self.prefix = prefix
        self.start = start
        self.zfill = zfill
        self.ext = ext

    def rename(self, dry_run=False):
        files = sorted([f for f in self.img_dir.glob(f"*{self.ext}") if f.is_file()])
        # self.img_dir.glob(f"*{self.ext}")，这边的意思是：glob("*.png") 会在 self.img_dir 目录下找所有扩展名是 .png 的文件。
        # self.img_dir.glob("*.png") → 返回一个 generator（生成器），会逐个产出 .png 文件的 Path 对象。
        # .is_file()的作用：判断一个路径是否是文件。如果路径存在并且是普通文件，返回 True；否则返回 False。
        # sorted(...) → 把这个列表进行排序。 默认是 按文件名（字符串字典序）排序。
        if not files:
            print(f"[WARN] No files found in {self.img_dir}")
            return

        idx = self.start
        for f in files:
            num = str(idx).zfill(self.zfill) if self.zfill > 0 else str(idx)
            new_img = f.with_name(f"{self.prefix}_{num}{self.ext}")

            old_lbl, new_lbl = None, None
            if self.labels_dir:
                old_lbl = self.labels_dir / f"{f.stem}.txt"
                new_lbl = self.labels_dir / f"{self.prefix}_{num}.txt"

            print(f"IMG: {f.name} -> {new_img.name}")
            if old_lbl and old_lbl.exists():
                print(f"LBL: {old_lbl.name} -> {new_lbl.name}")

            if not dry_run:
                f.rename(new_img)
                if old_lbl and old_lbl.exists():
                    old_lbl.rename(new_lbl)

            idx += 1

        print("[OK] Rename finished.")

# 使用示例
if __name__ == "__main__":
    renamer = Renamer(
        img_dir=r"C:\Users\zrs\Pictures\Screenshots\state5_return_home",
        # 要改的图片集的文件路径。
        prefix="state5_return_home",
        # 文件名前缀，比如第一个图片，zfill为3，文件名就会变成attack_train_001。
        start=1,
        # 编号从1开始。
        zfill=3
        # zfill表示扩展到3位数，比如数字1，用完zfill会变成001。
    )
    renamer.rename(dry_run=False)
    # 用dry_run=True 先测试，也就是说只打印，不执行。
