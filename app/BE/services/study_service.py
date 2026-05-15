# app/BE/services/study_service.py

class StudyService:
    def __init__(self):
        # Lịch học theo từng ngày trong tuần
        self.schedule = [
            {
                "day": "Thứ 2", "date": "20/04/2026",
                "sessions": [
                    {"start": "07:00", "end": "09:30", "subject": "Thiết kế web (9)_TA", "room": "K.A215", "type": "LT"},
                    {"start": "10:00", "end": "12:00", "subject": "Kiến trúc máy tính (1)_TA", "room": "K.A212", "type": "LT"},
                ]
            },
            {
                "day": "Thứ 3", "date": "21/04/2026",
                "sessions": [
                    {"start": "08:00", "end": "10:30", "subject": "Tiếng Anh 2 (18)", "room": "K.B102", "type": "LT"},
                    {"start": "13:00", "end": "16:00", "subject": "Lập trình Python (1)_TA", "room": "K.A312", "type": "LT"},
                ]
            },
            {
                "day": "Thứ 4", "date": "22/04/2026",
                "sessions": [
                    {"start": "07:00", "end": "09:30", "subject": "GDTC 2 (Bóng chuyền) (5)", "room": "Sân bóng chuyền", "type": "TT"},
                ]
            },
            {
                "day": "Thứ 5", "date": "23/04/2026",
                "sessions": [
                    {"start": "13:00", "end": "16:00", "subject": "Tiếng Anh chuyên ngành 2 (IT) (9)", "room": "K.B102", "type": "LT"},
                ]
            },
            {
                "day": "Thứ 6", "date": "24/04/2026",
                "sessions": [
                    {"start": "13:00", "end": "16:00", "subject": "Cấu trúc dữ liệu và giải thuật (9)_TA", "room": "K.A313", "type": "LT"},
                    {"start": "18:00", "end": "19:30", "subject": "Tự học - Ôn tập cuối tuần", "room": "Thư viện", "type": "TH"},
                ]
            },
            {
                "day": "Thứ 7", "date": "25/04/2026",
                "sessions": [
                    {"start": "07:00", "end": "09:30", "subject": "Đại số tuyến tính (9)_TA", "room": "K.A212", "type": "LT"},
                    {"start": "15:00", "end": "16:30", "subject": "Khởi nghiệp và đổi mới sáng tạo (9)", "room": "K.A110", "type": "LT"},
                ]
            },
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

    def get_schedule(self):
        return self.schedule

    def get_tasks(self):
        return self.tasks

    def get_stats(self):
        return self.stats

    def get_notifications(self):
        return self.notifications

    def get_study_suggestions(self):
        return "Bạn có 2 môn thi tuần tới. AI gợi ý ưu tiên ôn tập Tiếng Anh 2 và Cấu trúc dữ liệu trước."
