import json
import os
from datetime import datetime
 
"""
Module cung cấp khung tư duy quản trị Hệ thống Điểm kỷ lục (High Score).
Cho phép xử lý đọc, lưu trữ tệp dạng JSON và tính toán trích xuất danh sách 10 điểm cao nhất.
"""

class HighScoreManager:
    """
    Trình biên dịch và quản lý thông tin Điểm cao lịch sử cục bộ.
    Vá thông tin qua bộ tệp chuỗi JSON, quá trình load, ghi đè, và theo dõi
    thứ hạng xếp hạng Top 10 của game được lưu hành bề vững.

    Attributes:
        filename (str): Tên File lưu trữ hồ sơ (Mặc định: "highscores.json")
        scores (list[dict]): Bộ nhớ truy cập RAM lưu số liệu cụm Dictionary (Tên, Điểm, Ngày).
    """
    def __init__(self, filename="highscores.json"):
        """
        Nạp cấu hình cho trình quản lý máy chủ lưu HighScore, xác định bộ trỏ File path 
        và đẩy dữ liệu từ Disk vào Mem để tăng tốc đọc/ghi.
        
        Args:
            filename (str, optional): Tên tùy chọn khai báo nguồn cơ sở tập tin. Mặc định dùng "highscores.json".
        """
        self.filename = filename
        self.scores = self.load_scores()
    
    def load_scores(self):
        """
        Kiểm tra trạng thái đường dẫn tệp tin trên CSDL cục bộ và phân phối về mảng (Tải lại phiên cũ).
        Có bẫy biệt lệ an toàn, nếu hỏng định dạng (Invalid JSON) sẽ tự dọn và khơi nguồn bằng mảng rỗng.

        Returns:
            list[dict]: Array lịch sử chiến tích. (Trả mảng rỗng [] nếu lỗi hoặc chưa có file). 
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        """
        Mở kênh Ghi (Write) tới tệp tin Database tĩnh. 
        Xả toàn bộ thư mục bộ đệm và ghi đè xuống Storage bằng hàm phân tích JSON. 
        Đảm bảo giữ vững định dạng UTF-8 nhằm tránh lỗi Text có dấu.
        """
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, indent=4, ensure_ascii=False)
    
    def add_score(self, score, player_name="Player"):
        """
        Tiếp nhận và đẩy thông số 1 thành tích cá nhân vào Cỗ máy xếp hạng bảng danh dự.
        Tự lập Timestamp (Ngày/giờ đạt ấn chỉ), kết hợp thuật toán sắp xếp độ vĩ đại (Điểm lớn đứng đầu).
        Sau cùng thực hiện xén ngọn (Slice Slice[10]) triệt tiêu phần dư thừa ngoài top.

        Args:
            score (int): Thành tích số điểm quái rơi kết màn.
            player_name (str, optional): Ký tự chuỗi nhân danh. Mặc định là "Player".
        """
        entry = {
            "name": player_name,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.scores.append(entry)
    
        self.scores.sort(key=lambda x: x["score"], reverse=True)
   
        self.scores = self.scores[:10]
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        """
        Truy xuất nhóm Cột mốc điểm tinh xảo nhất dùng cho giao diện trình chiếu GUI Sảnh menu.

        Args:
            limit (int, optional): Giới hạn dòng cần xuất ra màn. Mặc mặc định hiển thị 10 hạng tử.

        Returns:
            list[dict]: Nhóm Object bản thành tích từ cao tới bét.
        """
        return self.scores[:limit]
    
    def is_high_score(self, score):
        """
        Hàm xác minh Logic xem điểm số kết sổ có đủ phẩm chất đánh lọt vào Bảng Vinh Danh không 
        (Từng dùng để kích hoạt tính năng nhập Tên màn Game Over).

        Args:
            score (int): Tổng lượng điểm gom được ván qua.

        Returns:
            bool: Tích cực (True) nếu đủ chuẩn bứt phá top, Tiểu cực (False) nếu là số điểm hẻo.
        """
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]["score"]
    
    def get_rank(self, score):
        """
        Thuật toán ướm tính xem cá nhân nắm cự ly điểm này sẽ trụ vững ở hàng ngai thứ bao nhiêu.
        
        Args:
            score (int): Tham số đánh giá số liệu.

        Returns:
            int: Nhãn định danh Index hạng kế tiếp (Vd: số 1 tức hạng 1, v.v..).
        """
        for i, entry in enumerate(self.scores):
            if entry["score"] <= score:
                return i + 1
        return len(self.scores) + 1