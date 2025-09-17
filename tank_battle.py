#!/usr/bin/env python3
"""
坦克大战游戏 - Tank Battle Game
使用方向键控制移动，空格键射击
Player 1: WASD移动，空格射击
Player 2: 方向键移动，Enter射击
"""

import curses
import time
import random
from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameObject:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.alive = True
    
    def draw(self, screen):
        if self.alive:
            try:
                screen.addstr(self.y, self.x, self.symbol)
            except:
                pass

class Tank(GameObject):
    def __init__(self, x, y, symbol, color_pair):
        super().__init__(x, y, symbol)
        self.direction = Direction.UP
        self.color_pair = color_pair
        self.health = 3
        self.last_shot_time = 0
        self.shot_cooldown = 0.5  # 射击冷却时间
    
    def move(self, dx, dy, max_x, max_y):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 边界检查
        if 0 < new_x < max_x - 1 and 0 < new_y < max_y - 1:
            self.x = new_x
            self.y = new_y
            
            # 更新方向和坦克外观
            if dx > 0:
                self.direction = Direction.RIGHT
                self.symbol = '>'
            elif dx < 0:
                self.direction = Direction.LEFT
                self.symbol = '<'
            elif dy > 0:
                self.direction = Direction.DOWN
                self.symbol = 'v'
            elif dy < 0:
                self.direction = Direction.UP
                self.symbol = '^'
    
    def can_shoot(self):
        current_time = time.time()
        if current_time - self.last_shot_time > self.shot_cooldown:
            self.last_shot_time = current_time
            return True
        return False
    
    def shoot(self):
        if self.can_shoot():
            dx, dy = self.direction.value
            return Bullet(self.x + dx, self.y + dy, self.direction)
        return None
    
    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            try:
                screen.attron(curses.color_pair(self.color_pair))
                screen.addstr(self.y, self.x, self.symbol)
                screen.attroff(curses.color_pair(self.color_pair))
            except:
                pass

class Bullet(GameObject):
    def __init__(self, x, y, direction):
        super().__init__(x, y, '•')
        self.direction = direction
        self.speed = 0.1  # 子弹移动速度
        self.last_move_time = time.time()
    
    def update(self, max_x, max_y):
        current_time = time.time()
        if current_time - self.last_move_time > self.speed:
            dx, dy = self.direction.value
            self.x += dx
            self.y += dy
            self.last_move_time = current_time
            
            # 检查是否出界
            if self.x <= 0 or self.x >= max_x - 1 or self.y <= 0 or self.y >= max_y - 1:
                self.alive = False

class Obstacle(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, '#')
        self.destructible = True

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.max_y, self.max_x = screen.getmaxyx()
        self.player1 = None
        self.player2 = None
        self.bullets = []
        self.obstacles = []
        self.game_over = False
        self.winner = None
        
        # 初始化颜色
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Player 1
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Player 2
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # 子弹
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 障碍物
        
        self.init_game()
    
    def init_game(self):
        # 创建玩家坦克
        self.player1 = Tank(5, self.max_y // 2, '^', 1)
        self.player2 = Tank(self.max_x - 5, self.max_y // 2, '^', 2)
        
        # 创建随机障碍物
        for _ in range(20):
            x = random.randint(10, self.max_x - 10)
            y = random.randint(3, self.max_y - 3)
            self.obstacles.append(Obstacle(x, y))
    
    def handle_input(self, key):
        if key == -1:  # 没有按键
            return
        
        # Player 1 控制 (WASD + 空格)
        if key == ord('w'):
            self.player1.move(0, -1, self.max_x, self.max_y)
        elif key == ord('s'):
            self.player1.move(0, 1, self.max_x, self.max_y)
        elif key == ord('a'):
            self.player1.move(-1, 0, self.max_x, self.max_y)
        elif key == ord('d'):
            self.player1.move(1, 0, self.max_x, self.max_y)
        elif key == ord(' '):
            bullet = self.player1.shoot()
            if bullet:
                self.bullets.append(bullet)
        
        # Player 2 控制 (方向键 + Enter)
        elif key == curses.KEY_UP:
            self.player2.move(0, -1, self.max_x, self.max_y)
        elif key == curses.KEY_DOWN:
            self.player2.move(0, 1, self.max_x, self.max_y)
        elif key == curses.KEY_LEFT:
            self.player2.move(-1, 0, self.max_x, self.max_y)
        elif key == curses.KEY_RIGHT:
            self.player2.move(1, 0, self.max_x, self.max_y)
        elif key == ord('\n'):  # Enter键
            bullet = self.player2.shoot()
            if bullet:
                self.bullets.append(bullet)
        
        # 退出游戏
        elif key == ord('q'):
            self.game_over = True
    
    def check_collisions(self):
        # 检查子弹与坦克的碰撞
        for bullet in self.bullets[:]:
            if not bullet.alive:
                continue
            
            # 检查与Player 1的碰撞
            if self.player1.alive and bullet.x == self.player1.x and bullet.y == self.player1.y:
                self.player1.hit()
                bullet.alive = False
                if not self.player1.alive:
                    self.winner = "Player 2"
                    self.game_over = True
            
            # 检查与Player 2的碰撞
            if self.player2.alive and bullet.x == self.player2.x and bullet.y == self.player2.y:
                self.player2.hit()
                bullet.alive = False
                if not self.player2.alive:
                    self.winner = "Player 1"
                    self.game_over = True
            
            # 检查与障碍物的碰撞
            for obstacle in self.obstacles[:]:
                if obstacle.alive and bullet.x == obstacle.x and bullet.y == obstacle.y:
                    bullet.alive = False
                    if obstacle.destructible:
                        obstacle.alive = False
        
        # 移除死亡的子弹
        self.bullets = [b for b in self.bullets if b.alive]
        # 移除被摧毁的障碍物
        self.obstacles = [o for o in self.obstacles if o.alive]
    
    def update(self):
        # 更新所有子弹
        for bullet in self.bullets:
            bullet.update(self.max_x, self.max_y)
        
        # 检查碰撞
        self.check_collisions()
    
    def draw(self):
        self.screen.clear()
        
        # 绘制边框
        for x in range(self.max_x):
            try:
                self.screen.addstr(0, x, '═')
                self.screen.addstr(self.max_y - 1, x, '═')
            except:
                pass
        
        for y in range(self.max_y):
            try:
                self.screen.addstr(y, 0, '║')
                self.screen.addstr(y, self.max_x - 1, '║')
            except:
                pass
        
        # 绘制角落
        try:
            self.screen.addstr(0, 0, '╔')
            self.screen.addstr(0, self.max_x - 1, '╗')
            self.screen.addstr(self.max_y - 1, 0, '╚')
            self.screen.addstr(self.max_y - 1, self.max_x - 1, '╝')
        except:
            pass
        
        # 绘制游戏信息
        try:
            info = f"坦克大战 | P1生命: {self.player1.health} | P2生命: {self.player2.health} | 按Q退出"
            self.screen.addstr(0, 2, info[:self.max_x-4])
        except:
            pass
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # 绘制坦克
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # 显示游戏结束信息
        if self.game_over and self.winner:
            msg = f" {self.winner} 获胜! 按任意键退出 "
            y = self.max_y // 2
            x = (self.max_x - len(msg)) // 2
            try:
                self.screen.attron(curses.color_pair(3))
                self.screen.addstr(y, x, msg)
                self.screen.attroff(curses.color_pair(3))
            except:
                pass
        
        self.screen.refresh()
    
    def run(self):
        # 设置非阻塞输入
        self.screen.nodelay(True)
        self.screen.keypad(True)
        curses.curs_set(0)  # 隐藏光标
        
        while not self.game_over:
            key = self.screen.getch()
            self.handle_input(key)
            self.update()
            self.draw()
            time.sleep(0.05)  # 控制游戏速度
        
        # 游戏结束，等待按键
        self.screen.nodelay(False)
        self.screen.getch()

def main(screen):
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    print("坦克大战游戏")
    print("=" * 40)
    print("玩家1控制:")
    print("  W/A/S/D - 上/左/下/右移动")
    print("  空格键 - 射击")
    print()
    print("玩家2控制:")
    print("  方向键 - 移动")
    print("  Enter键 - 射击")
    print()
    print("按Q退出游戏")
    print("=" * 40)
    print("按Enter键开始游戏...")
    input()
    
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\n游戏被中断")
    except Exception as e:
        print(f"游戏出错: {e}")
    
    print("感谢游玩！")