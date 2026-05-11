import pygame
import random
import sys
from Player import Player
from Enemy import Enemy, MonsterType1, MonsterType2
from Projectile import Projectile, Particle
from Map import Map, Obstacles, map_size
from AStar import init_nav_grid
from Items import Bomb, HealthOrb
from Utils import distance
from HighScore import HighScoreManager
 
"""
Module Game Chính (Main Engine Loop).
Đảm nhiệm xây dựng cấu trúc trạng thái màn hình (Main Menu, Gameplay, Score, Game Over).
Đồng thời là vòm Controller gom kết các logic Vật Lý, Di Chuyển, Xử lý va chạm (Collision) và Cập nhật Render.
"""

# Khởi tạo HighScore Manager
high_score_manager = HighScoreManager()
 
# ============ UTILITIES ============
def draw_text(text, font, text_col, surface, x, y):
    """
    Hàm tiện tích Render chữ cái Căn giữa (Center-aligned Text).

    Args:
        text (str): Nội dung thông điệp chuỗi.
        font (pygame.font.Font): Mẫu thư pháp (Font object) của hệ font Pygame.
        text_col (tuple): Mã màu RGB hiển thị.
        surface (pygame.Surface): Khung hiển thị giao diện trỏ kết xuất.
        x (int): Trục hoành giữa của con chữ.
        y (int): Trục tung giữa định vị chữ.
    """
    textobj = font.render(text, True, text_col)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)
 
def draw_text_left(text, font, text_col, surface, x, y):
    """
    Hàm tiện tích Render chữ cái Căn trái (Left-aligned Text).
    Hữu hiệu dùng để viết List Ranking Bảng Xếp hạng nhằm chống lồi lõm cột chữ.
    """
    textobj = font.render(text, True, text_col)
    surface.blit(textobj, (x, y))
 
def create_gradient_surface(width, height, color1, color2):
    """
    Khởi tạo vệt Background trải dải Gradient êm dịu, tiết kiệm bộ nhớ kết xuất điểm mảng.

    Args:
        width (int): Kích cỡ băng phẳng ngang màn.
        height (int): Kích cỡ băng phẳng dọc màn.
        color1 (tuple): Cấu trúc màu trên đỉnh đầu.
        color2 (tuple): Cấu trúc phôi màu vùng Đất ở đáy.

    Returns:
        pygame.Surface: Trải thảm màu chuyển sắc.
    """
    surface = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    return surface
 
# ============ MAIN MENU ============
def main_menu(screen):
    """
    Quản trị Vòng lặp Sảnh Menu Tiền Sảnh Hành nang (Main Menu Loop).
    Vẽ các Nút điều hướng: Bắt Đầu, Bảng Điểm, Thoát. Phục vụ hệ thống Hover và Click event chuột bóng mượt.
    Kết cấu có hiệu ứng Particle giả lập ngân hà trôi tuột, làm UI sinh động.

    Args:
        screen (pygame.Surface): Cửa số xuất hiển thị màn lưới máy tính.

    Returns:
        str: Chuỗi lệnh điều hướng báo cáo phản hồi thao tác user ("start", "scores", "quit").
    """
    clock = pygame.time.Clock()
    click = False
    
    font_title = pygame.font.SysFont("arial", 100, bold=True)
    font_subtitle = pygame.font.SysFont("arial", 40, bold=True)
    font_button = pygame.font.SysFont("arial", 50, bold=True)
    font_small = pygame.font.SysFont("arial", 24)
    
    # Tạo gradient background
    gradient = create_gradient_surface(1200, 720, (15, 15, 35), (40, 20, 60))
    
    pulse_value = 0  # Cho efect pulse của title
    
    while True:
        pulse_value = (pulse_value + 1) % 120
        pulse_ratio = 0.5 + 0.5 * abs(pygame.math.Vector2(1, 0).rotate(pulse_value * 3).x)
        
        screen.blit(gradient, (0, 0))
        
        # Vẽ particle effect (ngôi sao nhỏ)
        for i in range(5):
            x = (pygame.time.get_ticks() // 20 + i * 100) % 1200
            y = 80 + i * 40
            pygame.draw.circle(screen, (200, 150, 255), (x, y), 2)
        
        # Tiêu đề với efect pulse
        title_size = int(100 * pulse_ratio * 0.1 + 90)
        font_title_dynamic = pygame.font.SysFont("arial", title_size, bold=True)
        draw_text("TOP DOWN SHOOTER", font_title_dynamic, (255, 100, 150), screen, 600, 150)
        
        # Subtitle
        draw_text("Battle for Survival", font_subtitle, (150, 200, 255), screen, 600, 280)
        
        mx, my = pygame.mouse.get_pos()
        
        button_start = pygame.Rect(350, 380, 500, 80)
        button_scores = pygame.Rect(350, 500, 500, 80)
        button_quit = pygame.Rect(350, 620, 500, 80)
        
        hover_start = button_start.collidepoint((mx, my))
        hover_scores = button_scores.collidepoint((mx, my))
        hover_quit = button_quit.collidepoint((mx, my))
        
        color_start = (50, 200, 100) if hover_start else (30, 150, 80)
        pygame.draw.rect(screen, color_start, button_start, border_radius=15)
        pygame.draw.rect(screen, (100, 255, 150) if hover_start else (70, 200, 120), button_start, 3, border_radius=15)
        draw_text("START GAME", font_button, (255, 255, 255), screen, 600, 420)
        
        color_scores = (100, 150, 255) if hover_scores else (60, 100, 200)
        pygame.draw.rect(screen, color_scores, button_scores, border_radius=15)
        pygame.draw.rect(screen, (150, 200, 255) if hover_scores else (100, 150, 220), button_scores, 3, border_radius=15)
        draw_text("HIGH SCORES", font_button, (255, 255, 255), screen, 600, 540)
        
        color_quit = (200, 50, 50) if hover_quit else (150, 30, 30)
        pygame.draw.rect(screen, color_quit, button_quit, border_radius=15)
        pygame.draw.rect(screen, (255, 100, 100) if hover_quit else (200, 80, 80), button_quit, 3, border_radius=15)
        draw_text("QUIT", font_button, (255, 255, 255), screen, 600, 660)
        
        if click:
            if button_start.collidepoint((mx, my)):
                return "start"
            if button_scores.collidepoint((mx, my)):
                return "scores"
            if button_quit.collidepoint((mx, my)):
                return "quit"
        
        click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        pygame.display.flip()
        clock.tick(60)
 
# ============ HIGH SCORES SCREEN ============
def high_scores_screen(screen):
    """
    Khu vực Vòng lặp hiển thị Thành tích Bảng Vàng danh dự Top 10 (High Scores Screen).

    Args:
        screen (pygame.Surface): Bề mặt Render Pygame hiển thị kết cấu List điểm số theo dạng Text trãi dài.
    """
    clock = pygame.time.Clock()
    click = False
    
    font_title = pygame.font.SysFont("arial", 80, bold=True)
    font_score = pygame.font.SysFont("arial", 40, bold=True)
    font_small = pygame.font.SysFont("arial", 28)
    font_button = pygame.font.SysFont("arial", 40, bold=True)
    
    gradient = create_gradient_surface(1200, 720, (15, 15, 35), (40, 20, 60))
    
    while True:
        screen.blit(gradient, (0, 0))
        
        draw_text("HIGH SCORES", font_title, (255, 200, 100), screen, 600, 60)
        
        top_scores = high_score_manager.get_top_scores(10)
        
        if top_scores:
            y_pos = 150
            for i, entry in enumerate(top_scores):
                # Rank badge
                rank_color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50) if i == 2 else (150, 150, 150)
                pygame.draw.circle(screen, rank_color, (100, y_pos + 25), 25)
                draw_text(str(i + 1), font_score, (255, 255, 255), screen, 100, y_pos + 25)
                
                score_text = f"{entry['name']:<15} {entry['score']:>8} pts"
                draw_text_left(score_text, font_score, (200, 255, 200), screen, 150, y_pos)
                
                date_text = entry['date']
                draw_text_left(date_text, font_small, (150, 150, 150), screen, 150, y_pos + 45)
                
                y_pos += 55
        else:
            draw_text("Chưa có highscore", font_score, (200, 100, 100), screen, 600, 350)
        
        mx, my = pygame.mouse.get_pos()
        button_back = pygame.Rect(450, 650, 300, 50)
        hover = button_back.collidepoint((mx, my))
        
        color = (100, 100, 200) if hover else (60, 60, 150)
        pygame.draw.rect(screen, color, button_back, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 255) if hover else (100, 100, 200), button_back, 2, border_radius=10)
        draw_text("BACK", font_button, (255, 255, 255), screen, 600, 675)
        
        if click and button_back.collidepoint((mx, my)):
            return
        
        click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        pygame.display.flip()
        clock.tick(60)
 
# ============ GAME OVER SCREEN ============
def game_over_screen(screen, score, is_new_highscore=False):
    """
    Sân khấu Kết Liễu Game (Game Over Loop). 
    Thể hiện tổng kết thành tích, gọi bảng nhấp nháy nhập liệu lưu tên Người Chơi (Typewriter Text Input).
    Nếu điểm đủ cao phá kỷ lục bảng vàng lập tức vinh danh.

    Args:
        screen (pygame.Surface): Cửa số trò chơi gốc.
        score (int): Tham số lượng điểm gom thu được cuối trận.
        is_new_highscore (bool): Cờ hiệu báo mộc đánh giá tân kỷ lục giật giải.
    """
    clock = pygame.time.Clock()
    click = False
    
    font_title = pygame.font.SysFont("arial", 100, bold=True)
    font_score = pygame.font.SysFont("arial", 60, bold=True)
    font_normal = pygame.font.SysFont("arial", 40)
    font_button = pygame.font.SysFont("arial", 45, bold=True)
    font_input = pygame.font.SysFont("arial", 35)
    
    gradient = create_gradient_surface(1200, 720, (30, 10, 10), (60, 20, 20))
    
    player_name = ""
    input_active = is_new_highscore
    input_rect = pygame.Rect(350, 450, 500, 60)
    
    frame_count = 0
    
    while True:
        frame_count += 1
        screen.blit(gradient, (0, 0))
        
        title_color = (255, 100, 100)
        draw_text("GAME OVER", font_title, title_color, screen, 600, 100)
        
        draw_text(f"Your Score: {score}", font_score, (200, 255, 200), screen, 600, 250)
        
        if is_new_highscore:
            draw_text("NEW HIGH SCORE!", font_normal, (255, 215, 0), screen, 600, 350)
            draw_text("Enter your name:", font_normal, (255, 255, 255), screen, 600, 400)
            
            pygame.draw.rect(screen, (100, 100, 100) if input_active else (50, 50, 50), input_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200) if input_active else (100, 100, 100), input_rect, 3, border_radius=10)
            
            # Cursor nháp nháy
            if input_active and (frame_count // 30) % 2:
                cursor_x = input_rect.x + 20 + font_input.size(player_name)[0]
                pygame.draw.line(screen, (200, 200, 200), (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 50), 2)
            
            draw_text_left(player_name, font_input, (255, 255, 255), screen, input_rect.x + 20, input_rect.y + 12)
        
        mx, my = pygame.mouse.get_pos()
        button_menu = pygame.Rect(250, 600, 250, 70)
        button_quit = pygame.Rect(700, 600, 250, 70)
        
        hover_menu = button_menu.collidepoint((mx, my))
        hover_quit = button_quit.collidepoint((mx, my))
        
        color = (100, 150, 255) if hover_menu else (60, 100, 200)
        pygame.draw.rect(screen, color, button_menu, border_radius=10)
        pygame.draw.rect(screen, (150, 200, 255) if hover_menu else (100, 150, 220), button_menu, 3, border_radius=10)
        draw_text("MENU", font_button, (255, 255, 255), screen, 375, 635)
        
        color = (200, 100, 100) if hover_quit else (150, 60, 60)
        pygame.draw.rect(screen, color, button_quit, border_radius=10)
        pygame.draw.rect(screen, (255, 150, 150) if hover_quit else (200, 100, 100), button_quit, 3, border_radius=10)
        draw_text("QUIT", font_button, (255, 255, 255), screen, 825, 635)
        
        if click:
            if button_menu.collidepoint((mx, my)):
                if is_new_highscore and player_name:
                    high_score_manager.add_score(score, player_name)
                return "menu"
            if button_quit.collidepoint((mx, my)):
                if is_new_highscore and player_name:
                    high_score_manager.add_score(score, player_name)
                return "quit"
            if input_active and input_rect.collidepoint((mx, my)):
                pass  
        
        click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if is_new_highscore and player_name:
                    high_score_manager.add_score(score, player_name)
                return "quit"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False
            
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if player_name:
                        high_score_manager.add_score(score, player_name)
                        return "menu"
                elif len(player_name) < 15:
                    player_name += event.unicode
        
        pygame.display.flip()
        clock.tick(60)
 
# ============ GAME LOOP ============
def init_game():
    """
    Thiết lập khởi tạo Pygame Engine cơ sở cấp hệ thống trước khi vận hành.
    Can thiệp phân giải màn trổ và đặt tiêu đề đỉnh.

    Returns:
        pygame.Surface: Trả ra Cửa sổ render gốc (Main game root window).
    """
    pygame.init()
    screen = pygame.display.set_mode((1200, 720))
    pygame.display.set_caption("Top Down Shooter")
    return screen
 
def game_loop(screen):
    """
    Động cơ vòng xoay thực thể Gameplay Logic tàn bạo (Gameplay Engine Loop):
    1. Lắng nghe tương tác Event Phím/Chuột, Đổi vũ khí, Hack Tối Thượng (Dịch chuyển), Chỉ ngắm góc.
    2. Điều phối chuyển động đa chiều cho Player và Hàng đàn chục con Quái thông qua giải thuật A*.
    3. Thẩm định, xử lý các sự kiện bắn súng đạn, chèn Máu (Collision Check 2D Hitboxes).
    4. Trích xuất họa khối và Cập nhật Render tất cả trên Camera Panning Offset linh hoạt.

    Args:
        screen (pygame.Surface): Cửa số OS để xả Sprite lên.

    Returns:
        tuple[int, bool]: Trả về Múi mốc Tích điểm tổng đợt sống (Score), và Cờ hiệu phàn nàm Người dùng Exit ép màn chặn.
    """
    clock = pygame.time.Clock()
    hero = pygame.sprite.GroupSingle(Player(screen.get_size()))
    enemies = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    orbs = pygame.sprite.Group()
    
    score = 0 
    game_map = Map(map_size)
    camera_offset = [0, 0]
    
    init_nav_grid(game_map.obstacles, hero.sprite.radius)
    
    for _ in range(5):
        bombs.add(Bomb((random.randint(100, 2300), random.randint(100, 1300))))
 
    last_enemy_spawn = pygame.time.get_ticks()
    quit_game = False
    
    try:
        indicator_img = pygame.image.load("assert/indicator/indicator.png").convert_alpha()
        indicator_img = pygame.transform.scale(indicator_img, (30, 30)) 
    except Exception:
        indicator_img = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(indicator_img, (0, 255, 255), (5, 5), 4)
 
    while hero.sprite.alive and not quit_game:
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        delta_time = clock.get_time() / 17
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return score, True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Dịch chuyển tức thời đến điểm chuột hiện tại
                    mouse_w = (pygame.mouse.get_pos()[0] + game_map.camera_offset[0], pygame.mouse.get_pos()[1] + game_map.camera_offset[1])
                    hero.sprite.pos = list(mouse_w)
                    hero.sprite.rect.x = int(hero.sprite.pos[0])
                    hero.sprite.rect.y = int(hero.sprite.pos[1])
                    hero.sprite.hitbox.centerx = hero.sprite.rect.centerx
                    hero.sprite.hitbox.centery = hero.sprite.rect.centery
                    hero.sprite.target_pos = None
                if event.key == pygame.K_ESCAPE:
                    return score, False
 
        game_map.update()
        camera_offset = game_map.camera_offset
        
        # Actions
        if keys[pygame.K_1]: hero.sprite.equippedWeapon = hero.sprite.availableWeapons[0]
        if keys[pygame.K_2]: hero.sprite.equippedWeapon = hero.sprite.availableWeapons[1]
        if keys[pygame.K_3]: hero.sprite.equippedWeapon = hero.sprite.availableWeapons[2]
        
        mouse_world = (pygame.mouse.get_pos()[0] + camera_offset[0], pygame.mouse.get_pos()[1] + camera_offset[1])
        if mouse[2]: hero.sprite.target_pos = list(mouse_world) 
        if mouse[0]: hero.sprite.shoot(mouse_world)             
 
        hero.sprite.move(game_map, map_size, delta_time)
        
        for enemy in enemies:
            enemy.move(enemies, hero.sprite.pos, delta_time, game_map)
            enemy.shoot(hero.sprite.pos)
            
        Projectile.particles.update(delta_time)
        for b in bombs: pass
        for o in orbs: 
            o.update(delta_time)
            if distance(o.pos, hero.sprite.pos) < o.radius + hero.sprite.radius:
                if hero.sprite.health < hero.sprite.max_health:
                    hero.sprite.health += o.heal_amount
                    o.kill()
 
        for proj in Enemy.projectiles:
            proj.move(map_size, delta_time)
            if pygame.sprite.collide_circle(proj, hero.sprite):
                proj.kill()
                hero.sprite.health -= 1
                if hero.sprite.health <= 0: hero.sprite.alive = False
 
        for proj in Player.projectiles:
            proj.move(map_size, delta_time)
            hit_enemies = pygame.sprite.spritecollide(proj, enemies, False)
            if hit_enemies:
                proj.kill()
                for e in hit_enemies:
                    e.health -= 1
                    if e.health <= 0:
                        e.kill()
                        score += 10
                        if random.random() < 0.2:
                            orbs.add(HealthOrb(e.pos))
            hit_bombs = pygame.sprite.spritecollide(proj, bombs, False)
            if hit_bombs:
                proj.kill()
                for b in hit_bombs:
                    b.health -= 1
                    if b.health <= 0:
                        b.explode(enemies, Projectile)
                        b.kill()
                        bombs.add(Bomb((random.randint(100, 2300), random.randint(100, 1300))))
                        if random.random() < 0.5: orbs.add(HealthOrb(b.pos))
 
        if pygame.time.get_ticks() - last_enemy_spawn > 2000 and len(enemies) < 5:
            s_side = random.random()
            monster_class = random.choices([MonsterType1, MonsterType2], weights=[4, 1])[0]
            if s_side < 0.25: enemies.add(monster_class((random.randint(0, 2400), 0)))
            elif s_side < 0.5: enemies.add(monster_class((random.randint(0, 2400), 1440)))
            elif s_side < 0.75: enemies.add(monster_class((0, random.randint(0, 1440))))
            else: enemies.add(monster_class((2400, random.randint(0, 1440))))
            last_enemy_spawn = pygame.time.get_ticks()
 
        # ============ RENDER ============
        game_map.render(screen)
        
        for p in Projectile.particles:
            screen.blit(p.image, (p.pos[0] - camera_offset[0], p.pos[1] - camera_offset[1]))
            
        for orb in orbs: orb.render(screen, camera_offset)
        for bomb in bombs: bomb.render(screen, camera_offset)
        
        if hero.sprite.target_pos:
            indicator_rect = indicator_img.get_rect(center=(hero.sprite.target_pos[0] - camera_offset[0], hero.sprite.target_pos[1] - camera_offset[1]))
            screen.blit(indicator_img, indicator_rect)
            
        for proj in Player.projectiles: screen.blit(proj.image, (proj.pos[0] - camera_offset[0], proj.pos[1] - camera_offset[1]))
        for proj in Enemy.projectiles: screen.blit(proj.image, (proj.pos[0] - camera_offset[0], proj.pos[1] - camera_offset[1]))
        
        for e in enemies:
            screen.blit(e.image, e.rect.move(-camera_offset[0], -camera_offset[1]))
            e.draw_health_bar(screen, camera_offset)
            
        screen.blit(hero.sprite.image, hero.sprite.rect.move(-camera_offset[0], -camera_offset[1]))
        hero.sprite.draw_health_bar(screen, camera_offset)
        
        font_hud = pygame.font.SysFont("arial", 32, bold=True)
        pygame.draw.rect(screen, (20, 20, 30, 180), (10, 10, 200, 60), border_radius=10)
        pygame.draw.rect(screen, (100, 150, 255), (10, 10, 200, 60), 2, border_radius=10)
        score_text = font_hud.render(f"Score: {score}", True, (100, 255, 200))
        screen.blit(score_text, (20, 20))
                
        pygame.display.flip()
        clock.tick(60)
        
    return score, False
 
# ============ MAIN (ENTRY POINT) ============
if __name__ == "__main__":
    """Sợi kíp nổ chạy gốc, giữ con thuyền mạch truyện phân bổ qua lại Menu - Game - Quit."""
    screen = init_game()
    
    while True:
        result = main_menu(screen)
        
        if result == "quit":
            break
        elif result == "scores":
            high_scores_screen(screen)
        elif result == "start":
            score, quit_game = game_loop(screen)
            
            if quit_game:
                break
            
            is_new_highscore = high_score_manager.is_high_score(score)
            result = game_over_screen(screen, score, is_new_highscore)
            
            if result == "quit":
                break
    
    pygame.quit()
    sys.exit()