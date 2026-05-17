import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QScrollArea, QFrame, QApplication, QCheckBox, QStyledItemDelegate
)
from PySide6.QtGui import QPixmap, QCursor, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QRect, QPoint

from config import COLORS, FONTS

def get_font_style(font_tuple):
    """Hàm tiện ích để tạo chuỗi style CSS cho Font dựa trên tuple cấu hình."""
    family, size, *weight = font_tuple
    w = "bold" if weight and weight[0] == "bold" else "normal"
    return f"font-family: '{family}'; font-size: {size}px; font-weight: {w};"

class ToggleSwitch(QCheckBox):
    """Nút gạt (Switch) tùy chỉnh theo phong cách iOS/Material Design."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.stateChanged.connect(self.update_state)

    def update_state(self):
        self.update()

    def hitButton(self, pos: QPoint) -> bool:
        return self.rect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Track (Nền thanh gạt)
        track_opacity = 1.0
        track_color = QColor(COLORS['primary']) if self.isChecked() else QColor(COLORS['border'])
        painter.setBrush(track_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 4, 44, 20, 10, 10)
        
        # Thumb (Nút tròn gạt)
        painter.setBrush(QColor("white"))
        # Vị trí nút tròn: 4 khi tắt, 24 khi bật
        x_pos = 24 if self.isChecked() else 4
        painter.drawEllipse(x_pos, 7, 14, 14)
        painter.end()

class ArrowComboBox(QComboBox):
    """QComboBox tùy chỉnh tự vẽ mũi tên xuống, không cần sử dụng file ảnh bên ngoài."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(QStyledItemDelegate())
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Sử dụng màu chữ chính để đảm bảo độ tương phản
        painter.setPen(QColor(COLORS.get('text_primary', '#111827')))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        arrow_rect = QRect(self.width() - 22, 0, 18, self.height())
        painter.drawText(arrow_rect, Qt.AlignVCenter | Qt.AlignHCenter, "▼")
        painter.end()

# ═══════════════════════════════════════════════
#  HELPER
# ═══════════════════════════════════════════════
def create_card():
    """Hàm tạo khung thẻ (Card) trắng có viền bo góc dùng cho các mục cài đặt."""
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {COLORS['card']};
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
        }}
    """)
    return card

def create_divider():
    """Tạo đường kẻ ngang mỏng để phân tách các mục."""
    div = QFrame()
    div.setFixedHeight(1)
    div.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
    return div

# ═══════════════════════════════════════════════
#  MAIN PAGE
# ═══════════════════════════════════════════════
class SettingPage(QWidget):
    """Trang cài đặt hệ thống: Thông tin tài khoản, Giao diện, Thông báo và Bảo mật."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Scroll Content
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(14)
        
        # Variables
        self.selected_theme = "Sáng"
        self.gender_val = "Nam"
        
        # Build UI
        self.create_header()
        self.create_account_info_card()
        self.create_password_card()
        self.create_appearance_card()
        self.create_notification_card()
        self.create_account_action_card()
        
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    # ──────────────────────────────────────────
    #  1. HEADER
    # ──────────────────────────────────────────
    def create_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 18)
        layout.setSpacing(2)
        
        title = QLabel("Cài đặt")
        title.setStyleSheet(f"{get_font_style(FONTS['h1_set'])} color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Tùy chỉnh tài khoản và ứng dụng của bạn")
        subtitle.setStyleSheet(f"{get_font_style(FONTS['body_set'])} color: {COLORS['text_secondary']};")
        layout.addWidget(subtitle)
        
        self.scroll_layout.addWidget(header)

    # ──────────────────────────────────────────
    #  2. CARD: THÔNG TIN TÀI KHOẢN
    # ──────────────────────────────────────────
    def create_account_info_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        
        # Header
        hdr = QWidget()
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 14)
        
        title = QLabel("👤  Thông tin tài khoản")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        hdr_layout.addWidget(title)
        
        hdr_layout.addStretch()
        
        btn_edit = QPushButton("Chỉnh sửa")
        btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        btn_edit.setFixedSize(90, 30)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                {get_font_style(FONTS['small_bold_set'])}
                border: 2px solid {COLORS['primary']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        btn_edit.clicked.connect(lambda: print("Chỉnh sửa thông tin"))
        hdr_layout.addWidget(btn_edit)
        layout.addWidget(hdr)
        
        # Body
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        
        # Avatar
        avatar_col = QWidget()
        avatar_col.setFixedWidth(120)
        avatar_layout = QVBoxLayout(avatar_col)
        avatar_layout.setContentsMargins(0, 0, 20, 0)
        avatar_layout.setAlignment(Qt.AlignTop)
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        img_dir = os.path.join(base_dir, "image")
        
        self.man_pixmap = QPixmap(os.path.join(img_dir, "user_man.png")).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.woman_pixmap = QPixmap(os.path.join(img_dir, "user_woman.png")).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        self.update_avatar()
        avatar_layout.addWidget(self.avatar_label)
        body_layout.addWidget(avatar_col)
        
        # Form
        form = QWidget()
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15)
        
        fields = [
            ("Họ và tên",           "Nguyen Van A",              0, 0, False),
            ("Email",               "nguyenvana@student.edu.vn", 0, 1, False),
            ("Giới tính",           "Nam",                       1, 0, True),
            ("Ngày tháng năm sinh", "01/01/2000",                1, 1, False),
            ("Mã sinh viên",        "K.AI212",                   2, 0, False),
            ("Số điện thoại",       "0912345678",                2, 1, False),
            ("Trường",              "Đại học Công nghệ",         3, 0, False),
            ("Ngành học",           "Công nghệ thông tin",       3, 1, False),
        ]
        
        for label_text, value, row, col, is_combo in fields:
            cell = QWidget()
            cell_layout = QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(6)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
            cell_layout.addWidget(lbl)
            
            input_style = f"""
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: transparent;
                {get_font_style(FONTS['body_set'])}
                color: {COLORS['text_primary']};
                padding: 4px 8px;
            """
            
            if is_combo:
                cb = ArrowComboBox()
                cb.setFixedHeight(36)
                cb.setStyleSheet("QComboBox { " + input_style + " padding-right: 26px; } QComboBox::drop-down { width: 0px; border: none; } QComboBox::down-arrow { image: none; } QComboBox QAbstractItemView { background-color: white; color: " + COLORS['text_primary'] + "; selection-background-color: " + COLORS['hover'] + "; }")
                if label_text == "Giới tính":
                    cb.addItems(["Nam", "Nữ"])
                    cb.setCurrentText(value)
                    cb.currentTextChanged.connect(self.on_gender_change)
                else:
                    cb.addItems([value, "Khác"])
                cell_layout.addWidget(cb)
            else:
                ent = QLineEdit()
                ent.setFixedHeight(36)
                ent.setText(value)
                ent.setStyleSheet("QLineEdit { " + input_style + " }")
                cell_layout.addWidget(ent)
                
            form_layout.addWidget(cell, row, col)
            
        body_layout.addWidget(form, 1)
        layout.addWidget(body)
        self.scroll_layout.addWidget(card)

    def update_avatar(self):
        if self.gender_val == "Nam":
            self.avatar_label.setPixmap(self.man_pixmap)
        else:
            self.avatar_label.setPixmap(self.woman_pixmap)

    def on_gender_change(self, text):
        self.gender_val = text
        self.update_avatar()

    # ──────────────────────────────────────────
    #  3. CARD: ĐỔI MẬT KHẨU
    # ──────────────────────────────────────────
    def create_password_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        
        title = QLabel("Đổi mật khẩu")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        pw_form = QWidget()
        pw_layout = QHBoxLayout(pw_form)
        pw_layout.setContentsMargins(0, 12, 0, 0)
        pw_layout.setSpacing(16)
        
        pw_fields = [
            ("Mật khẩu hiện tại", "Nhập mật khẩu hiện tại"),
            ("Mật khẩu mới", "Nhập mật khẩu mới"),
            ("Xác nhận mật khẩu mới", "Nhập lại mật khẩu mới")
        ]
        
        for label_text, placeholder in pw_fields:
            col_frame = QWidget()
            col_layout = QVBoxLayout(col_frame)
            col_layout.setContentsMargins(0, 0, 0, 0)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
            col_layout.addWidget(lbl)
            
            ent = QLineEdit()
            ent.setPlaceholderText(placeholder)
            ent.setEchoMode(QLineEdit.Password)
            ent.setFixedHeight(36)
            ent.setStyleSheet(f"""
                QLineEdit {{
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    background-color: transparent;
                    {get_font_style(FONTS['body_set'])}
                    color: {COLORS['text_primary']};
                    padding: 4px 8px;
                }}
            """)
            col_layout.addWidget(ent)
            pw_layout.addWidget(col_frame, 1)
            
        btn_update = QPushButton("Cập nhật mật khẩu")
        btn_update.setFixedHeight(36)
        btn_update.setCursor(QCursor(Qt.PointingHandCursor))
        btn_update.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: #FFFFFF;
                {get_font_style(FONTS['body_bold_set'])}
                border-radius: 8px;
                border: none;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        btn_update.clicked.connect(lambda: print("Xử lý cập nhật mật khẩu"))
        
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignBottom)
        btn_layout.addWidget(btn_update)
        
        pw_layout.addWidget(btn_container)
        layout.addWidget(pw_form)
        self.scroll_layout.addWidget(card)

    # ──────────────────────────────────────────
    #  4. CARD: GIAO DIỆN
    # ──────────────────────────────────────────
    def create_appearance_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        
        title = QLabel("🎨  Giao diện")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        row_frame = QWidget()
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(0, 14, 0, 0)
        
        desc = QWidget()
        desc_layout = QVBoxLayout(desc)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        
        l1 = QLabel("Chế độ giao diện")
        l1.setStyleSheet(f"{get_font_style(FONTS['body_bold_set'])} color: {COLORS['text_primary']}; border: none;")
        desc_layout.addWidget(l1)
        
        l2 = QLabel("Chọn chế độ hiển thị phù hợp với bạn")
        l2.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
        desc_layout.addWidget(l2)
        
        row_layout.addWidget(desc)
        row_layout.addStretch()
        
        options_row = QWidget()
        options_layout = QHBoxLayout(options_row)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(10)
        
        themes = [("☀️", "Sáng"), ("🌙", "Tối"), ("🖥", "Tự động")]
        self.theme_btns = {}
        
        for icon, name in themes:
            btn = QPushButton(f"{icon}  {name}")
            btn.setFixedSize(110, 38)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.theme_btns[name] = btn
            btn.clicked.connect(lambda checked=False, n=name: self.select_theme(n))
            options_layout.addWidget(btn)
            
        self.select_theme("Sáng")
        row_layout.addWidget(options_row)
        
        layout.addWidget(row_frame)
        self.scroll_layout.addWidget(card)

    def select_theme(self, name):
        self.selected_theme = name
        for n, btn in self.theme_btns.items():
            if n == name:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['primary']};
                        {get_font_style(FONTS['body_bold_set'])}
                        border: 2px solid {COLORS['primary']};
                        border-radius: 8px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text_secondary']};
                        {get_font_style(FONTS['body_bold_set'])}
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{ background-color: {COLORS['hover']}; }}
                """)

    # ──────────────────────────────────────────
    #  5. CARD: THÔNG BÁO
    # ──────────────────────────────────────────
    def create_notification_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        
        title = QLabel("🔔  Thông báo")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        self.create_setting_row(
            layout, "📅", "#DBEAFE", "Nhắc lịch học", "Nhận thông báo trước giờ học",
            ["30 phút trước", "15 phút trước", "1 giờ trước"], "30 phút trước"
        )
        layout.addWidget(create_divider())
        self.create_setting_row(
            layout, "📌", "#FEF3C7", "Nhắc deadline", "Nhận thông báo trước khi đến hạn nộp bài",
            ["1 ngày trước", "3 giờ trước", "30 phút trước"], "1 ngày trước"
        )
        
        note = QLabel("ℹ️   Bạn sẽ nhận thông báo qua ứng dụng và (nếu cho phép) qua email.")
        note.setStyleSheet(f"""
            background-color: {COLORS['blue_light']};
            color: {COLORS['text_secondary']};
            {get_font_style(FONTS['small_set'])}
            border-radius: 8px;
            padding: 10px 12px;
            border: none;
        """)
        layout.addWidget(note)
        self.scroll_layout.addWidget(card)

    def create_setting_row(self, parent_layout, icon, icon_bg, title, subtitle, combo_values, combo_default):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 8, 0, 8)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"background-color: {icon_bg}; border-radius: 10px; font-size: 15px; border: none;")
        row_layout.addWidget(icon_lbl)
        
        txt = QWidget()
        txt_layout = QVBoxLayout(txt)
        txt_layout.setContentsMargins(12, 0, 0, 0)
        
        l1 = QLabel(title)
        l1.setStyleSheet(f"{get_font_style(FONTS['body_bold_set'])} color: {COLORS['text_primary']}; border: none;")
        txt_layout.addWidget(l1)
        
        l2 = QLabel(subtitle)
        l2.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
        txt_layout.addWidget(l2)
        
        row_layout.addWidget(txt, 1)
        
        cb = ArrowComboBox()
        cb.addItems(combo_values)
        cb.setCurrentText(combo_default)
        cb.setFixedHeight(32)
        cb.setFixedWidth(160)
        cb.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: transparent;
                {get_font_style(FONTS['small_set'])}
                color: {COLORS['text_primary']};
                padding: 4px 26px 4px 8px;
            }}
            QComboBox::drop-down {{ width: 0px; border: none; }}
            QComboBox::down-arrow {{ image: none; }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: #111827;
                selection-background-color: #F5F7FB;
                selection-color: #111827;
                border: 1px solid #BFCAD9;
            }}
        """)
        row_layout.addWidget(cb)
        
        sw = ToggleSwitch()
        sw.setChecked(True)
        row_layout.addWidget(sw)
        
        parent_layout.addWidget(row)

    # ──────────────────────────────────────────
    #  6. CARD: TÀI KHOẢN
    # ──────────────────────────────────────────
    def create_account_action_card(self):
        card = create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        
        title = QLabel("👤  Tài khoản")
        title.setStyleSheet(f"{get_font_style(FONTS['h3_set'])} color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        self.create_action_row(layout, "🚪", "#FEE2E2", "Đăng xuất", "Đăng xuất khỏi StudyAI trên thiết bị này", "Đăng xuất", lambda: print("Đăng xuất"))
        layout.addWidget(create_divider())
        self.create_action_row(layout, "🗑", "#FEE2E2", "Xóa tài khoản", "Xóa vĩnh viễn tài khoản và toàn bộ dữ liệu của bạn", "Xóa tài khoản", lambda: print("Xóa tài khoản"))
        
        warn = QLabel("⚠️   Lưu ý: Hành động này không thể hoàn tác. Vui lòng cân nhắc kỹ trước khi xóa tài khoản.")
        warn.setWordWrap(True)
        warn.setStyleSheet(f"""
            background-color: {COLORS['danger_bg']};
            color: {COLORS['danger']};
            {get_font_style(FONTS['small_set'])}
            border-radius: 8px;
            padding: 10px 12px;
            border: none;
        """)
        layout.addWidget(warn)
        self.scroll_layout.addWidget(card)

    def create_action_row(self, parent_layout, icon, icon_bg, title, subtitle, btn_text, cmd):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 8, 0, 8)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"background-color: {icon_bg}; border-radius: 10px; font-size: 15px; border: none;")
        row_layout.addWidget(icon_lbl)
        
        txt = QWidget()
        txt_layout = QVBoxLayout(txt)
        txt_layout.setContentsMargins(12, 0, 0, 0)
        
        l1 = QLabel(title)
        l1.setStyleSheet(f"{get_font_style(FONTS['body_bold_set'])} color: {COLORS['text_primary']}; border: none;")
        txt_layout.addWidget(l1)
        
        l2 = QLabel(subtitle)
        l2.setStyleSheet(f"{get_font_style(FONTS['small_set'])} color: {COLORS['text_secondary']}; border: none;")
        txt_layout.addWidget(l2)
        
        row_layout.addWidget(txt, 1)
        
        btn = QPushButton(btn_text)
        btn.setFixedSize(120, 34)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['danger']};
                {get_font_style(FONTS['small_bold_set'])}
                border: 2px solid {COLORS['danger']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_bg']};
            }}
        """)
        btn.clicked.connect(cmd)
        row_layout.addWidget(btn)
        
        parent_layout.addWidget(row)

# ═══════════════════════════════════════════════
#  CHẠY THỬ ĐỘC LẬP
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingPage()
    window.resize(1100, 760)
    window.show()
    sys.exit(app.exec())
