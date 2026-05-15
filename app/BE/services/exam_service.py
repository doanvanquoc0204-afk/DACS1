# app/BE/services/exam_service.py

class ExamService:
    def __init__(self):
        # Dữ liệu mẫu – sau này thay bằng lời gọi Supabase/Google Drive
        self.exams = [
            {
                "name":      "Đề thi học kỳ 2 – Toán 12",
                "sub":       "Đề thi học kỳ 2 năm học 2024-2025",
                "subject":   "Toán",
                "grade":     "Lớp 12",
                "type":      "Cuối kỳ",
                "date":      "20/04/2026",
                "size":      "2.4 MB",
                "downloads": 128,
                "file_type": "PDF",
            },
            {
                "name":      "Đề thi giữa kỳ 2 – Văn 11",
                "sub":       "Đề tham khảo giữa kỳ 2",
                "subject":   "Ngữ văn",
                "grade":     "Lớp 11",
                "type":      "Giữa kỳ",
                "date":      "19/04/2026",
                "size":      "1.8 MB",
                "downloads": 87,
                "file_type": "DOCX",
            },
            {
                "name":      "Đề thi thử THPTQG – Lý 12",
                "sub":       "Đề thi thử tốt nghiệp THPT Quốc gia",
                "subject":   "Vật lý",
                "grade":     "Lớp 12",
                "type":      "Thi thử",
                "date":      "18/04/2026",
                "size":      "3.1 MB",
                "downloads": 214,
                "file_type": "PDF",
            },
            {
                "name":      "Đề cương ôn tập – Hóa 11",
                "sub":       "Đề cương ôn tập học kỳ 2",
                "subject":   "Hóa học",
                "grade":     "Lớp 11",
                "type":      "Đề ôn tập",
                "date":      "17/04/2026",
                "size":      "1.2 MB",
                "downloads": 63,
                "file_type": "PDF",
            },
            {
                "name":      "Đề thi học kỳ 1 – Anh 12",
                "sub":       "Đề thi học kỳ 1 năm học 2024-2025",
                "subject":   "Tiếng Anh",
                "grade":     "Lớp 12",
                "type":      "Cuối kỳ",
                "date":      "15/04/2026",
                "size":      "2.0 MB",
                "downloads": 179,
                "file_type": "DOCX",
            },
        ]

        self.stats = {
            "total":       128,
            "pdf_count":   36,
            "word_count":  24,
            "recent_downloads": 18,
        }

        self.popular_subjects = [
            ("📐 Toán",       32),
            ("📖 Ngữ văn",    18),
            ("⚡ Vật lý",     15),
            ("🧪 Hóa học",    14),
            ("🌍 Tiếng Anh",  20),
        ]

    # ── Các hàm truy xuất dữ liệu ──────────────────────────
    def get_exams(self):
        """Trả về toàn bộ danh sách đề thi."""
        return self.exams

    def get_stats(self):
        """Trả về số liệu thống kê tổng quan."""
        return self.stats

    def get_popular_subjects(self):
        """Trả về danh sách môn học phổ biến."""
        return self.popular_subjects
