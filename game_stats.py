class GameStats():
    """跟踪游戏的统计信息"""

    def __init__(self, game_settings):
        """初始化统计信息"""
        self.game_settings = game_settings
        self.reset_stats()

        # 游戏刚启动时处于非活动状态
        self.game_active = False

        # 在任何情况下都不应重置最高得分
        with open("high_score.txt") as file_object:
            self.high_score = int(file_object.read().strip())

    def reset_stats(self):
        """初始化在游戏运行期间可能变化的统计信息"""
        self.ships_left = self.game_settings.ship_limit
        self.score = 0
        self.level = 1