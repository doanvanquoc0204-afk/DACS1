from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QCursor, QFont, QPainter, QColor
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QVBoxLayout, QWidget, QStyledItemDelegate
)

from config import COLORS, FONTS

def qfont(font_tuple):
    """Hàm tiện ích để tạo QFont từ tuple cấu hình trong file config."""
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class ArrowComboBox(QComboBox):
    """QComboBox tùy chỉnh, tự vẽ mũi tên ▼ bằng văn bản thay vì dùng ảnh, giúp giao diện nhẹ và đồng bộ."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(QStyledItemDelegate())
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#64748B"))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        arrow_rect = QRect(self.width() - 22, 0, 18, self.height())
        painter.drawText(arrow_rect, Qt.AlignVCenter | Qt.AlignHCenter, "▼")
        painter.end()

class DocumentPage(QFrame):
    """Trang quản lý tài liệu và đề thi, cho phép tìm kiếm, xem và tải xuống."""
    def __init__(self, master, documente_service):
        super().__init__(master)
        self.documente_service = documente_service
        
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Vùng cuộn bên trái
        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }")
        
        self.left_content = QWidget()
        self.left_content.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout(self.left_content)
        self.left_layout.setContentsMargins(0, 0, 10, 0)
        self.left_layout.setSpacing(20)
        self.left_layout.setAlignment(Qt.AlignTop)
        
        self.left_scroll.setWidget(self.left_content)
        
        # Cột phải (cố định)
        self.right_frame = QFrame()
        self.right_frame.setStyleSheet("background: transparent;")
        self.right_frame.setFixedWidth(360)
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(20)
        self.right_layout.setAlignment(Qt.AlignTop)
        
        main_layout.addWidget(self.left_scroll, 1)
        main_layout.addWidget(self.right_frame, 0)
        
        self.create_header()
        self.create_search_bar()
        self.create_stats()
        self.create_exam_list()
        self.create_right_panel()

    def make_card(self):
        """Tạo một QFrame với kiểu dáng thẻ (bo góc, viền xám) dùng cho các mục đề thi."""
        card = QFrame()
        card.setObjectName("exam_card")
        card.setStyleSheet(f"""
            #exam_card {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        return card

    def create_header(self):
        """Tạo phần tiêu đề trang và các nút chức năng (Upload, Refresh)."""
        header = QFrame()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        title = QLabel("Hệ thống đề thi")
        title.setFont(qfont(FONTS["h1_exam"]))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        sub = QLabel("Quản lý, tìm kiếm và tải xuống tài liệu ôn tập")
        sub.setFont(qfont(FONTS["small_exam"]))
        sub.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        
        title_box.addWidget(title)
        title_box.addWidget(sub)
        
        h_layout.addLayout(title_box)
        h_layout.addStretch()
        
        btn_upload = QPushButton("+ Upload đề thi")
        btn_upload.setFixedHeight(38)
        btn_upload.setFont(qfont(FONTS["body_bold_exam"]))
        btn_upload.setCursor(QCursor(Qt.PointingHandCursor))
        btn_upload.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: #357FE0;
            }}
        """)
        
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setFont(qfont(FONTS["body_exam"]))
        btn_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        
        h_layout.addWidget(btn_upload)
        h_layout.addWidget(btn_refresh)
        
        self.left_layout.addWidget(header)

    def create_search_bar(self):
        """Tạo thanh tìm kiếm kết hợp các bộ lọc (Môn học, Lớp)."""
        bar = self.make_card()
        b_layout = QHBoxLayout(bar)
        b_layout.setContentsMargins(15, 12, 15, 12)
        b_layout.setSpacing(10)
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Tìm kiếm đề thi, môn học, lớp học...")
        self.search_entry.setFixedHeight(40)
        self.search_entry.setFont(qfont(FONTS["small_exam"]))
        self.search_entry.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 10px;
                background-color: {COLORS['bg']};
                color: {COLORS['text_primary']};
            }}
        """)
        b_layout.addWidget(self.search_entry, 1)
        
        combo_style = f"""
            QComboBox {{
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 32px 0 10px;
                background-color: white;
                color: {COLORS['text_primary']};
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
        """
        
        self.cb_subject = ArrowComboBox()
        self.cb_subject.addItems(["Tất cả môn", "Toán", "Vật lý", "Hóa học", "Tiếng Anh", "Ngữ văn"])
        self.cb_subject.setFixedHeight(40)
        self.cb_subject.setFixedWidth(150)
        self.cb_subject.setFont(qfont(FONTS["body_exam"]))
        self.cb_subject.setStyleSheet(combo_style)
        b_layout.addWidget(self.cb_subject)
        
        self.cb_grade = ArrowComboBox()
        self.cb_grade.addItems(["Tất cả lớp", "Lớp 10", "Lớp 11", "Lớp 12"])
        self.cb_grade.setFixedHeight(40)
        self.cb_grade.setFixedWidth(140)
        self.cb_grade.setFont(qfont(FONTS["body_exam"]))
        self.cb_grade.setStyleSheet(combo_style)
        b_layout.addWidget(self.cb_grade)

        
        btn_search = QPushButton("Tìm kiếm")
        btn_search.setFixedHeight(40)
        btn_search.setFixedWidth(100)
        btn_search.setFont(qfont(FONTS["body_bold_exam"]))
        btn_search.setCursor(QCursor(Qt.PointingHandCursor))
        btn_search.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #357FE0;
            }}
        """)
        b_layout.addWidget(btn_search)
        
        self.left_layout.addWidget(bar)

    def create_stats(self):
        """Tạo hàng hiển thị các con số thống kê tổng quan về tài liệu."""
        stats = self.documente_service.get_stats()
        stats_data = [
            ("📋", str(stats["total"]), "Tổng đề thi", COLORS["primary"], "#DCF0FF"),
            ("📄", str(stats["pdf_count"]), "PDF", "#E74C3C", "#FDDEDE"),
            ("📝", str(stats["word_count"]), "Word", "#2980B9", "#D6EAFB"),
            ("⬇️", str(stats["recent_downloads"]), "Tải gần đây", COLORS.get("success", "#10B981"), "#D4EDDA"),
        ]
        
        stats_row = QFrame()
        s_layout = QHBoxLayout(stats_row)
        s_layout.setContentsMargins(0, 0, 0, 0)
        s_layout.setSpacing(15)
        
        for icon, number, label, color, bg_color in stats_data:
            card = self.make_card()
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(20, 20, 20, 20)
            c_layout.setSpacing(12)
            
            icon_box = QLabel(icon)
            icon_box.setFixedSize(45, 45)
            icon_box.setAlignment(Qt.AlignCenter)
            icon_box.setStyleSheet(f"background-color: {bg_color}; border-radius: 12px; font-size: 19px; border: none;")
            c_layout.addWidget(icon_box)
            
            text_box = QVBoxLayout()
            text_box.setSpacing(2)
            num_lbl = QLabel(number)
            num_lbl.setFont(qfont(FONTS["h3_exam"]))
            num_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            
            desc_lbl = QLabel(label)
            desc_lbl.setFont(qfont(FONTS["small_exam"]))
            desc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
            
            text_box.addWidget(num_lbl)
            text_box.addWidget(desc_lbl)
            c_layout.addLayout(text_box)
            c_layout.addStretch()
            
            s_layout.addWidget(card, 1)
            
        self.left_layout.addWidget(stats_row)

    def create_exam_list(self):
        """Hiển thị danh sách các đề thi dưới dạng các thẻ (Card)."""
        exams = self.documente_service.get_exams()
        total_exams = self.documente_service.get_stats()['total']
        
        hdr = QFrame()
        h_layout = QHBoxLayout(hdr)
        h_layout.setContentsMargins(0, 5, 0, 5)
        
        title = QLabel("Danh sách đề thi")
        title.setFont(qfont(FONTS["h3_exam"]))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        h_layout.addWidget(title)
        
        h_layout.addStretch()
        
        count_lbl = QLabel(f"Hiển thị {len(exams)} / {total_exams} đề thi")
        count_lbl.setFont(qfont(FONTS["small_exam"]))
        count_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        h_layout.addWidget(count_lbl)
        
        self.left_layout.addWidget(hdr)
        
        # Danh sách thẻ
        for exam in exams:
            card = self.make_card()
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(15, 12, 15, 12)
            c_layout.setSpacing(15)
            
            is_pdf = exam["file_type"] == "PDF"
            icon_color    = "#E74C3C" if is_pdf else "#2980B9"
            icon_bg_color = "#FDDEDE" if is_pdf else "#D6EAFB"
            icon_text     = "PDF"     if is_pdf else "DOC"
            
            file_icon = QLabel(icon_text)
            file_icon.setFixedSize(65, 65)
            file_icon.setAlignment(Qt.AlignCenter)
            file_icon.setStyleSheet(f"""
                background-color: {icon_bg_color};
                color: {icon_color};
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                border: none;
            """)
            c_layout.addWidget(file_icon)
            
            # Thông tin (Giữa)
            info_layout = QVBoxLayout()
            info_layout.setSpacing(6)
            
            name_lbl = QLabel(exam["name"])
            name_lbl.setFont(qfont(FONTS["body_bold_exam"]))
            name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            info_layout.addWidget(name_lbl)
            
            sub_lbl = QLabel(exam["sub"])
            sub_lbl.setFont(qfont(FONTS["small_exam"]))
            sub_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
            info_layout.addWidget(sub_lbl)
            
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(8)
            
            tags = [
                (exam["subject"], COLORS["primary"], "#DCF0FF"),
                (exam["grade"], COLORS["text_secondary"], "#F1F5F9"),
                (exam["type"], COLORS.get("warning", "#F59E0B"), "#FEF3C7"),
            ]
            
            for text, color, bg in tags:
                tag_lbl = QLabel(f" {text} ")
                tag_lbl.setFont(qfont(FONTS["small_bold_exam"]))
                tag_lbl.setStyleSheet(f"""
                    background-color: {bg};
                    color: {color};
                    border-radius: 6px;
                    padding: 2px 4px;
                    border: none;
                """)
                tags_layout.addWidget(tag_lbl)
            tags_layout.addStretch()
            
            info_layout.addLayout(tags_layout)
            c_layout.addLayout(info_layout, 1)
            
            # Thông tin phụ & Nút (Phải)
            right_info = QVBoxLayout()
            right_info.setSpacing(6)
            right_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            date_lbl = QLabel(f"📅 {exam['date']}")
            date_lbl.setFont(qfont(FONTS["small_exam"]))
            date_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
            date_lbl.setAlignment(Qt.AlignRight)
            right_info.addWidget(date_lbl)
            
            meta_lbl = QLabel(f"⬇️ {exam['downloads']} lượt  •  {exam['size']}")
            meta_lbl.setFont(qfont(FONTS["small_exam"]))
            meta_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
            meta_lbl.setAlignment(Qt.AlignRight)
            right_info.addWidget(meta_lbl)
            
            btns_layout = QHBoxLayout()
            btns_layout.setAlignment(Qt.AlignRight)
            btns_layout.setSpacing(8)
            
            btn_view = QPushButton("Xem")
            btn_view.setFixedSize(80, 32)
            btn_view.setFont(qfont(FONTS["small_bold_exam"]))
            btn_view.setCursor(QCursor(Qt.PointingHandCursor))
            btn_view.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['primary']};
                    border: 2px solid {COLORS['primary']};
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: #DCF0FF;
                }}
            """)
            
            btn_dl = QPushButton("Tải")
            btn_dl.setFixedSize(80, 32)
            btn_dl.setFont(qfont(FONTS["small_bold_exam"]))
            btn_dl.setCursor(QCursor(Qt.PointingHandCursor))
            btn_dl.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: #357FE0;
                }}
            """)
            
            btns_layout.addWidget(btn_view)
            btns_layout.addWidget(btn_dl)
            right_info.addLayout(btns_layout)
            
            c_layout.addLayout(right_info)
            self.left_layout.addWidget(card)
            
    def create_right_panel(self):
        """Tạo cột bên phải bao gồm khu vực tải lên và các danh mục phổ biến."""
        # Card Upload
        up_card = self.make_card()
        up_layout = QVBoxLayout(up_card)
        up_layout.setContentsMargins(15, 15, 15, 15)
        up_layout.setSpacing(12)
        
        up_hdr = QFrame()
        up_hdr.setStyleSheet(f"background-color: {COLORS['primary']}; border-radius: 8px; border: none;")
        up_h_layout = QHBoxLayout(up_hdr)
        up_h_layout.setContentsMargins(10, 8, 10, 8)
        up_title = QLabel("Upload Files")
        up_title.setFont(qfont(FONTS["h3_exam"]))
        up_title.setStyleSheet("color: white; border: none; background: transparent;")
        up_h_layout.addWidget(up_title)
        up_h_layout.addStretch()
        up_layout.addWidget(up_hdr)
        
        drop_zone = QFrame()
        drop_zone.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['hover']};
                border: 2px dashed #A8CFFA;
                border-radius: 10px;
            }}
        """)
        dz_layout = QVBoxLayout(drop_zone)
        dz_layout.setContentsMargins(15, 20, 15, 20)
        dz_layout.setSpacing(8)
        dz_layout.setAlignment(Qt.AlignCenter)
        
        dz_icon = QLabel("📂")
        dz_icon.setStyleSheet("font-size: 33px; border: none; background: transparent;")
        dz_icon.setAlignment(Qt.AlignCenter)
        dz_layout.addWidget(dz_icon)
        
        dz_txt = QLabel("Kéo thả PDF/DOCX vào đây")
        dz_txt.setFont(qfont(FONTS["body_bold_exam"]))
        dz_txt.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; background: transparent;")
        dz_txt.setAlignment(Qt.AlignCenter)
        dz_layout.addWidget(dz_txt)
        
        dz_sub = QLabel("Hỗ trợ PDF, DOCX – tối đa 50 MB")
        dz_sub.setFont(qfont(FONTS["small_exam"]))
        dz_sub.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
        dz_sub.setAlignment(Qt.AlignCenter)
        dz_layout.addWidget(dz_sub)
        
        up_layout.addWidget(drop_zone)
        
        btn_choose = QPushButton("📁 Chọn file")
        btn_choose.setFixedHeight(40)
        btn_choose.setFont(qfont(FONTS["body_bold_exam"]))
        btn_choose.setCursor(QCursor(Qt.PointingHandCursor))
        btn_choose.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #357FE0;
            }}
        """)
        up_layout.addWidget(btn_choose)
        
        self.right_layout.addWidget(up_card)
        
        # Danh mục phổ biến
        cat_card = self.make_card()
        cat_layout = QVBoxLayout(cat_card)
        cat_layout.setContentsMargins(15, 15, 15, 15)
        cat_layout.setSpacing(10)
        
        cat_hdr = QFrame()
        cat_hdr.setStyleSheet(f"background-color: {COLORS['primary']}; border-radius: 8px; border: none;")
        cat_h_layout = QHBoxLayout(cat_hdr)
        cat_h_layout.setContentsMargins(10, 8, 10, 8)
        cat_title = QLabel("Danh mục phổ biến")
        cat_title.setFont(qfont(FONTS["h3_exam"]))
        cat_title.setStyleSheet("color: white; border: none; background: transparent;")
        cat_h_layout.addWidget(cat_title)
        cat_h_layout.addStretch()
        cat_layout.addWidget(cat_hdr)
        
        popular_subjects = self.documente_service.get_popular_subjects()
        for subj, count in popular_subjects:
            row = QHBoxLayout()
            row.setContentsMargins(5, 4, 5, 4)
            
            s_lbl = QLabel(subj)
            s_lbl.setFont(qfont(FONTS["body_exam"]))
            s_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            row.addWidget(s_lbl)
            
            row.addStretch()
            
            c_lbl = QLabel(str(count))
            c_lbl.setFont(qfont(FONTS["small_bold_exam"]))
            c_lbl.setAlignment(Qt.AlignCenter)
            c_lbl.setStyleSheet(f"""
                background-color: #DCF0FF;
                color: {COLORS['primary']};
                border-radius: 6px;
                padding: 2px 8px;
                border: none;
            """)
            row.addWidget(c_lbl)
            
            cat_layout.addLayout(row)
            
        btn_all_cat = QPushButton("Xem tất cả môn học →")
        btn_all_cat.setFixedHeight(36)
        btn_all_cat.setFont(qfont(FONTS["body_bold_exam"]))
        btn_all_cat.setCursor(QCursor(Qt.PointingHandCursor))
        btn_all_cat.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: none;
                text-align: left;
            }}
            QPushButton:hover {{
                color: #357FE0;
            }}
        """)
        cat_layout.addWidget(btn_all_cat)
        
        self.right_layout.addWidget(cat_card)
