import pygame
import random
import math
from Projectile import Projectile
from Utils import normalize_vector, rotate_vector

"""
Module quản lý hệ thống vũ khí (Weapon) trong trò chơi.
Bao gồm kiến trúc vũ khí cơ sở và các biến thể súng đạn đa dạng như Pistol, Shotgun, Machine Gun.
"""

class Weapon:
    """
    Lớp cơ sở (Base Class) định nghĩa cấu trúc của một vũ khí chung.
    Gồm tham chiếu thời điểm xả đạn (Cooldown Management) và hàm bắn trừu tượng.
    """
    def __init__(self):
        """Khởi tạo biến kiểm soát tần suất bắn."""
        self.lastShot = 0
        
    def shoot(self, user, mousePos): 
        """
        Khung hàm khai hỏa. Yêu cầu các lớp súng cụ thể (Lớp con) phải ghi đè (override) 
        để tạo logic đường đạn tản mát phân biệt.
        """
        pass

class Pistol(Weapon):
    """
    Súng lục (Pistol) - Vũ khí mặc định, cấp 1.
    Bắn ra một tia đạn đơn, nhịp độ xả súng vừa phải và có độ chính xác tuyến tính 100%.
    Dùng cho các mục tiêu đơn mục tiêu tầm xa.
    
    Attributes:
        weaponCooldown (int): Chu kỳ dãn cách tối thiểu giữa 2 lần khai hỏa (250ms).
    """
    def __init__(self):
        super().__init__()
        self.weaponCooldown = 250
        
    def shoot(self, user, mousePos):
        """
        Thực thi cơ chế nhả đạn đơn. Tính toán vector hướng chuẩn xác 
        từ vị trí nhân vật vạch trỏ thẳng về điểm ảnh chỉ định của chuột điện tử.
        """
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastShot > self.weaponCooldown:
            direction = (mousePos[0] - user.pos[0], mousePos[1] - user.pos[1]) if mousePos != tuple(user.pos) else (1, 1)
            self.lastShot = currentTime
            user.projectiles.add(Projectile(user.pos, normalize_vector(direction), 5, 2000, (0, 255, 0), is_player=True))
            
class Shotgun(Weapon):
    """
    Súng Hoa cải / Súng Đoản (Shotgun) - Vũ khí cấp 2.
    Phóng ra một lượng lớn hạt đạn kim quạt đa điểm cùng một lúc.
    Sát thương hủy diệt ở điểm chạm gần nhưng Cooldown nạp đạn lại rất chậm trễ.
    
    Attributes:
        weaponCooldown (int): Cooldown thời gian nghỉ ngắt quãng giữa các làn khói (750ms).
        spreadArc (int): Độ mở rộng của góc Quạt tản đạn (Đo bằng góc độ 90).
        projectilesCount (int): Số lượng hạt văng mảnh xuất trảo song song.
    """
    def __init__(self):
        super().__init__()
        self.weaponCooldown = 750
        self.spreadArc = 90
        self.projectilesCount = 7
        
    def shoot(self, user, mousePos):
        """
        Thực thi xả đạn tản sương cục diện. 
        Mảng đường đạn được rẽ quạt dựa vào hàm quy đổi góc lệch (rotate_vector) 
        chia độ đều theo từng nấc cung Arc cố định.
        """
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastShot > self.weaponCooldown:
            direction = (mousePos[0] - user.pos[0], mousePos[1] - user.pos[1]) if mousePos != tuple(user.pos) else (1, 1)
            self.lastShot = currentTime
            arcDifference = self.spreadArc / (self.projectilesCount - 1)
            for proj in range(self.projectilesCount):
                theta = math.radians(arcDifference*proj - self.spreadArc/2)
                projDir = rotate_vector(direction, theta)
                user.projectiles.add(Projectile(user.pos, normalize_vector(projDir), 7, 500, (0, 255, 0), is_player=True))
                
class MachineGun(Weapon):
    """
    Súng Máy Tự động (Machine Gun) - Vũ khí cấp 3.
    Xả lượng đạn liên thanh tới tấp nhằm càn quét trận địa.
    Kèm tác dụng phụ giật nòng dẫn tới việc quỹ đạo bay của đạn là một biến số nhiễu lộn xộn.
    
    Attributes:
        weaponCooldown (int): Nhịp độ nhả đạn liên tục cường độ cao (150ms).
        spreadArc (int): Giới hạn giới biên dao động độ giật nòng hãm (25 độ lệch).
    """
    def __init__(self):
        super().__init__()
        self.weaponCooldown = 150
        self.spreadArc = 25
        
    def shoot(self, user, mousePos):
        """
        Phóng đạn liên thanh và cấp ma trận random() vào tham số góc theta để
        phát tác độ rít, độ sai số (Inaccuracy / Recoil Effect) cho dòng đạn bão.
        """
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastShot > self.weaponCooldown:
            direction = (mousePos[0] - user.pos[0], mousePos[1] - user.pos[1]) if mousePos != tuple(user.pos) else (1, 1)
            self.lastShot = currentTime
            theta = math.radians(random.random()*self.spreadArc - self.spreadArc/2)
            projDir = rotate_vector(direction, theta)   
            user.projectiles.add(Projectile(user.pos, normalize_vector(projDir), 6, 1000, (0, 255, 0), is_player=True))