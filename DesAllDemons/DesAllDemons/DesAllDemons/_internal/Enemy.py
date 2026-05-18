import random
import pygame
import math
from AStar import a_star_search
from Map import map_size
from Utils import normalize_vector
import Projectile

"""
Module này bao hàm cấu trúc định hình Kẻ địch trong game (Enemy Entity).
Hệ thống xử lý di chuyển theo giải thuật A-Star kết hợp di chuyển theo vector.
"""

class Enemy(pygame.sprite.Sprite):
    """
    Lớp cơ sở chủ đạo đại diện cho Kẻ địch (Enemy). Quản lý tổng quan về trạng thái sống chết, định vị trí hiển thị, bộ di chuyển theo A*, 
    sức khỏe (Máu) và các vòng lặp hoat ảnh (Animation loop).

    Attributes:
        projectiles (pygame.sprite.Group): Group statics chứa các viên đạn bắn ra dùng chung cho hệ logic.
        radius (int): Bán kính thiết diện dùng cho Culling và Padding đường đi né chướng ngại.
        frames (list): Tích lũy dải khung hình Sprite hoạt ảnh của cá thể quái.
        health (int/float): Bộ nhớ chịu đựng sát thương nội tại sức bền.
        movementSpeed (float): Chỉ số BaseSpeed tốc độ di chuyển cơ bản.
        weaponCooldown (int): Chu kỳ quy chuẩn của vũ khí mỗi đợt nhả đạn bắn (ms).
        path (list): Waypoint dẫn xuất định tuyến trả về từ thuật toán A*.
    """
    projectiles = pygame.sprite.Group()
    
    def __init__(self, pos):
        """
        Khởi tạo thực thể Kẻ địch tại một điểm vật lý ban đầu tùy ý trên bản đồ.

        Args:
            pos (tuple[int, int] | list): Tọa độ trung tâm x, y sinh ra của kẻ quái vật.
        """
        super().__init__()
        self.radius = random.randint(15, 20)

        self.frames = []
        self.current_frame = 0 
        self.animation_speed = 100 
        self.last_update = pygame.time.get_ticks()
        
        self.image = pygame.Surface([40, 40], pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (20, 20), 20)
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-16, -16)
        
        self.pos = list(pos)
        self.movementVector = [0, 0]
        self.movementSpeed = 1.5
        self.lastShot = pygame.time.get_ticks()
        self.weaponCooldown = 1500
        
        self.health, self.max_health = 2, 2
        
        self.path = []
        self.last_path_update, self.path_update_interval = 0, 400

    def update_animation(self):
        """
        Cập nhật kết xuất khung hình (Animation Frame) vòng lặp mượt đi lên dựa trên Time Delta và chu kỳ Update_speed.
        Ngăn chặn việc frame bị xoay quá nhanh so với tốc độ tính toán đồ họa gốc.
        """
        if not self.frames:
            return

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def move(self, enemies, playerPos, tDelta, game_map):
        """
        Trung tâm đầu não chi phối luồng xử lý di chuyển của enemies:
        1. Gọi tọa độ đường truyền A* định hướng tìm đến Player.
        2. Tịnh tiến hướng tiếp theo qua thuật toán nội suy Vector.
        3. Validate xử lý cản và trượt chướng ngại vật cứng rải rác trên MAP.
        4. Separation Forces - Hiệu ứng trượt lực đẩy lùi những kẻ địch khác khi gom chặt vào đồng rầm.

        Args:
            enemies (pygame.sprite.Group): Module nhóm tất cả quái vật phân bổ chung bản đồ.
            playerPos (tuple): Tọa độ quy chiếu Người chơi.
            tDelta (float): Sai số lượng dời khung nhịp độ chênh lệch.
            game_map (Map): Cấu trúc Map cấp tải Collision tránh đường.
        """
        current_time = pygame.time.get_ticks()

        self.update_animation()

        if current_time - self.last_path_update > self.path_update_interval or not self.path:
            self.last_path_update = current_time
            self.path = a_star_search(self.pos, playerPos)

        target_pos = playerPos 
        if self.path:
            next_node = self.path[0]
            if math.hypot(next_node[0] - self.pos[0], next_node[1] - self.pos[1]) < self.radius * 1.5:
                self.path.pop(0)
                if self.path: next_node = self.path[0]
                else: next_node = playerPos
            target_pos = next_node

        self.movementVector = normalize_vector((target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]))
        vx, vy = self.movementVector[0] * self.movementSpeed * tDelta, self.movementVector[1] * self.movementSpeed * tDelta

        obstacles = game_map.get_obstacles()

        self.pos[0] += vx
        self.rect.centerx = int(self.pos[0])
        self.hitbox.centerx = self.rect.centerx
        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                if vx > 0: self.hitbox.right = obs.rect.left
                elif vx < 0: self.hitbox.left = obs.rect.right
                self.rect.centerx = self.hitbox.centerx
                self.pos[0] = float(self.rect.centerx)

        self.pos[1] += vy
        self.rect.centery = int(self.pos[1])
        self.hitbox.centery = self.rect.centery
        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                if vy > 0: self.hitbox.bottom = obs.rect.top
                elif vy < 0: self.hitbox.top = obs.rect.bottom
                self.rect.centery = self.hitbox.centery
                self.pos[1] = float(self.rect.centery)

        pushX, pushY = 0, 0
        for sprite in enemies:
            if sprite is self: continue
            if abs(sprite.pos[0] - self.pos[0]) < 100 and abs(sprite.pos[1] - self.pos[1]) < 100:
                if pygame.sprite.collide_circle(self, sprite):
                    pushX += self.pos[0] - sprite.pos[0]
                    pushY += self.pos[1] - sprite.pos[1]

        pv = normalize_vector([pushX, pushY])
        self.pos[0] += pv[0] * 0.5
        self.pos[1] += pv[1] * 0.5
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))
        self.hitbox.center = self.rect.center

    def shoot(self, playerPos):
        """
        Tính toán chu kỳ hồi đạn (Weapon Cooldown) và nhả một góc bắn đạn chĩa thẳng đến tọa thủ của Hero.

        Args:
            playerPos (tuple[float, float]): Tọa độ (x, y) căn chỉnh hướng Vector bắn súng.
        """
        if pygame.time.get_ticks() - self.lastShot > self.weaponCooldown:
            direction = normalize_vector((playerPos[0] - self.pos[0], playerPos[1] - self.pos[1]))
            self.lastShot = pygame.time.get_ticks()
            self.projectiles.add(Projectile.Projectile(self.pos, direction, 3, 500, (255, 0, 0), is_player=False))

    def draw_health_bar(self, surface, camera_offset):
        """
        Vẽ thanh máu đỏ thẫm (Health bar) bám nổi trên đỉnh đầu kẻ địch liên kết chặt chẽ vào khu vực Cờ màn.
        Độ tịnh tiến xói mòn màu sắc lệ thuộc hoàn toàn vào tỷ lệ máu chênh lệch Max - Min.

        Args:
            surface (pygame.Surface): Cửa sổ tương tác màn hình app.
            camera_offset (list): Công cụ trừ bộ lệch Panning Edge góc máy toàn cảnh.
        """
        screen_x, screen_y = int(self.pos[0] - camera_offset[0]), int(self.pos[1] - camera_offset[1])
        bar_w, bar_h = 30, 4
        bar_x, bar_y = int(screen_x - bar_w // 2), int(screen_y - 25)
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, int(bar_w * max(0, self.health / self.max_health)), bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1)

class MonsterType1(Enemy):
    """
    Bản thiết kế cấu trúc Quái vật hạng nhẹ (Fly Monster - Loài côn trùng ngắm bắn và di chuyển lơ lửng).
    Thừa hưởng cốt lõi logic Enemy nhưng chỉnh đổi Skin diện mạo hiển thị, hạ thấp lượng Máu (Máu = 3).
    """
    def __init__(self, pos):
        """
        Khởi động đối tượng quái thú bay. Ghi đè chỉ số vật lý, đạn và hoạt ảnh.
        """
        super().__init__(pos) 
        
        self.radius = 20
        self.health, self.max_health = 3, 3 
        self.movementSpeed = 1.6 
        self.weaponCooldown = 2000
        self.animation_speed = 100 
 
        self.frames = []
        try:
            for i in range(0, 6):
                img = pygame.image.load(f"_internal/assert/enemies/fly/fly_{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (50, 50))
                self.frames.append(img)
                
            self.image = self.frames[0]
        except Exception as e:
            pass 
            
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-30, -30)

class MonsterType2(Enemy):
    """
    Bản thiết kế cấu trúc Quái vật dạng Cứng (Walk Monster - Quái vật bộ binh bước dài).
    Lượng máu tăng cao cường lực kháng đòn (5 Máu), bộ Skin thiết lập dạng bước đi đè trên mặt phẳng đất.
    """
    def __init__(self, pos):
        """
        Khởi tạo đối tượng tịnh tiến bước chậm với sát thương và máu trâu bò cứng cáp.
        """
        super().__init__(pos) 
        
        self.radius = 20
        self.health, self.max_health = 5, 5 
        self.movementSpeed = 1.6 
        self.weaponCooldown = 2000
        self.animation_speed = 100 
 
        self.frames = []
        try:
            for i in range(0, 8):
                img = pygame.image.load(f"_internal/assert/enemies/walk/walk_{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (50, 50))
                self.frames.append(img)
                
            self.image = self.frames[0]
        except Exception as e:
            pass 
            
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-30, -30)