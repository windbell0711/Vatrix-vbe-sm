"""
-*- coding: utf-8 -*-
@Time    : 2026-05-16
@Github  : windbell0711/Vatrix-vbe-sm
@File    : display.py
@Author  : windbell0711
"""
import pygame
import engine
import beach

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
DISPLAY_SPEED = 1

# 1. 初始化
pygame.init()
game_font = pygame.font.Font(None, 36)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("方块正在移动")
clock = pygame.time.Clock() # 控制帧率

# 2. 创建游戏实例
g = engine.VbGame()
beach.test(g)
print(g)

# 3. 主循环 (核心)
running = True
while running:
    # --- 事件处理 (必须有，否则窗口无法关闭)---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- 游戏逻辑更新---
    g.update_game() # 调用你的逻辑

    # --- 绘图 (渲染) ---
    screen.fill((0, 0, 0)) # 填充背景色 (黑色)
    
    # 这里需要你写绘图代码，例如：
    for p in g.plants:
        pygame.draw.rect(screen, (0, 255, 0), p.rect.to_tuple())
        text_str = f"{p.typ} " + (p.state if p.state != "none" else "")
        text_surface = game_font.render(text_str, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=p.rect.get_centre())
        screen.blit(text_surface, text_rect)
    for z in g.zombies:
        pygame.draw.rect(screen, (255, 0, 0), z.rect.to_tuple())
        text_str = (f"{z.typ} HP:{z.hp}") + (f"+{z.helm_hp}" if z.helm_hp > 0 else "")
        text_surface = game_font.render(text_str, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=z.rect.get_centre())
        screen.blit(text_surface, text_rect)
    if g.win or g.lose:
        text_str = "Win!" if g.win else "Lose!"
        text_surface = game_font.render(text_str, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
    
    
    # --- 刷新屏幕 ---
    pygame.display.flip() # 这一行是让画面动起来的关键！

    # --- 控制帧率 ---
    clock.tick(DISPLAY_SPEED * 100)

pygame.quit()
print(g)
