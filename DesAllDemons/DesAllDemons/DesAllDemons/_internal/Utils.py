import math

"""
Module tiện ích (Utilities).
Cung cấp bộ khung các hàm Toán hình học 2 chiều hỗ trợ xử lý Vector, định quy tọa độ,
chuẩn hóa chiều không gian, đóng vai cốt lõi cho tính năng Di chuyển, Chỉ ngắm đường đạn bay.
"""

def normalize_vector(vector):
    """
    Chuẩn hóa Vector đường chéo đồ họa thành dạng Vector cơ sở (Unit Vector) 
    có độ lớn duy nhất bằng 1 (Magnitude = 1).
    Phép tính rất thiết yếu ngăn chặn rủi ro đi vận tốc đi chéo bị nhân lên quá cao 
    so với đi biên nằm ngang (Diagonal Movement Bug).

    Args:
        vector (list/tuple): Vector đa hướng [x, y] độ lớn vô tận chĩa từ A đến B.

    Returns:
        tuple (float, float): Tổ hợp hướng x, y tịnh tiến có cự tích đơn vị bằng tuyệt đối giới hạn 1. 
                              Trả về (0, 0) nếu biên nằm trúng trục cụt ban đầu.
    """
    if vector == [0, 0] or vector == (0, 0): return (0, 0)
    mag = math.hypot(vector[0], vector[1])
    if mag == 0: return (0, 0)
    return (vector[0] / mag, vector[1] / mag)

def rotate_vector(vector, theta):
    """
    Phép xoay ma trận Vector 2D (2D Vector Rotation Transformation).
    Dựa vào góc Radians nạp vào để nhức vế Vector chóp ngoặt xoay ngang quanh trục trung tâm.
    Dùng chuyên dụng tạo tính năng rải súng đạn chùm (Shotgun) hay tái chế Recoil Spray.

    Args:
        vector (list/tuple): Vector phương diện mốc [x, y].
        theta (float): Góc bẻ lái của chiều Vector bằng giá trị quay Toán Radians (không phải độ Degrees).

    Returns:
        tuple (float, float): Phôi điểm phương hướng sau khi đã được chéo góc xê dịch lệch đi so với tâm ngắm.
    """
    return (
        vector[0] * math.cos(theta) - vector[1] * math.sin(theta),
        vector[0] * math.sin(theta) + vector[1] * math.cos(theta)
    )

def distance(pos1, pos2):
    """
    Kéo thước cuộn đo đạc khoảng cách thực tế giữa hai thực thể cố hữu tọa độ Pixel trên mặt bảng sơ map.
    Áp dụng thuật toán căn bậc hai bình phương tam giác lượng giác Pythagoras.

    Args:
        pos1 (list/tuple/pygame.Vector2): Cục điểm nhắm trúng thứ 1.
        pos2 (list/tuple/pygame.Vector2): Cục điểm nhắm trúng thứ 2.

    Returns:
        float: Giá trị khoảng cách trực tuyến giữa 2 tâm quy mô.
    """
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])