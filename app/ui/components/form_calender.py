from PySide6.QtCore import QDate, QTime, Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components.select_hour import TimePickerDialog
from ui.components.select_date import StyledCalendar


PRIMARY = "#4C96F5"
PRIMARY_HOVER = "#357FE0"
BG = "#F5F7FB"
CARD = "#FFFFFF"
BORDER = "#D8E0EE"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#64748B"


def make_font(size, bold=False):
    """Tạo đối tượng QFont với font Segoe UI và định dạng in đậm tùy chọn."""
    font = QFont("Segoe UI", size)
    font.setWeight(QFont.Bold if bold else QFont.Normal)
    return font

class AddScheduleDialog(QDialog):
    """Cửa sổ hội thoại để thêm một tiết học/lịch học mới vào thời khóa biểu."""
    def __init__(self, home_service, parent=None):
        super().__init__(parent)
        self.home_service = home_service
        self.setWindowTitle("Thêm lịch học")
        self.setModal(True)
        self.setFixedSize(720, 750)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(self._style_sheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # Header
        main_layout.addWidget(self._build_header())

        # Time section
        main_layout.addWidget(self._build_time_section())

        # Course info section
        main_layout.addWidget(self._build_course_section())

        # Note section
        main_layout.addWidget(self._build_note_section())

        # Footer buttons
        main_layout.addWidget(self._build_footer())

    def _build_header(self):
        """Xây dựng phần đầu của form gồm biểu tượng lịch và tiêu đề."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 2)
        layout.setSpacing(12)

        icon = QLabel("📅")
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"background-color: #EAF2FF; color: {PRIMARY}; border-radius: 14px; font-size: 24px;"
        )
        layout.addWidget(icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(3)

        title = QLabel("Thêm lịch học")
        title.setFont(make_font(18, True))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        title_box.addWidget(title)

        subtitle = QLabel("Nhập thông tin để thêm lịch học mới")
        subtitle.setFont(make_font(11))
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY};")
        title_box.addWidget(subtitle)

        layout.addLayout(title_box, 1)
        return header

    def _build_time_section(self):
        """Tạo phần chọn thời gian cho lịch học."""
        card, layout = self._create_card("Thời gian")
        card.setMinimumHeight(210)

        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.start_time_edit = self._create_time_input(QTime.currentTime().toString("HH:mm"))
        self.end_time_edit = self._create_time_input(QTime.currentTime().addSecs(90 * 60).toString("HH:mm"))

        for date_edit in (self.start_date_edit, self.end_date_edit):
            date_edit.setCalendarPopup(True)
            date_edit.setCalendarWidget(StyledCalendar(date_edit))
            date_edit.setDisplayFormat("dd/MM/yyyy")
            date_edit.setFixedHeight(36)
            date_edit.setCursor(QCursor(Qt.PointingHandCursor))
            self._setup_emoji_icon(date_edit, "📅")

        grid = QGridLayout()
        grid.setContentsMargins(0, 8, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self._add_field(grid, "Ngày bắt đầu", self.start_date_edit, 0, 0)
        self._add_field(grid, "Ngày kết thúc", self.end_date_edit, 0, 1)
        self._add_field(grid, "Giờ bắt đầu", self.start_time_edit, 1, 0)
        self._add_field(grid, "Giờ kết thúc", self.end_time_edit, 1, 1)
        layout.addLayout(grid)

        return card

    def _build_time_row(self):
        """Tạo hàng chọn thời gian bắt đầu và kết thúc tiết học."""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        start_field = self._field_wrapper("Giờ bắt đầu")
        self.start_time_input = QLineEdit("07:00")
        self.start_time_input.setReadOnly(True)
        self.start_time_input.setFixedHeight(40)
        self.start_time_input.setCursor(QCursor(Qt.PointingHandCursor))
        # Mở TimePicker khi click
        self.start_time_input.mousePressEvent = lambda event, w=self.start_time_input: self._open_time_picker(w)
        self._setup_emoji_icon(self.start_time_input, "🕒")
        start_field.layout().addWidget(self.start_time_input)

        end_field = self._field_wrapper("Giờ kết thúc")
        self.end_time_input = QLineEdit("09:30")
        self.end_time_input.setReadOnly(True)
        self.end_time_input.setFixedHeight(40)
        self.end_time_input.setCursor(QCursor(Qt.PointingHandCursor))
        # Mở TimePicker khi click
        self.end_time_input.mousePressEvent = lambda event, w=self.end_time_input: self._open_time_picker(w)
        self._setup_emoji_icon(self.end_time_input, "🕒")
        end_field.layout().addWidget(self.end_time_input)

        layout.addWidget(start_field, 1)
        layout.addWidget(end_field, 1)
        return row

    def _create_time_input(self, value):
        """Tạo ô nhập liệu thời gian."""
        time_input = QLineEdit(value)
        time_input.setReadOnly(True)
        time_input.setFixedHeight(36)
        time_input.setCursor(QCursor(Qt.PointingHandCursor))
        self._setup_emoji_icon(time_input, "🕒")
        time_input.mousePressEvent = lambda event, widget=time_input: self._open_time_picker(widget)
        return time_input

    def _open_time_picker(self, target_input):
        """Mở cửa sổ chọn giờ chi tiết."""
        dialog = TimePickerDialog(target_input.text(), self)
        if dialog.exec() == QDialog.Accepted:
            target_input.setText(dialog.get_time())

    def _build_course_section(self):
        """Tạo phần nhập thông tin học phần."""
        card, layout = self._create_card("Thông tin học phần")
        card.setMinimumHeight(210)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Nhập tên môn học hoặc tiêu đề...")
        self.title_input.setFixedHeight(36)

        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("VD: A205, B101...")
        self.room_input.setFixedHeight(36)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Lý thuyết", "Thực hành", "Thể dục"])
        self.type_combo.setFixedHeight(36)
        self.type_combo.setCursor(QCursor(Qt.PointingHandCursor))

        grid = QGridLayout()
        grid.setContentsMargins(0, 8, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(18)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self._add_field(grid, "Tiêu đề", self.title_input, 0, 0, 1, 2)
        self._add_field(grid, "Phòng học", self.room_input, 1, 0)
        self._add_field(grid, "Loại buổi học", self.type_combo, 1, 1)
        layout.addLayout(grid)

        return card

    def _build_date_selection(self):
        """Tạo vùng chọn Ngày học sử dụng bảng lịch tùy chỉnh."""
        card, layout = self._create_card("Ghi chú")
        card.setMinimumHeight(150)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Nhập ghi chú nếu có...")
        self.note_input.setFixedHeight(65)
        layout.addWidget(self.note_input)

        return card

    def _build_note_section(self):
        """Tạo phần ghi chú cho lịch học."""
        card, layout = self._create_card("Ghi chú")
        card.setMinimumHeight(150)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Nhập ghi chú nếu có...")
        self.note_input.setFixedHeight(65)
        layout.addWidget(self.note_input)

        return card

    def _build_location_row(self):
        """Tạo hàng nhập Phòng học và Loại hình (Lý thuyết/Thực hành)."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.addStretch()
        return footer

    def _build_footer(self):
        """Tạo phần chân trang với các nút chức năng."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.addStretch()

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Thêm lịch học")
        submit_btn.setObjectName("submitButton")
        submit_btn.setFixedSize(140, 36)
        submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        submit_btn.clicked.connect(self._submit)
        layout.addWidget(submit_btn)

        return footer

    def _create_card(self, title_text):
        card = QFrame()
        card.setObjectName("sectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setFont(make_font(13, True))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        return card, layout

    def _add_field(self, grid, label_text, widget, row, col, row_span=1, col_span=1):
        wrapper = QWidget()
        wrapper.setMinimumHeight(65)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 3)
        layout.setSpacing(4)

        label = QLabel(label_text)
        label.setFont(make_font(11, True))
        label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(label)
        layout.addWidget(widget)

        grid.addWidget(wrapper, row, col, row_span, col_span)

    def _setup_emoji_icon(self, widget, emoji):
        """Thêm biểu tượng Emoji làm vật trang trí bên trong ô nhập liệu."""
        # Tạo label chứa emoji và đặt widget làm cha
        icon_label = QLabel(emoji, widget)
        icon_label.setStyleSheet("background: transparent; font-size: 14px; border: none;")
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents) # Để không chặn click vào date_edit
        
        # Căn lề phải cho icon
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addStretch()
        layout.addWidget(icon_label)

    def _submit(self):
        """Xử lý thu thập dữ liệu từ tất cả các ô nhập và lưu vào hệ thống qua Service."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Thiếu tiêu đề", "Vui lòng nhập tiêu đề lịch học.")
            self.title_input.setFocus()
            return

        same_day = self.start_date_edit.date() == self.end_date_edit.date()
        invalid_time = self.end_time_edit.text() <= self.start_time_edit.text()
        if same_day and invalid_time:
            QMessageBox.warning(
                self,
                "Thời gian không hợp lệ",
                "Giờ kết thúc phải lớn hơn giờ bắt đầu trong cùng một ngày.",
            )
            return

        data = {
            "start_date": self.start_date_edit.date().toString("dd/MM/yyyy"),
            "end_date": self.end_date_edit.date().toString("dd/MM/yyyy"),
            "start_time": self.start_time_edit.text(),
            "end_time": self.end_time_edit.text(),
            "title": title,
            "room": self.room_input.text().strip(),
            "type": self.type_combo.currentText(),
            "note": self.note_input.toPlainText().strip(),
        }
        # Gọi Service để xử lý (Contract với Backend)
        success = self.home_service.add_schedule(data)
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu lịch học. Vui lòng thử lại.")

    def _style_sheet(self):
        return f"""
            QDialog {{
                background-color: {BG};
            }}
            #sectionCard {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
            }}
            QLineEdit, QDateEdit, QComboBox, QTextEdit {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 11px;
                font-family: "Segoe UI";
                font-size: 12px;
                selection-background-color: {PRIMARY};
            }}
            QTextEdit {{
                padding: 9px 11px;
            }}
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 1px solid {PRIMARY};
            }}
            QComboBox::drop-down, QDateEdit::drop-down {{
                border: none;
                width: 32px;
            }}
            QDateEdit {{
                padding-right: 30px;
            }}
            QComboBox::down-arrow {{
                image: url(image/down_arrow.png);
                width: 14px;
                height: 14px;
            }}

            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                selection-background-color: #EAF2FF;
                selection-color: {TEXT_PRIMARY};
                outline: none;
            }}
            QPushButton {{
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
                border-radius: 9px;
            }}
            #submitButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border: none;
            }}
            #submitButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            #cancelButton {{
                background-color: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
            }}
            #cancelButton:hover {{
                background-color: #F8FAFC;
            }}
        """
