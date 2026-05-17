from datetime import datetime, timedelta

class HomeService:
    """Dịch vụ quản lý dữ liệu cho Trang chủ: Lịch học, Nhiệm vụ, Thống kê và Thông báo."""
    def __init__(self):

        # Lịch học theo từng ngày trong tuần (7 ngày)
        self.schedule = []
        for i in range(7):
            day_name = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"][i]
            self.schedule.append({
                "day": day_name,
                "date": "", # Sẽ được tính động
                "sessions": []
            })
        
        # Dữ liệu mẫu (có thể gán lại theo ngày)
        self.schedule[0]["sessions"] = [
            {"start": "07:00", "end": "09:30", "subject": "Thiết kế web (9)_TA", "room": "K.A215", "type": "LT"},
            {"start": "10:00", "end": "12:00", "subject": "Kiến trúc máy tính (1)_TA", "room": "K.A212", "type": "LT"},
        ]
        self.schedule[1]["sessions"] = [
            {"start": "08:00", "end": "10:30", "subject": "Tiếng Anh 2 (18)", "room": "K.B102", "type": "LT"},
            {"start": "13:00", "end": "16:00", "subject": "Lập trình Python (1)_TA", "room": "K.A312", "type": "LT"},
        ]
        self.schedule[2]["sessions"] = [
            {"start": "07:00", "end": "09:30", "subject": "GDTC 2 (Bóng chuyền) (5)", "room": "Sân bóng chuyền", "type": "TT"},
        ]
        self.schedule[3]["sessions"] = [
            {"start": "13:00", "end": "16:00", "subject": "Tiếng Anh chuyên ngành 2 (IT) (9)", "room": "K.B102", "type": "LT"},
        ]
        self.schedule[4]["sessions"] = [
            {"start": "13:00", "end": "16:00", "subject": "Cấu trúc dữ liệu và giải thuật (9)_TA", "room": "K.A313", "type": "LT"},
            {"start": "18:00", "end": "19:30", "subject": "Tự học - Ôn tập cuối tuần", "room": "Thư viện", "type": "TH"},
        ]
        self.schedule[5]["sessions"] = [
            {"start": "07:00", "end": "09:30", "subject": "Đại số tuyến tính (9)_TA", "room": "K.A212", "type": "LT"},
            {"start": "15:00", "end": "16:30", "subject": "Khởi nghiệp và đổi mới sáng tạo (9)", "room": "K.A110", "type": "LT"},
        ]

        self.tasks = [
            {"name": "Nộp bài tập Lập trình Python", "tag": "K.A312", "deadline": "23:59 hôm nay", "done": False},
            {"name": "Ôn tập Tiếng Anh 2", "tag": "K.B102", "deadline": "20:30", "done": False},
            {"name": "Đọc tài liệu Kiến trúc máy tính", "tag": "K.A212", "deadline": "21:00", "done": False},
            {"name": "Làm đề thi Cấu trúc dữ liệu", "tag": "K.A313", "deadline": "22:00", "done": False},
        ]

        self.stats = {
            "total_sessions": "28",
            "self_study_hours": "12h",
            "completion": 0.85
        }

        self.notifications = [
            {"text": "Lịch học K.A215 đã được cập nhật", "time": "2 giờ trước"},
            {"text": "Có 3 đề thi mới được thêm vào", "time": "5 giờ trước"},
            {"text": "AI đã tạo kế hoạch học tập mới", "time": "1 ngày trước"},
        ]

    def get_schedule(self, week_offset=0):
        """Tính toán và trả về danh sách lịch học theo tuần dựa trên độ lệch (offset) tuần."""
        # Tính toán ngày dựa trên offset tuần
        today = datetime.now()
        monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        
        updated_schedule = []
        for i, item in enumerate(self.schedule):
            new_item = item.copy()
            d = monday + timedelta(days=i)
            new_item["date"] = d.strftime("%d/%m/%Y")
            updated_schedule.append(new_item)
            
        return updated_schedule

    def get_tasks(self):
        """Lấy danh sách các nhiệm vụ học tập hiện tại."""
        return self.tasks

    def get_stats(self):
        """Lấy dữ liệu thống kê kết quả học tập trong tuần."""
        return self.stats

    def get_notifications(self):
        """Lấy danh sách các thông báo mới nhất."""
        return self.notifications

    def add_task(self, task_data):
        """
        Xử lý thêm nhiệm vụ mới. 
        Sau này bạn Backend sẽ viết code lưu vào database ở đây.
        """
        print(f"Service nhận dữ liệu nhiệm vụ: {task_data}")
        # Tạm thời chỉ append vào list mẫu
        self.tasks.append(task_data)
        return True

    def add_schedule(self, schedule_data):
        """
        Xử lý thêm lịch học mới.
        Sau này bạn Backend sẽ viết code lưu vào database ở đây.
        """
        print(f"Service nhận dữ liệu lịch học: {schedule_data}")
        # Logic xử lý lưu trữ sẽ ở đây
        return True

    def get_study_suggestions(self):
        """AI phân tích dữ liệu và đưa ra lời khuyên học tập ngắn gọn."""
        return "Bạn có 2 môn thi tuần tới. AI gợi ý ưu tiên ôn tập Tiếng Anh 2 và Cấu trúc dữ liệu trước."
