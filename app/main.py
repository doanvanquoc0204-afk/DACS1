import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt

from ui.components.sidebar import Sidebar

# Tạm thời comment các trang cũ do chưa convert xong
from ui.page.center_panel import CenterPanel
# Tạm thời comment các trang chưa convert sang PySide6 để tránh crash
from ui.page.exam_question import ExamQuestionPage
from ui.page.setting import SettingPage
from ui.page.AI_assistant import AIAssistantPage

# Nhập các Service (Dịch vụ)
from BE.services.study_service import StudyService
from BE.services.exam_service import ExamService
from AI.chatbot.ai_service import AIService

# ── Cấu hình màu sắc ─────────────────────────────────────────────────────────
COLORS = {
    "bg": "#F5F7FB",  # Màu nền ứng dụng
}

class StudyAIApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StudyAI")
        self.resize(1440, 900)
        # self.showMaximized() # Phóng to toàn màn hình (Đã chuyển ra main)
        
        self.setStyleSheet(f"QMainWindow {{ background-color: {COLORS['bg']}; }}")

        # Khởi tạo các Service
        self.study_service = StudyService()
        self.exam_service  = ExamService()
        self.ai_service    = AIService()

        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # Xóa margin viền
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────
        self.sidebar = Sidebar(on_navigate=self.navigate)
        main_layout.addWidget(self.sidebar)

        # ── QStackedWidget chứa các trang ───────────────────────
        self.page_stack = QStackedWidget()
        main_layout.addWidget(self.page_stack, 1) # stretch=1

        # Tạo một trang placeholder chung cho các trang chưa convert
        self.pages = {}
        for page_name in ["Thống kê"]:
            placeholder = QWidget()
            layout = QHBoxLayout(placeholder)
            label = QLabel(f"Trang '{page_name}' đang được nâng cấp lên PySide6...\nVui lòng chờ nhé!")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 21px; color: #64748B;")
            layout.addWidget(label)
            
            self.page_stack.addWidget(placeholder)
            self.pages[page_name] = placeholder

        # Khởi tạo trang Cài đặt (Đã convert)
        self.setting_page = SettingPage()
        self.page_stack.addWidget(self.setting_page)
        self.pages["Cài đặt"] = self.setting_page

        # Khởi tạo trang Tổng quan (Mới cập nhật)
        self.center_panel = CenterPanel(self.page_stack, self.study_service, self.ai_service)
        self.page_stack.addWidget(self.center_panel)
        self.pages["Tổng quan"] = self.center_panel

        # Khởi tạo trang Tài liệu (Đã convert)
        self.exam_page = ExamQuestionPage(self.page_stack, self.exam_service)
        self.page_stack.addWidget(self.exam_page)
        self.pages["Tài liệu"] = self.exam_page

        # Khởi tạo trang Trợ lý AI (Đã convert)
        self.ai_page = AIAssistantPage(self.page_stack, self.ai_service)
        self.page_stack.addWidget(self.ai_page)
        self.pages["Trợ lý AI"] = self.ai_page

        # Hiển thị trang mặc định
        self.navigate("Tổng quan")

    def navigate(self, page_name):
        """Chuyển đổi trang trên QStackedWidget."""
        self.sidebar.set_active_page(page_name)
        if page_name in self.pages:
            self.page_stack.setCurrentWidget(self.pages[page_name])
        else:
            print(f"Page '{page_name}' chưa được xây dựng.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudyAIApp()
    window.showMaximized()
    sys.exit(app.exec())
