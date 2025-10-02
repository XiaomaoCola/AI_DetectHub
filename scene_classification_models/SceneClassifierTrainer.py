import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional


class SceneClassifierTrainer:
    """COC场景分类器训练类"""
    
    def __init__(self, 
                 data_dir: str = "../scene_classification_dataset",
                 model_save_path: str = "BBAutoAttack_scene_classifier.pt",
                 config_save_path: str = "BBAutoAttack_scene_classifier.json",
                 batch_size: int = 16,
                 img_size: int = 224,
                 learning_rate: float = 0.001):
        """
        初始化训练器
        
        Args:
            data_dir: 数据集目录
            model_save_path: 模型保存路径
            config_save_path: 配置文件保存路径
            batch_size: 批次大小
            img_size: 图像尺寸
            learning_rate: 学习率
        """
        self.data_dir = Path(data_dir)
        self.model_save_path = model_save_path
        self.config_save_path = config_save_path
        self.batch_size = batch_size
        self.img_size = img_size
        self.learning_rate = learning_rate
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[INFO] 使用设备: {self.device}")
        
        # 初始化属性
        self.model = None
        self.train_loader = None
        self.val_loader = None
        self.class_names = []
        self.num_classes = 0
        
        # 训练历史
        self.training_history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
    
    def _get_transforms(self) -> Tuple[transforms.Compose, transforms.Compose]:
        """
        构建两个图像处理的“流水线”：
        - 训练集会做翻转、旋转、变亮等增强操作
        - 验证集只做基础的缩放和归一化

        这些操作会在图片喂给模型之前自动执行（GPT写的，不知道这句话啥意思）
        """
        # transforms.Compose(...) 这个写法是 PyTorch 的图像预处理pipeline的工具。
        # 传进去一个变换列表 [...]，会自动按顺序执行每个变换，
        # 调用 Compose 对象就等于依次执行全部步骤。
        train_transform = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.RandomHorizontalFlip(p=0.3),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        val_transform = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return train_transform, val_transform

    def load_data(self, train_split: float = 0.8) -> bool:
        """
        读取图片数据集，并把它切分为训练集和验证集
        同时设置图像预处理操作（比如缩放、翻转等）
        最后返回两个 DataLoader，供模型训练和评估使用
        
        Args:
            train_split: 训练集比例
            train_split=0.8 表示 80% 的图片用来训练，20% 验证（默认设置）。
            
        Returns:
            bool: 是否成功加载数据
        """
        try:
            train_transform, val_transform = self._get_transforms()
            
            # 加载数据集，这行非常关键：使用 PyTorch 自带的 ImageFolder 类从文件夹读取图片，所以目录结构固定。
            # datasets.ImageFolder(...)，是 PyTorch torchvision 自带的一个工具类，用来从文件夹里加载数据集。
            # transform=train_transform表示：每次从这个数据集中取图片的时候，
            # 都会先执行 train_transform（也就是缩放、翻转、旋转、亮度扰动、归一化等处理），再把处理后的结果交给模型。
            dataset = datasets.ImageFolder(str(self.data_dir), transform=train_transform)
            # 关于dataset.classes：ImageFolder 会自动记录下有哪些类别，并保存在 .classes 属性里。
            # 比如['stage1_village', 'stage2_attack_menu', 'stage3_battle_scene']。
            self.class_names = dataset.classes
            self.num_classes = len(self.class_names)
            
            print(f"[INFO] 找到 {self.num_classes} 个类别: {self.class_names}")
            print(f"[INFO] 总共 {len(dataset)} 张图片")
            
            # 数据分割
            train_size = int(train_split * len(dataset))
            val_size = len(dataset) - train_size
            # random_split 进行随机划分。
            train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
            
            # 为验证集设置不同的transform。
            # val_dataset 是 Subset，它有个 .dataset 属性，指向原始 ImageFolder 对象。
            val_dataset.dataset.transform = val_transform
            
            # 创建数据加载器
            self.train_loader = DataLoader(
                train_dataset, 
                batch_size=self.batch_size, 
                shuffle=True, 
                num_workers=2,
                pin_memory=True if self.device.type == 'cuda' else False
            )
            
            self.val_loader = DataLoader(
                val_dataset, 
                batch_size=self.batch_size, 
                shuffle=False, 
                num_workers=2,
                pin_memory=True if self.device.type == 'cuda' else False
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 数据加载失败: {e}")
            return False
    
    def build_model(self, model_name: str = "resnet18", pretrained: bool = True) -> None:
        """
        构建模型
        
        Args:
            model_name: 模型名称
            pretrained: 是否使用预训练权重
        """
        if model_name == "resnet18":
            self.model = models.resnet18(pretrained=pretrained)
            self.model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(self.model.fc.in_features, self.num_classes)
            )
        elif model_name == "resnet50":
            self.model = models.resnet50(pretrained=pretrained)
            self.model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(self.model.fc.in_features, self.num_classes)
            )
        else:
            raise ValueError(f"不支持的模型: {model_name}")
        
        self.model = self.model.to(self.device)
        print(f"[INFO] 模型 {model_name} 已构建完成")
    
    def train_epoch(self, optimizer, criterion, scheduler=None) -> Tuple[float, float]:
        """训练一个epoch"""
        self.model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (imgs, labels) in enumerate(self.train_loader):
            imgs, labels = imgs.to(self.device), labels.to(self.device)
            
            optimizer.zero_grad()
            outputs = self.model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        if scheduler:
            scheduler.step()
        
        avg_loss = train_loss / len(self.train_loader)
        accuracy = 100 * train_correct / train_total
        
        return avg_loss, accuracy
    
    def validate_epoch(self, criterion) -> Tuple[float, float]:
        """验证一个epoch"""
        self.model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for imgs, labels in self.val_loader:
                imgs, labels = imgs.to(self.device), labels.to(self.device)
                
                outputs = self.model(imgs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        avg_loss = val_loss / len(self.val_loader)
        accuracy = 100 * val_correct / val_total
        
        return avg_loss, accuracy
    
    def train(self, epochs: int = 20, save_best_only: bool = True) -> Dict:
        """
        开始训练
        
        Args:
            epochs: 训练轮数
            save_best_only: 是否只保存最佳模型
            
        Returns:
            Dict: 训练历史
        """
        if not self.model:
            raise ValueError("请先调用 build_model() 构建模型")
        
        # 设置优化器和损失函数
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
        
        best_val_acc = 0.0
        
        print(f"[INFO] 开始训练，共 {epochs} 个epoch")
        print("=" * 60)
        
        for epoch in range(epochs):
            # 训练阶段
            train_loss, train_acc = self.train_epoch(optimizer, criterion, scheduler)
            
            # 验证阶段
            val_loss, val_acc = self.validate_epoch(criterion)
            
            # 记录历史
            self.training_history["train_loss"].append(train_loss)
            self.training_history["train_acc"].append(train_acc)
            self.training_history["val_loss"].append(val_loss)
            self.training_history["val_acc"].append(val_acc)
            
            # 输出结果
            print(f"Epoch [{epoch+1}/{epochs}]")
            print(f"  训练: Loss={train_loss:.4f}, Acc={train_acc:.2f}%")
            print(f"  验证: Loss={val_loss:.4f}, Acc={val_acc:.2f}%")
            
            # 保存最佳模型
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                if save_best_only:
                    self.save_model(val_acc, epoch + 1)
                    print(f"  ✅ 保存最佳模型 (验证准确率: {val_acc:.2f}%)")
            
            print("-" * 40)
        
        print("=" * 60)
        print(f"🎉 训练完成！最佳验证准确率: {best_val_acc:.2f}%")
        
        return self.training_history
    
    def save_model(self, val_acc: float, epoch: int) -> None:
        """保存模型和配置"""
        model_data = {
            "model_state": self.model.state_dict(),
            "class_names": self.class_names,
            "num_classes": self.num_classes,
            "val_acc": val_acc,
            "epoch": epoch,
            "img_size": self.img_size,
            "device": str(self.device)
        }
        
        torch.save(model_data, self.model_save_path)
        
        # 保存配置文件
        config = {
            "class_names": self.class_names,
            "num_classes": self.num_classes,
            "img_size": self.img_size,
            "model_path": self.model_save_path,
            "best_val_acc": val_acc,
            "training_epochs": epoch
        }
        
        with open(self.config_save_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 模型已保存: {self.model_save_path}")
        print(f"[INFO] 配置已保存: {self.config_save_path}")
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        加载训练好的模型
        
        Args:
            model_path: 模型路径，如果为None则使用默认路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            model_path = model_path or self.model_save_path
            
            if not os.path.exists(model_path):
                print(f"[ERROR] 模型文件不存在: {model_path}")
                return False
            
            model_data = torch.load(model_path, map_location=self.device)
            
            self.class_names = model_data["class_names"]
            self.num_classes = model_data["num_classes"]
            
            # 重新构建模型
            self.build_model()
            self.model.load_state_dict(model_data["model_state"])
            
            print(f"[INFO] 模型加载成功: {model_path}")
            print(f"[INFO] 类别: {self.class_names}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 模型加载失败: {e}")
            return False


def main():
    """示例使用"""
    # 创建训练器
    trainer = SceneClassifierTrainer(
        data_dir="../scene_classification_dataset",
        model_save_path="bb_auto_attack/BBAutoAttack_scene_classifier.pt",
        batch_size=16,
        learning_rate=0.001
    )
    
    # 加载数据
    if not trainer.load_data():
        print("数据加载失败，退出程序")
        return
    
    # 构建模型
    trainer.build_model(model_name="resnet18", pretrained=True)
    
    # 开始训练
    history = trainer.train(epochs=20)
    
    print("训练完成！")


if __name__ == "__main__":
    main()