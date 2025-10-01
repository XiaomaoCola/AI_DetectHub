from typing import Dict, List, Optional, Any

from features import FeatureType, FeatureStrategy
from features.GameMode import GameMode
from states.GameState import GameState
from states.state_machine import Detection, WindowInfo


class FeatureRegistry:
    """功能策略注册表"""

    def __init__(self):
        self._strategies: Dict[GameMode, Dict[FeatureType, FeatureStrategy]] = {
            GameMode.HOME_VILLAGE: {},
            GameMode.BUILDER_BASE: {}
        }
        self._execution_order: Dict[GameMode, List[FeatureType]] = {
            GameMode.HOME_VILLAGE: [],
            GameMode.BUILDER_BASE: []
        }

    def register(self, strategy: FeatureStrategy):
        """注册功能策略"""
        game_mode = strategy.game_mode
        feature_type = strategy.feature_type

        self._strategies[game_mode][feature_type] = strategy

        if feature_type not in self._execution_order[game_mode]:
            self._execution_order[game_mode].append(feature_type)

        print(f"[FEATURES] 注册功能策略: {game_mode.value} - {strategy.name}")

    def unregister(self, game_mode: GameMode, feature_type: FeatureType):
        """注销功能策略"""
        if feature_type in self._strategies[game_mode]:
            del self._strategies[game_mode][feature_type]
            self._execution_order[game_mode].remove(feature_type)
            print(f"[FEATURES] 注销功能策略: {game_mode.value} - {feature_type.value}")

    def get_strategy(self, game_mode: GameMode, feature_type: FeatureType) -> Optional[FeatureStrategy]:
        """获取功能策略"""
        return self._strategies[game_mode].get(feature_type)

    def get_all_strategies(self, game_mode: GameMode) -> List[FeatureStrategy]:
        """获取指定模式的所有策略"""
        return list(self._strategies[game_mode].values())

    def execute_features(self,
                         game_mode: GameMode,
                         detections: List[Detection],
                         window_info: WindowInfo,
                         config: Dict[str, Any]) -> Optional[GameState]:
        """
        按顺序执行指定模式下启用的功能

        Args:
            game_mode: 游戏模式
            detections: 检测结果
            window_info: 窗口信息
            config: 用户配置

        Returns:
            Optional[GameState]: 第一个执行成功的功能返回的状态
        """
        executed_count = 0
        mode_strategies = self._strategies[game_mode]
        execution_order = self._execution_order[game_mode]

        for feature_type in execution_order:
            strategy = mode_strategies.get(feature_type)
            if not strategy:
                continue

            # 检查功能是否启用
            if not strategy.is_enabled(config):
                continue

            # 检查冷却期
            if strategy.is_on_cooldown():
                continue

            # 检查执行条件
            if not strategy.can_execute(detections, config):
                continue

            # 执行功能
            print(f"[FEATURES] 执行功能: {game_mode.value} - {strategy.name} - {strategy.description}")
            try:
                result = strategy.execute(detections, window_info)
                strategy.update_execution_time()
                executed_count += 1

                # 如果功能返回了状态转换，立即返回
                if result:
                    print(f"[FEATURES] 功能 {strategy.name} 触发状态转换: {result.value}")
                    return result

            except Exception as e:
                print(f"[FEATURES] 功能 {strategy.name} 执行失败: {e}")
                continue

        if executed_count == 0:
            print(f"[FEATURES] {game_mode.value} - 没有可执行的功能")
        else:
            print(f"[FEATURES] {game_mode.value} - 执行了 {executed_count} 个功能")

        return None

    def set_execution_order(self, game_mode: GameMode, order: List[FeatureType]):
        """设置功能执行顺序"""
        # 只保留已注册的功能
        mode_strategies = self._strategies[game_mode]
        self._execution_order[game_mode] = [ft for ft in order if ft in mode_strategies]
        print(f"[FEATURES] 更新 {game_mode.value} 执行顺序: {[ft.value for ft in self._execution_order[game_mode]]}")

    def get_execution_order(self, game_mode: GameMode) -> List[FeatureType]:
        """获取当前执行顺序"""
        return self._execution_order[game_mode].copy()

    def get_available_features(self, game_mode: GameMode) -> List[Dict[str, str]]:
        """获取指定模式的可用功能列表（用于GUI）"""
        features = []
        mode_strategies = self._strategies[game_mode]
        for strategy in mode_strategies.values():
            features.append({
                'type': strategy.feature_type.value,
                'name': strategy.name,
                'description': strategy.description
            })
        return features
