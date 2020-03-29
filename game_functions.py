import sys
from time import sleep

import pygame
from ship import Ship
from bullet import Bullet
from alien import Alien


def store_high_score(stats):
    with open("high_score.txt") as file_object:
        stored_high_score = int(file_object.read().strip())

    if stats.high_score > stored_high_score:
        stored_high_score = stats.high_score
        with open("high_score.txt",'w') as file_object:
            file_object.write(str(stored_high_score))


def check_keydown_events(event, ship, game_settings, screen, bullets, stats, aliens):
    """响应按键"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(game_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        store_high_score(stats)
        sys.exit()
    elif event.key == pygame.K_p:
        start_game(game_settings, stats, ship, aliens, bullets, screen)


def check_keyup_events(event, ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ship, game_settings, stats, screen, bullets, play_button, aliens, sb):
    """响应按键和鼠标事件"""

    # 监视键盘和鼠标事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            store_high_score(stats)
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(game_settings, stats, play_button, mouse_x, mouse_y, ship, aliens, bullets, screen, sb)

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ship, game_settings, screen, bullets, stats, aliens)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)


def start_game(game_settings, stats, ship, aliens, bullets, screen, sb):
    """重新开始游戏"""
    # 隐藏光标
    pygame.mouse.set_visible(False)

    # 重置游戏统计信息
    stats.reset_stats()
    stats.game_active = True

    # 清空外星人列表和子弹列表
    aliens.empty()
    bullets.empty()

    # 创建一群新的外星人，并让飞船居中
    create_fleet(game_settings, screen, ship, aliens)
    ship.center_ship()

    # 重置游戏设置
    game_settings.initialize_dynamic_settings()

    # 更新得分板信息
    sb.prep_score()
    sb.prep_level()
    sb.prep_ships()


def check_play_button(game_settings, stats, play_button, mouse_x, mouse_y, ship, aliens, bullets, screen, sb):
    """在玩家单击Play按钮时开始新游戏"""
    # 检查鼠标单击位置是否在Play按钮的rect内
    if play_button.rect.collidepoint(mouse_x, mouse_y) and not stats.game_active:
        start_game(game_settings, stats, ship, aliens, bullets, screen, sb)


def update_screen(game_settings, stats, screen, ship, aliens, bullets, play_button, sb):
    """更新屏幕上的图像，并切换到新屏幕"""

    # 每次循环时都重绘屏幕
    screen.fill(game_settings.bg_color)

    # 重绘子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    # 重绘飞船
    ship.blitme()

    # 重绘外星人
    aliens.draw(screen)

    # 显示得分
    sb.show_score()

    # 如果游戏处于非活动状态，就绘制Play按钮
    if not stats.game_active:
        play_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()


def update_bullets(game_settings, stats, screen, ship, bullets, aliens, sb):
    """更新子弹的位置，并删除已消失的子弹"""
    # 更新子弹的位置
    bullets.update()

    # 删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(game_settings, stats, screen, ship, aliens, bullets, sb)


def check_high_score(stats, sb):
    """检查是否诞生了新的最高得分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def check_bullet_alien_collisions(game_settings, stats, screen, ship, aliens, bullets, sb):
    """响应子弹和外星人的碰撞"""
    # 检查是否有子弹击中了外星人
    # 如果是这样，就删除相应的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += game_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # 删除现有的子弹并新建一群外星人
        bullets.empty()
        game_settings.increase_speed()

        # 提高玩家等级
        stats.level += 1
        sb.prep_level()
        create_fleet(game_settings, screen, ship, aliens)


def check_fleet_edges(game_settings, aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(game_settings, aliens)
            break


def change_fleet_direction(game_settings, aliens):
    """将整群外星人下移，并改变它们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += game_settings.fleet_drop_speed
    game_settings.fleet_direction *= -1


def ship_hit(game_settings, stats, screen, ship, aliens, bullets, sb):
    """响应被外星人撞到的飞船"""
    if stats.ships_left > 0:
        # 将ships_left减1
        stats.ships_left -= 1

        # 更新记分牌
        sb.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并将飞船放在屏幕底部中央
        create_fleet(game_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(game_settings, stats, screen, ship, aliens, bullets, sb):
    """检查是否有外星人到达了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样进行处理
            ship_hit(game_settings, stats, screen, ship, aliens, bullets, sb)
            break


def update_aliens(game_settings, stats, screen, ship, aliens, bullets, sb):
    """
    检查是否有外星人位于屏幕边缘，并更新整群外星人的位置
    """
    check_fleet_edges(game_settings, aliens)
    aliens.update()

    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(game_settings, stats, screen, ship, aliens, bullets, sb)

    # 检查是否有外星人到达屏幕底端
    check_aliens_bottom(game_settings, stats, screen, ship, aliens, bullets, sb)


def fire_bullet(game_settings, screen, ship, bullets):
    """如果还没有到达限制，就发射一颗子弹"""
    # 创建新子弹，并将其加入到编组bullets中
    if len(bullets) < game_settings.bullets_allowed:
        new_bullet = Bullet(game_settings, screen, ship)
        bullets.add(new_bullet)


def get_number_aliens_x(game_settings, alien_width):
    """计算每行可容纳多少个外星人"""
    available_space_x = game_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(game_settings, ship_height, alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y = game_settings.screen_height - 3 * alien_height - ship_height
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(game_settings, screen, aliens, alien_number, row_number):
    """创建一个外星人并将其放在当前行"""
    alien = Alien(game_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(game_settings, screen, ship, aliens):
    """创建外星人群"""
    # 创建一个外星人，并计算一行可容纳多少个外星人
    # 外星人间距为外星人宽度
    alien = Alien(game_settings, screen)
    alien_width = alien.rect.width
    alien_height = alien.rect.height
    number_aliens_x = get_number_aliens_x(game_settings, alien_width)
    number_rows = get_number_rows(game_settings, ship.rect.height, alien_height)

    # 创建第一行外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            # 创建一个外星人并将其加入当前行
            create_alien(game_settings, screen, aliens, alien_number, row_number)



