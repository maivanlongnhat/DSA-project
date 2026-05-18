import pygame
import random
import os

screen_size = (1200, 720)
map_size = (1200, 720)
edge_threshold = 30
camera_speed = 8

"""
Module phụ trách mảng Cấu hình bề nổi Địa lý, gồm Hệ thống Bản đồ (Map), phông nền và cụm chướng ngại vật cứng.
"""

class Obstacles(pygame.sprite.Sprite):
    """
    Lớp chuẩn cấu trúc Đại diện cho Cụm các rào cản vật lý (Chướng ngại vật).
    Kỹ nghệ thiết kế phân li Vùng Vẽ (Image) và Vùng Va chạm (Hitbox).
    Việc làm hẹp dẹt Hitbox ở dưới chân giúp mô phỏng ảo giác độ sâu 2.5D, cho phép Sprite khác núp dần vào phía sau và di chuyển mượt mà hơn.

    Attributes:
        rect (pygame.Rect): Khung hộp chữ nhật ôm chọn cả khối hình họa hiển thị đồ.
        hitbox (pygame.Rect): Khung hộp chữ thu nhỏ cắm cọc ở rễ vật phẩm làm chức trách chặn lối cứng. 
        type (str): Kiểu cách phân loại nhận diện.
    """
    def __init__(self, rect, obstacle_type, img_file):
        """
        Thiết kế hình mẫu tổng quản trước khi dán bộ giáp Skin lên khung mô phỏng xương.

        Args:
            rect (tuple|list): Parameter độ lớn móng (x, y, Rộng, Cao).
            obstacle_type (str): Bộ phân tách thể chất ('rock', 'tree').
            img_file (str): Vector trỏ dẫn file PNG bộ cài tài nguyên tranh ảnh tĩnh.
        """
        super().__init__()
        self.rect = pygame.Rect(rect)
        self.type = obstacle_type
    
        original_image = pygame.image.load(img_file).convert_alpha()
        self.image = pygame.transform.scale(original_image, (self.rect.width, self.rect.height))

        hitbox_width = self.rect.width * 0.5
        hitbox_height = self.rect.height * 0.4
        self.hitbox = pygame.Rect(
            self.rect.centerx - hitbox_width / 2,
            self.rect.bottom - hitbox_height,
            hitbox_width,
            hitbox_height
        )

class Rock(Obstacles):
    """
    Biến thể nhánh Chướng ngại vật Đá vôi / Tinh thể nguyên khối.
    Chủ trương mở rộng bè ngang cho Hitbox vì Đá có khung thể chất lùn và tản rộng hơn so với bóng cây cổ thụ.
    """
    def __init__(self, rect, img_file=None):
        """
        Ráp khối thạch nhũ và override chèn ép lại tỉ số Hitbox của đối tượng gốc Obstacle.
        """
        super().__init__(rect, obstacle_type='rock', img_file=img_file)
        hb_width = self.rect.width * 0.8
        hb_height = self.rect.height * 0.6
        self.hitbox = pygame.Rect(
            self.rect.centerx - hb_width / 2,
            self.rect.bottom - hb_height,
            hb_width,
            hb_height
        )

class Tree(Obstacles):
    """
    Biến thể nhánh cấu trúc Lâm nghiệp Cây xanh che bóng.
    Tận dụng trực tiếp định chuẩn hitbox gầy, cao của Lớp Cha nhằm tối thiểu công rườm rà đổi dời.
    """
    def __init__(self, rect, img_file=None):
        """
        Gieo mầm Cây cối tại vị trí cố định.
        """
        super().__init__(rect, obstacle_type='tree', img_file=img_file)

class Map:
    """
    Xử lý mảng phối cảnh toàn thể cục bộ: 
    Giữ các giá trị thông số ranh giới thế giới mở ảo.

    Attributes:
        width, height (int): Nới lỏng không gian hoạt thể của vòng thế giới so với cửa sổ render.
        obstacles (pygame.sprite.Group): Biến phân chia đếm tất cả ngọn chướng ngại nhằm xét va chạm logic.
        camera_offset (list[int]): Biến Panning dời tọa [x, y], khóa biên vùng chết.
    """
    def __init__(self, size):
        """
        Xây dựng vùng đất, xây dựng rừng cây và tinh thạch tại tọa độ cố định.

        Args:
            size (tuple[int, int]): Tọa độ (Chiều ngang, Chiều dọc) tuyệt đối cho khuôn viên sinh thái lớn.
        """
        self.width, self.height = size 
        self.obstacles = pygame.sprite.Group() 
        self.camera_offset = [0, 0] 
        
        self.bg_image = None
        bg_path = '_internal/assert/background.png' 
        if os.path.exists(bg_path):
            img = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(img, (self.width, self.height))
        
        xmastree_w, xmastree_h = 75, 75
        christmas_coords = [(242, 70), (94, 292), (303, 474), (357, 418)]
        for x, y in christmas_coords:
            self.obstacles.add(Tree((x, y, xmastree_w, xmastree_h), img_file='_internal/assert/tree/christmas_tree.png'))

        palmtree_w, palmtree_h = 75, 75
        palm_coords = [
            (626, 195), (626, 355), (741, 28), (808, 474), 
            (741, 522), (1172, 522), (842, 195), (909, 139), 
            (1010, 418), (1077, 474), (1118, 70), (1172, 195)
        ]
        for x, y in palm_coords:
            self.obstacles.add(Tree((x, y, palmtree_w, palmtree_h), img_file='_internal/assert/tree/palm_tree.png'))

        brokentree_w, brokentree_h = 40, 40
        broken_coords = [(120, 100), (242, 300), (418, 111)]
        for x, y in broken_coords:
            self.obstacles.add(Tree((x, y, brokentree_w, brokentree_h), img_file='_internal/assert/tree/broken_tree.png'))

        mosstree_w, mosstree_h = 75, 75
        moss_coords = [(1100, 650)]
        for x, y in moss_coords:
            self.obstacles.add(Tree((x, y, mosstree_w, mosstree_h), img_file='_internal/assert/tree/moss_tree.png'))

        red_crystal_w, red_crystal_h = 30, 30
        red_crystal_coords = [(780, 450)]
        for x, y in red_crystal_coords:
            self.obstacles.add(Rock((x, y, red_crystal_w, red_crystal_h), img_file='_internal/assert/rock/red_crystal.png'))

    def render(self, surface):
        """
        Trình kết xuất Render nhúng màu sắc môi trường và lót tranh tĩnh đồ chướng ngại vật lên vòm mắt chiếu màn hình thật.
        Này tích hợp bộ Culling tự hủy: Các thành tố lọt vào vùng điểm mù Camera bị từ chối vẽ nhằm nhẹ hóa vi xử lý GPU.

        Args:
            surface (pygame.Surface): Cửa số hiện đồ chính thức Pygame.
        """
        if self.bg_image:
            surface.blit(self.bg_image, (-self.camera_offset[0], -self.camera_offset[1]))
        else:
            surface.fill((20, 20, 30)) 
            
        for obstacle in self.obstacles:
            screen_x = obstacle.rect.x - self.camera_offset[0] 
            screen_y = obstacle.rect.y - self.camera_offset[1] 

            if -200 < screen_x < screen_size[0] + 200 and -200 < screen_y < screen_size[1] + 200: 
                surface.blit(obstacle.image, (screen_x, screen_y)) 

    def get_obstacles(self):
        """
        Hàm cung cấp chốt truy cập nhóm tĩnh.

        Returns:
            pygame.sprite.Group: Nhóm toàn quyền chướng ngại vật (Gốc cây, Khối đá..).
        """
        return self.obstacles 
    
    def update(self):
        """
        Gọi thăm dò tín hiệu Chuột máy tính Edge Panning (Đẩy trôi viền):
        Nếu người xem lia chuột chạm rìa cửa sổ, camera sẽ chủ động dịch sang khu vực bản đồ liền dề bên.
        Tự khoanh vùng phanh hãm nhằm tránh tuột ngõ kẹp xa hơn cấu trúc Map biên giới.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos() 
        if mouse_x < edge_threshold: 
            self.camera_offset[0] -= camera_speed 
        elif mouse_x > screen_size[0] - edge_threshold: 
            self.camera_offset[0] += camera_speed 
        if mouse_y < edge_threshold: 
            self.camera_offset[1] -= camera_speed 
        elif mouse_y > screen_size[1] - edge_threshold: 
            self.camera_offset[1] += camera_speed 
        
        self.camera_offset[0] = max(0, min(self.camera_offset[0], self.width - screen_size[0]))
        self.camera_offset[1] = max(0, min(self.camera_offset[1], self.height - screen_size[1]))