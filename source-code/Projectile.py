import pygame

"""
Module chuyên trị khía cạnh đường đạn động học (Projectiles) và Hiệu ứng tàn dư lửa (Particles).
Thay vì tạo file âm thanh và khói phức tạp, áp dụng vẽ đồ họa Surface đơn nguyên Pygame 
để tăng tốc độ quét khung Game, cho phép nã hỏa lực chằng chịt mà không bị Lag giật.
"""

class Particle(pygame.sprite.Sprite):
    """
    Lớp cấu thành các mảnh vụn nhỏ (VFX Particle Effect).
    Sử dụng để nhả các luồng đốm li ti đuổi vệt sáng đằng sau đầu các viên đạn 
    hoặc khi có chấn động đánh bom cực mạnh (Particle explosion).
    Lớp đối tượng được lập trình có chu kì mờ nhạt dần theo thời lượng sống bằng mã Alpha fade out.

    Attributes:
        pos (list): Khoảng không ghi hình giọt hạt vụn nhấp nháy.
        velocity (tuple[int]): Lực văng dư nén (X,Y) đẩy trôi các hạt bụi ra đằng sau.
        lifetime (int): Giai doạn Time-to-Live tàn rỗng của mảnh hạt trước dập tắt (MilliSeconds).
        createdAt (int): Khoảng mốc Timeline Timestamp đính ấn chỉ ngày chào đời đốm nổ để tính vòng Fade.
    """
    def __init__(self, pos, velocity, lifetime, color):
        """Khởi tạo thực điểm mảnh hạt với vận lượng, quy chế sinh và mã Alpha hòa sương."""
        super().__init__()
        size = 3
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        
        self.pos = list(pos)
        self.velocity = velocity
        self.lifetime = lifetime
        self.createdAt = pygame.time.get_ticks()
        self.rect = self.image.get_rect(x=pos[0], y=pos[1])
        
    def update(self, tDelta):
        """
        Cập nhật chuyển động tịnh tiệm trôi nổi rơi, song song trượt bộ điều chỉnh vặn nhỏ độ mờ ảnh tĩnh Alpha xuống thấp.
        Sẽ tực xóa nát rác đối tượng khỏi bộ nhớ RAM khi kết dứt LifeTime.

        Args:
            tDelta (float): Bộ chỉ số sai biến thời gian (Time Delta) bù đáp lỗi trượt cấu hình khung vi lặp.
        """
        elapsed = pygame.time.get_ticks() - self.createdAt
        if elapsed > self.lifetime:
            self.kill()
            return
        self.pos[0] += self.velocity[0] * tDelta * 0.3
        self.pos[1] += self.velocity[1] * tDelta * 0.3
        self.rect.topleft = self.pos
        alpha = int(255 * (1 - elapsed / self.lifetime))
        self.image.set_alpha(max(0, alpha))

class Projectile(pygame.sprite.Sprite):
    """
    Thực thể Đầu Đạn Đại Bác (Đại diện chung cho nhóm Đạn của Người Cầm Trịch lẫn Quái Thú).
    Xác tác quỹ đạo và quán sát đụng dập lên vỏ thân thể quái vật. Phân chia logic tự đùn vệt hạt lửa khói.

    Attributes:
        particles (pygame.sprite.Group): Group chứa tập tàn dư mảnh bụi do đạn bắn rớt lại trên thân luồng sau.
        speed (float): Tốc lượng gia tốc định biên diệt của viên đạt vút đo lường/ticks.
        lifetime (int): Số khung giờ mili-giây đạn giới hạn tồn tại để tự phá nát trên đường văng xa ranh.
        is_player (bool): Tham chiếu Nhãn phe Ta và Địch nhằm loại bỏ rủi ro bắn nhầm phe lính tráng (Friendly Fire Guard).
    """
    particles = pygame.sprite.Group()
    def __init__(self, source, direction, speed, lifetime, color, is_player=False):
        """Nhả xả ngọn đạn tại một trọng điểm trỏ với Vector đâm đầu nhất định."""
        super().__init__()
        self.image = pygame.Surface([8, 8], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=source)
        pygame.draw.circle(self.image, color, (4, 4), 4)
        
        self.pos, self.movementVector = list(source), list(direction)
        self.speed, self.lifetime, self.color = speed, lifetime, color
        self.createdAt = pygame.time.get_ticks()
        self.last_particle_time = pygame.time.get_ticks()
        self.is_player = is_player
        
    def move(self, surfaceSize, tDelta):
        """
        Di dời viên đạn tịnh tiến thẳng theo vector. Đồng thời xử lý rải hạt dư.
        
        Args:
            surfaceSize (tuple): Cấp hạn chớp dời điểm cự tối đa nới màn để phát nổ đầu đạn khi vượt quá ốc góc độ Camera.
            tDelta (float): Denta bộ canh nhịp Frame game phòng rủi bị lag FPS.
        """
        if pygame.time.get_ticks() > self.createdAt + self.lifetime:
            self.kill()
            return
            
        self.pos[0] += self.movementVector[0] * self.speed * tDelta
        self.pos[1] += self.movementVector[1] * self.speed * tDelta
        self.rect.center = self.pos
        
        if pygame.time.get_ticks() - self.last_particle_time > 25:
            self.last_particle_time = pygame.time.get_ticks()
            p_vel = (-self.movementVector[0] * self.speed * 0.2, -self.movementVector[1] * self.speed * 0.2)
            Projectile.particles.add(Particle(self.pos, p_vel, 150, self.color))
            
        if not (-100 < self.pos[0] < surfaceSize[0] + 100) or not (-100 < self.pos[1] < surfaceSize[1] + 100):
            self.kill()
