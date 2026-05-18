import pygame
import math
import Weapon
from Utils import normalize_vector
from Map import map_size

"""
Module xây dựng Bộ Nhân Vật Trung Tâm (Hero/Player Player).
Thực hiện ràng buộc các chỉ số sinh học của Người đội trưởng chiến dịch: Máu, Độ di chuyển, Vũ khí, Camera 2D.
"""

class Player(pygame.sprite.Sprite):
    """
    Lớp đại diện cho nhân vật người chơi (Player) trong game.
    Tích hợp hệ thống Animation khung hoạt ảnh, xử lý va chạm Box tĩnh và vũ khí cầm tay động học.

    Attributes:
        projectiles (pygame.sprite.Group): Nhóm (Group) quản lý tất cả các viên đạn do người chơi bắn ra.
        radius (int): Bán kính khối cầu vô hình để dò tìm tiếp xúc Item.
        frames (list): Danh sách lưu các khung hình phân dải (spritesheet img) dùng cho vòng lặp chuyển động.
        current_frame (int): Chỉ số Index mảng của khung hình hiện trạng đang show.
        animation_speed (int): Dãn cách mili giây (ms) giữa mỗi cữ chuyển Frame.
        image (pygame.Surface): Texture hiển thị thực tiễn của người chơi.
        rect (pygame.Rect): Khung chóp giới hình đồ họa hình chữ nhật vuông vức xung quanh Sprite.
        hitbox (pygame.Rect): Khối Va chạm thật sự (Thường ép nhỏ hơn rect để mường tượng cảm giác 3D Depth độ sâu).
        pos (list): Danh sách chứa tọa độ [x, y] Float nhằm hỗ trợ cho Delta Time di chuyển mịn màng.
        health (int): Thể lực cột HP hiện tại của nhân vật anh hùng.
        movementSpeed (int): Điểm Vận Tốc tĩnh tốc chạy thường hành.
        availableWeapons (list): Mảng danh sách ba lô súng ống sở hữu.
        equippedWeapon (Weapon): Biến con trỏ trỏ đích danh mục khẩu súng đang kề trên tay.
        target_pos (tuple | None): Tọa độ mục tiêu đích đến khi có lệnh phím chuột Autopath thả trôi ngắm.
    """
    projectiles = pygame.sprite.Group()
    
    def __init__(self, screenSize):
        """Khởi tạo toàn bộ thuộc tính Người Chơi, cấp vũ khí, máu hiển thị tại trung khu bản đồ gốc."""
        super().__init__()
        self.radius = 20 
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 100
        self.last_update = pygame.time.get_ticks()

        
        for i in range(0, 8):
            img = pygame.image.load(f"_internal/assert/hero/hero_{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 40)) 
            self.frames.append(img)
                
        self.image = self.frames[0]
        
    
        self.rect = self.image.get_rect(x=screenSize[0]//2, y=screenSize[1]//2)
        self.hitbox = self.rect.inflate(-16, -16) 
        self.pos = [screenSize[0] // 2, screenSize[1] // 2]
        self.health, self.max_health = 6, 6
        self.alive = True
        self.movementVector, self.movementSpeed = [0, 0], 5
        self.availableWeapons = [Weapon.Pistol(), Weapon.Shotgun(), Weapon.MachineGun()]
        self.equippedWeapon = self.availableWeapons[0]
        self.target_pos = None
        self.health_bar_width, self.health_bar_height = 40, 6

    def update_animation(self, is_moving):
        """
        Cập nhật khung hình (animation) rảo bước mượt mà. 

        Args:
            is_moving (bool): Lệch pha di chuyển. Chạy vòng lặp nếu True, dừng cứng 1 frame tĩnh nếu False.
        """
        if not self.frames:
            return

        now = pygame.time.get_ticks()

        if is_moving:
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
        else:
            self.current_frame = 0
            self.image = self.frames[0]

    def move(self, game_map, screenSize, tDelta):
        """
        Khối điều tiết não bộ định hướng 8 chiều thông qua Nút bấm WASD hoặc Autopath.
        Chặn góc va đập cứng giới biên màn vách chắn và Khối tĩnh Đá, Cây dựa vào Box AABB Collision Logic.

        Args:
            game_map (Map): Gọi tham chiếu Hệ sinh thái MAP để lấy Obstacles tránh đường.
            screenSize (tuple): Cấu trúc đo đạc quy mô Map gốc.
            tDelta (float): Bù lệch trôi khung (Time Delta scale).
        """
        keys = pygame.key.get_pressed()
        kb_dx = 0
        kb_dy = 0
        if keys[pygame.K_w]: kb_dy -= 1
        if keys[pygame.K_s]: kb_dy += 1
        if keys[pygame.K_a]: kb_dx -= 1
        if keys[pygame.K_d]: kb_dx += 1

        if kb_dx != 0 or kb_dy != 0:
            self.target_pos = None
            self.movementVector = [kb_dx, kb_dy]
        elif self.target_pos:
            dx = self.target_pos[0] - self.pos[0]
            dy = self.target_pos[1] - self.pos[1]
            if math.hypot(dx, dy) > 5:
                self.movementVector = [dx, dy]
            else:
                self.movementVector, self.target_pos = [0, 0], None
        else:
            self.movementVector = [0, 0]
            
        self.movementVector = normalize_vector(self.movementVector)
        
        vx = self.movementVector[0] * self.movementSpeed * tDelta
        vy = self.movementVector[1] * self.movementSpeed * tDelta

        is_moving = abs(vx) > 0 or abs(vy) > 0
        self.update_animation(is_moving)

        obstacles = game_map.get_obstacles()

        # Xử lý Logic tách trục ngăn giật (Trục X riêng, Trục Y riêng)
        self.pos[0] += vx
        self.rect.x = int(self.pos[0])
        self.hitbox.centerx = self.rect.centerx 

        if self.rect.left < 0:
            self.rect.left = 0
            self.hitbox.centerx = self.rect.centerx
        if self.rect.right > map_size[0]:
            self.rect.right = map_size[0]
            self.hitbox.centerx = self.rect.centerx

        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                if vx > 0: 
                    self.hitbox.right = obs.rect.left
                elif vx < 0: 
                    self.hitbox.left = obs.rect.right
                self.rect.centerx = self.hitbox.centerx  

        self.pos[0] = float(self.rect.x)

        self.pos[1] += vy
        self.rect.y = int(self.pos[1])
        self.hitbox.centery = self.rect.centery  
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.hitbox.centery = self.rect.centery
        if self.rect.bottom > map_size[1]:
            self.rect.bottom = map_size[1]
            self.hitbox.centery = self.rect.centery

        for obs in obstacles:
            if self.hitbox.colliderect(obs.rect):
                if vy > 0: 
                    self.hitbox.bottom = obs.rect.top
                elif vy < 0: 
                    self.hitbox.top = obs.rect.bottom
                self.rect.centery = self.hitbox.centery  
                
        self.pos[1] = float(self.rect.y)

    def shoot(self, mousePos):
        """
        Nã đạn theo hướng trỏ chuột. Chuyển tiếp công việc cho biến EquippedWeapon.

        Args:
            mousePos (tuple): Cụm điểm ngắm đích (X, Y) đã bù lệch Camera Panning vào Map.
        """
        self.equippedWeapon.shoot(self, mousePos)
    
    def draw_health_bar(self, surface, camera_offset):
        """
        Gói UI vẽ thanh HP hiển thị tình trạng kiệt quệ máu bám trên đỉnh đầu nhân vật.
        Màng thanh máu có viền trắng tinh tế, vạch xanh ruột đỏ.

        Args:
            surface (pygame.Surface): Cửa số OS.
            camera_offset (tuple/list): Lệch trục màn để trừ ngược lại điểm ghim Render.
        """
        screen_x = int(self.pos[0] - camera_offset[0])
        screen_y = int(self.pos[1] - camera_offset[1])
        center_x = screen_x + 20 
        bar_x = int(center_x - self.health_bar_width // 2)
        bar_y = int(screen_y - 30)
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, self.health_bar_width, self.health_bar_height))
        hp_perc = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, int(self.health_bar_width * hp_perc), self.health_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, self.health_bar_width, self.health_bar_height), 1)