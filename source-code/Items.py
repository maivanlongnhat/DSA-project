import pygame
import math
from Projectile import Projectile, Particle

"""
Module quản lý hệ tài nguyên trang bị và vật phẩm thả rơi trên mặt trận game.
Gồm nhóm Quả cầu Y tế, Trái bom nổ diện và hiệu ứng ngọn chớp nổ tương ứng.
"""

class ExplosionSprite(pygame.sprite.Sprite):
    """
    Trình đồ họa phân tán hiệu ứng vụ nổ diện đặc biệt (Explosion Graphical Effect).
    Hệ thống làm mờ và giới hạn thời gian Timeout giúp thu hồi giải phóng dữ liệu theo chu kì quy định. Thời điểm
    tới hạn sẽ kill().

    Attributes:
        pos (list[float]): Vector thiết lập cắm góc trên phần trái khung tranh chiếu.
        radius (float): Bán kính chấn động và giãn nở.
        duration (int): Thời lượng Timeout tối đa cho phép hiển thị cháy (Thường là 400 mili-giây).
    """
    def __init__(self, pos, radius):
        """
        Nạp giao diện, scale và thả đồ họa mảnh vỡ nổ lửa.

        Args:
            pos (tuple/list): Tâm quy chiếu nơi diễn ra tai nạn.
            radius (float): Bán kính để phóng to và căn tỉ lệ vòng tròn ngọn lửa.
        """
        super().__init__()
        # self.pos lưu tọa độ góc trên bên trái để khi blit ở main.py sẽ nằm đúng vị trí trung tâm vụ nổ
        self.pos = [pos[0] - radius, pos[1] - radius]
        self.radius = radius
        try:
            self.image = pygame.transform.scale(pygame.image.load("assert/bomb/explosion.png").convert_alpha(), (radius*2, radius*2))
        except:
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 0, 150), (radius, radius), radius)
        
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 400 # 400ms duration
        self.alive = True
        
    def update(self, tDelta):
        """
        Đồng bộ hàm Delta Time kiểm kê vòng lặp. Còi báo đếm ngược Time-to-Live sẽ ra lệnh tự đứt 
        nếu thời gian bám trên màn hình quá ranh giới.

        Args:
            tDelta (float): Sai số thời điểm cập nhật logic máy chủ so với màn hình.
        """
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

class Bomb(pygame.sprite.Sprite):
    """
    Class quản trị Cỗ máy kíp nổ chậm Bomb TNT đứng rải rác ngoài đấu trường.
    Bom chịu một thanh định mức tấn công của người chơi (4 Hit), khi tới mốc giới hạn, nó
    kết tủa tạo sát thương hủy diệt các sinh mệnh quái vật và thả mù hạt mảnh diện rộng chói lòa.

    Attributes:
        health (int/float): Điểm giới hạn giáp bom đạn trước khi quá tải nổ banh xác.
        blast_radius (int): Thiết bị Tầm kích lan tỏ chấn động vùng rộng trên bản đồ.
    """
    def __init__(self, pos):
        """
        Chuẩn bị khung, nhúng biểu đồ trạng thái tĩnh và tích hợp cọc tính sinh khí độ bền Bom.

        Args:
            pos (tuple): Tọa độ địa chấn đặt rương rải rác trên màn.
        """
        super().__init__()
        self.pos = list(pos)
        self.radius = 20
        
        # Thêm hiển thị hình đồ họa cho bom
        try: 
            self.image = pygame.transform.scale(pygame.image.load("assert/bomb/bomb.png").convert_alpha(), (self.radius * 2, self.radius * 2))
        except: 
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (30, 30, 30), (self.radius, self.radius), self.radius)
            pygame.draw.circle(self.image, (255, 100, 0), (self.radius, self.radius), self.radius, 3)
            try: font = pygame.font.Font(None, 24)
            except: font = pygame.font.sysfont.SysFont(None, 24)
            text = font.render('B', True, (255, 150, 0))
            text_rect = text.get_rect(center=(self.radius, self.radius))
            self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect(center=self.pos)
        self.health = 4 
        self.max_health = 4
        self.blast_radius = 70 
        self.alive = True
        
    def explode(self, enemies, Projectile_module):
        """
        Chu trình xử lý kích nổ bạo lực khi thanh độ bền gãy ngang: 
        1. Gọi đồ họa vùng trung tâm sinh nhiệt độ rực lửa. Phân vút các đốm hạt cháy tóe tàn (40 Particles).
        2. Dò quỹ tích, bào mòn Máu quái bị tóm trong miền vòng chấn.

        Args:
            enemies (pygame.sprite.Group): List khoái quái để bị trừ Máu trực tiếp khi hứng bão táp.
            Projectile_module (Mô-đun): Bộ công cụ gọi hệ sinh thái cành đạn/vụn vụt tóe ra làm nền hiệu ứng.
        """
        self.alive = False
        
        # Thêm sprite hiệu ứng vụ nổ
        explosion = ExplosionSprite(self.pos, self.blast_radius)
        Projectile_module.particles.add(explosion)
        
        for i in range(40):
            theta = (i / 40) * math.pi * 2
            speed = 5
            p_vel = (math.cos(theta) * speed, math.sin(theta) * speed)
            particle = Particle(self.pos, p_vel, 400, (255, 150, 0))
            Projectile_module.particles.add(particle)
    
        for enemy in enemies:
            dist = math.hypot(enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1])
            if dist <= self.blast_radius:
                enemy.health -= 5 
                if enemy.health <= 0:
                    enemy.kill()
                    
    def render(self, surface, camera_offset):
        """
        Điêu rập mẫu Texture và Thanh cảnh báo Độ bền ghim nổi. Tối ưu hiệu lực bằng hệ thống lọc khoảng nhìn Culling.

        Args:
            surface (pygame.Surface): Layout kết xuất cửa chớp hình OS.
            camera_offset (list): Cụm tính toán bù dời Edge Panning.
        """
        if not self.alive: return
        screen_pos = (int(self.pos[0] - camera_offset[0]), int(self.pos[1] - camera_offset[1]))
        if -50 < screen_pos[0] < 1250 and -50 < screen_pos[1] < 770:
            surface.blit(self.image, self.image.get_rect(center=screen_pos))
            bar_w, bar_h = 40, 5
            bx, by = screen_pos[0] - bar_w // 2, screen_pos[1] - self.radius - 12
            pygame.draw.rect(surface, (50, 50, 50), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, (255, 150, 0), (bx, by, bar_w * (max(0, self.health) / self.max_health), bar_h))

class HealthOrb(pygame.sprite.Sprite):
    """
    Viên cầu Cứu thương khẩn năng lượng (Health Orb).
    Linh dược chữa lành hỗ trợ người dùng bị suy kiệt khi va vào rớt ra nhờ may rủi trong ván quái / đập bình xăng.
    Vẽ nên cảm quan vật lý bay trôi và đục dao động Sin tự nhiên êm ái trên không cực kì chuyên nghiệp.

    Attributes:
        heal_amount (int): Bậc sức khỏe hoàn quy bồi đắp sau sự kiện tiếp nhận chạm viền nhặt.
        bob_time (float): Trọng số nhấp nhô của góc độ toán học hàm Sin dùng phục vụ cơ thể nảy (hovering).
    """
    def __init__(self, pos):
        """
        Dựng hình khối vuông có dấu thập nổi bật đặt tại trục định mệnh. Đợi mồi chài cho lữ khách đạp phải.

        Args:
            pos (tuple[float, float]): Giao điểm rớt mồi đồ.
        """
        super().__init__()
        self.pos = list(pos)
        self.radius = 10
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 50, 100), (self.radius, self.radius), self.radius)
        pygame.draw.rect(self.image, (255, 255, 255), (self.radius - 2, 4, 4, self.radius * 2 - 8))
        pygame.draw.rect(self.image, (255, 255, 255), (4, self.radius - 2, self.radius * 2 - 8, 4))
        
        self.rect = self.image.get_rect(center=self.pos)
        self.bob_time = 0
        self.heal_amount = 1

    def update(self, tDelta):
        """
        Đẩy tiến trình đồng hồ sóng toán học tăng tốc độ đục Sin đều đặn vòng chu kì.

        Args:
            tDelta (float): Máy nhịp độ chênh lệch thời gian máy tinh/khung hình.
        """
        self.bob_time += tDelta * 0.1
        
    def render(self, surface, camera_offset):
        """
        Nâng trôi đối tượng vào khoảng đồ họa kèm một biến rung lắc trục dọc theo phép tính nhấp nhổ Wave Math.

        Args:
            surface (pygame.Surface): Thảm phẳng mặt canvas xuất file đồ họa.
            camera_offset (list): Nhóm công thức Offset Panning nhìn rộng.
        """
        bob_offset = math.sin(self.bob_time) * 5
        screen_pos = (int(self.pos[0] - camera_offset[0] - self.radius), 
                      int(self.pos[1] - camera_offset[1] - self.radius + bob_offset))
        surface.blit(self.image, screen_pos)