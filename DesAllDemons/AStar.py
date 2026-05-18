import math
import heapq
from Map import map_size

"""
Module phân tích không gian và tìm đường A* (A-Star).
"""

# Tối ưu: Tạo Grid tĩnh một lần để không phải check collision Pygame liên tục
GRID_SIZE = 50
COLS = int(map_size[0] // GRID_SIZE) + 1
ROWS = int(map_size[1] // GRID_SIZE) + 1
nav_grid = []

def init_nav_grid(obstacles, enemy_radius):
    """
    Khởi tạo lưới tìm đường (navigation grid) tĩnh để hỗ trợ tính toán phương hướng cho A*.
    Mỗi ô lưu trữ trạng thái Boolean, cho phép đi (True) hoặc bị chặn (False).

    Args:
        obstacles (list[pygame.sprite.Sprite]): Danh sách các chướng ngại vật vật lý trên bản đồ.
        enemy_radius (float): Bán kính bao quanh kẻ địch. Được sử dụng để tạo một lớp đệm (padding) 
                              đảm bảo chúng không bị kẹt sát viền hoặc đi xuyên vách đối tượng.
    """
    global nav_grid
    nav_grid = [[True for _ in range(ROWS)] for _ in range(COLS)]
    padding = enemy_radius * 0.8  # Giới hạn viền tường
    
    for x in range(COLS):
        for y in range(ROWS):
            gx = x * GRID_SIZE + GRID_SIZE / 2
            gy = y * GRID_SIZE + GRID_SIZE / 2
            for obs in obstacles:
                if (gx + padding > obs.rect.left and gx - padding < obs.rect.right and 
                    gy + padding > obs.rect.top and gy - padding < obs.rect.bottom):
                    nav_grid[x][y] = False
                    break

def heuristic(a, b):
    """
    Hàm đo lường chi phí (Cost) dự kiến từ điểm đang xét đến mục tiêu.
    Sử dụng công thức khoảng cách Euclide (Đường thẳng nối 2 điểm).

    Args:
        a (tuple[int, int]): Tọa độ (x, y) trên lưới điểm xét duyệt hiện tại.
        b (tuple[int, int]): Tọa độ (x, y) trên lưới cho điểm đích đến.

    Returns:
        float: Giá trị khoảng cách tuyến tính giữa 2 khu vực.
    """
    return math.hypot(b[0] - a[0], b[1] - a[1])

def a_star_search(start_pos, goal_pos):
    """
    Triển khai thuật toán định tuyến đồ thị A* (A-Star) thông qua Navigation Grid.
    Từ tọa độ vật lý (pixel), hàm ánh xạ về tọa độ dạng lưới (Mesh Grid), tìm lộ trình 
    có phi chí thấp nhất rồi nội suy ngược trả lại tọa độ pixel.

    Args:
        start_pos (tuple[float, float]): Tọa độ thực của kẻ địch (Gốc xuất phát).
        goal_pos (tuple[float, float]): Tọa độ thực của Người chơi (Mục tiêu chốt).

    Returns:
        list[tuple[float, float]]: Kết xuất danh sách lộ trình theo tọa độ đồ họa điểm (Pixel Waypoints). 
                                   Nếu bị chặn tắc ngõ, hàm sẽ trả về mảng rỗng [].
    """
    global nav_grid
    if not nav_grid: return []
    
    start_grid = (int(start_pos[0] // GRID_SIZE), int(start_pos[1] // GRID_SIZE))
    goal_grid = (int(goal_pos[0] // GRID_SIZE), int(goal_pos[1] // GRID_SIZE))
    
    start_grid = (max(0, min(COLS-1, start_grid[0])), max(0, min(ROWS-1, start_grid[1])))
    goal_grid = (max(0, min(COLS-1, goal_grid[0])), max(0, min(ROWS-1, goal_grid[1])))

    frontier = []
    heapq.heappush(frontier, (0, start_grid))
    came_from = {start_grid: None}
    cost_so_far = {start_grid: 0}
    
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best_node = start_grid
    min_h = heuristic(start_grid, goal_grid)
    
    iterations = 0
    while frontier and iterations < 800:
        iterations += 1
        _, current = heapq.heappop(frontier)
        
        if current == goal_grid:
            best_node = current
            break
            
        h = heuristic(current, goal_grid)
        if h < min_h:
            min_h, best_node = h, current
            
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            
            if 0 <= nx < COLS and 0 <= ny < ROWS and nav_grid[nx][ny]:
                # NGĂN CHẶN CẮT GÓC XUYÊN TƯỜNG KHI ĐI CHÉO
                if dx != 0 and dy != 0:
                    if not nav_grid[current[0]+dx][current[1]] or not nav_grid[current[0]][current[1]+dy]:
                        continue
                        
                next_node = (nx, ny)
                move_cost = 1.414 if dx != 0 and dy != 0 else 1.0
                new_cost = cost_so_far[current] + move_cost
                
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(goal_grid, next_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current
                    
    path = []
    current = best_node
    while current != start_grid and current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    
    return [(node[0]*GRID_SIZE + GRID_SIZE/2, node[1]*GRID_SIZE + GRID_SIZE/2) for node in path]