import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt

from ui.components.sidebar import Sidebar

# Tạm thời comment các trang cũ do chưa convert xong
from ui.page.home_page import HomePage
# Tạm thời comment các trang chưa convert sang PySide6 để tránh crash
from ui.page.document_page import DocumentPage
from ui.page.setting_page import SettingPage
from ui.page.AI_assistant_page import AIAssistantPage

# Nhập các Service (Dịch vụ)
from BE.services.home_service import HomeService
from BE.services.documente_service import DocumenteService
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
        self.home_service = HomeService()
        self.documente_service  = DocumenteService()
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

        # Khởi tạo các trang Tổng quan (Mới cập nhật)
        self.home_page = HomePage(self.page_stack, self.home_service, self.ai_service)
        self.page_stack.addWidget(self.home_page)
        self.pages["Tổng quan"] = self.home_page

        # Khởi tạo trang Tài liệu (Đã convert)
        self.document_page = DocumentPage(self.page_stack, self.documente_service)
        self.page_stack.addWidget(self.document_page)
        self.pages["Tài liệu"] = self.document_page

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
