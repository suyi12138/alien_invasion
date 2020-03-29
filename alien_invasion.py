import sys

import pygame
from ship import Ship
import game_functions as gf
from pygame.sprite import Group
from alien import Alien
from game_stats import GameStats
from settings import Settings
from button import Button
from scoreboard import Scoreboard

def run_game():
    """
    游戏运行主程序
    """

    # 初始化pygame、 设置和屏幕对象
    pygame.init()
    game_settings = Settings()
    screen = pygame.display.set_mode((game_settings.screen_width, game_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    # 创建Play按钮
    play_button = Button(game_settings, screen, "Play")

    # 创建一个用于存储游戏统计信息的实例
    stats = GameStats(game_settings)

    # 创建记分牌
    sb = Scoreboard(game_settings, screen, stats)

    # 创建一艘飞船
    ship = Ship(screen, game_settings)

    # 创建一个用于存储子弹的编组
    bullets = Group()

    # 创建外星人编组
    aliens = Group()

    # 创建外星人群
    gf.create_fleet(game_settings, screen, ship, aliens)

    # 开始游戏的主循环
    while True:
        gf.check_events(ship, game_settings, stats, screen, bullets, play_button, aliens, sb)

        if stats.game_active:
            ship.update()
            gf.update_bullets(game_settings, stats, screen, ship, bullets, aliens, sb)
            gf.update_aliens(game_settings, stats, screen, ship, aliens, bullets, sb)

        gf.update_screen(game_settings, stats, screen, ship, aliens, bullets, play_button, sb)


run_game()

