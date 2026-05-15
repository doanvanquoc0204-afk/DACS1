from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget
)

from config import COLORS, FONTS

DAY_PALETTE = [
    ("#EEF2FF", "#4F46E5"),  # Thứ 2 - Indigo
    ("#F0FDF4", "#16A34A"),  # Thứ 3 - Green
    ("#FFF7ED", "#EA580C"),  # Thứ 4 - Orange
    ("#FAF5FF", "#9333EA"),  # Thứ 5 - Purple
    ("#FFF1F2", "#E11D48"),  # Thứ 6 - Rose
    ("#F0FDFA", "#0D9488"),  # Thứ 7 - Teal
    ("#FFFBEB", "#D97706"),  # Chủ nhật - Amber
]

PERIOD_INFO = {
    "Sáng":  {"icon": "☀️",  "bg": "#FEFCE8", "fg": "#854D0E"},
    "Chiều": {"icon": "🌤️", "bg": "#FFF7ED", "fg": "#9A3412"},
    "Tối":   {"icon": "🌙",  "bg": "#EFF6FF", "fg": "#1E40AF"},
}

DAY_LABELS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

def get_period(start_str: str) -> str:
    h = int(start_str.split(":")[0])
    if h < 12:  return "Sáng"
    if h < 18:  return "Chiều"
    return "Tối"

def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class CenterPanel(QFrame):
    def __init__(self, master, study_service, ai_service):
        super().__init__(master)
        self.study_service = study_service
        self.ai_service = ai_service
        self._selected_day = 0
        self._day_buttons = []
        
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left column
        self.left_frame = QFrame()
        self.left_frame.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(self.left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Right column
        self.right_frame = QFrame()
        self.right_frame.setStyleSheet("background: transparent;")
        self.right_frame.setFixedWidth(360) # Tăng chiều rộng cột phải một chút
        right_layout = QVBoxLayout(self.right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)
        
        main_layout.addWidget(self.left_frame, 1)
        main_layout.addWidget(self.right_frame, 0)
        
        self.create_header(left_layout)
        self.create_week_bar(left_layout)
        self.create_schedule_list(left_layout)
        self.create_bottom_cards(left_layout)
        
        self.create_today_tasks(right_layout)
        self.create_notifications(right_layout)
        right_layout.addStretch()

    def make_card(self):
        card = QFrame()
        card.setObjectName("card_frame")
        card.setStyleSheet(f"""
            #card_frame {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        return card

    def create_header(self, parent_layout):
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Lịch học tập")
        title.setFont(qfont(FONTS["h1_center"]))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        h_layout.addWidget(title)
        
        h_layout.addStretch()
        
        btn_style = f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """
        
        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(36, 36)
        btn_prev.setStyleSheet(btn_style)
        btn_prev.setCursor(QCursor(Qt.PointingHandCursor))
        h_layout.addWidget(btn_prev)
        
        btn_next = QPushButton(">")
        btn_next.setFixedSize(36, 36)
        btn_next.setStyleSheet(btn_style)
        btn_next.setCursor(QCursor(Qt.PointingHandCursor))
        h_layout.addWidget(btn_next)
        
        date_lbl = QLabel("20 thg 4 – 26 thg 4, 2026")
        date_lbl.setFont(qfont(FONTS["body_bold_center"]))
        date_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; margin: 0 10px;")
        h_layout.addWidget(date_lbl)
        
        btn_today = QPushButton("Hôm nay")
        btn_today.setFixedHeight(36)
        btn_today.setStyleSheet(btn_style)
        btn_today.setCursor(QCursor(Qt.PointingHandCursor))
        h_layout.addWidget(btn_today)
        
        # Removed Segmented Button (Tuần / Tháng)
        
        btn_add = QPushButton("+ Thêm lịch học")
        btn_add.setFixedHeight(36)
        btn_add.setFont(qfont(FONTS["body_bold_center"]))
        btn_add.setCursor(QCursor(Qt.PointingHandCursor))
        btn_add.setStyleSheet(f"""
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
        h_layout.addWidget(btn_add)
        
        parent_layout.addWidget(header)

    def create_week_bar(self, parent_layout):
        bar_outer = self.make_card()
        bar_layout = QHBoxLayout(bar_outer)
        bar_layout.setContentsMargins(10, 10, 10, 10)
        bar_layout.setSpacing(10)
        
        schedule = self.study_service.get_schedule()
        
        for i, label in enumerate(DAY_LABELS):
            if i < len(schedule):
                date_part = schedule[i]["date"].split("/")
                date_str  = f"{date_part[0]}/{date_part[1]}"
            else:
                date_str = ""
            
            btn = QPushButton(f"{label}\n{date_str}")
            btn.setFont(qfont(FONTS["small_bold_center"]))
            btn.setFixedHeight(65)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked=False, idx=i: self.select_day(idx))
            self._day_buttons.append(btn)
            bar_layout.addWidget(btn, 1) # Thêm stretch để chia đều không gian
            
        self.refresh_day_styles()
        parent_layout.addWidget(bar_outer)

    def select_day(self, idx):
        self._selected_day = idx
        self.refresh_day_styles()
        self.reload_schedule()

    def refresh_day_styles(self):
        for i, btn in enumerate(self._day_buttons):
            if i == self._selected_day:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['primary']};
                        color: white;
                        border: none;
                        border-radius: 10px;
                        text-align: center;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text_secondary']};
                        border: none;
                        border-radius: 10px;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['hover']};
                    }}
                """)

    def create_schedule_list(self, parent_layout):
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 10, 0) # Padding phải cho thanh cuộn
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        self._scroll.setWidget(self.scroll_content)
        parent_layout.addWidget(self._scroll, 1) # Cho phép mở rộng chiều cao
        
        self.reload_schedule()

    def reload_schedule(self):
        # Clear layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
                
        self.load_day_schedule(self._selected_day)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def load_day_schedule(self, day_idx):
        schedule = self.study_service.get_schedule()
        if day_idx >= len(schedule):
            lbl = QLabel("Không có lịch học")
            lbl.setFont(qfont(FONTS["body_center"]))
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
            lbl.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(lbl)
            return

        day_data = schedule[day_idx]
        bg_day, accent = DAY_PALETTE[day_idx % len(DAY_PALETTE)]

        sessions = day_data.get("sessions", [])
        grouped  = {"Sáng": [], "Chiều": [], "Tối": []}
        for s in sessions:
            grouped[get_period(s["start"])].append(s)

        for period in ["Sáng", "Chiều", "Tối"]:
            if not grouped[period]:
                continue
            p_info = PERIOD_INFO[period]

            # Nhãn buổi (Sáng/Chiều/Tối)
            p_row = QFrame()
            p_row.setStyleSheet("background: transparent;")
            p_layout = QHBoxLayout(p_row)
            p_layout.setContentsMargins(0, 10, 0, 5)
            
            badge = QLabel(f"  {p_info['icon']} {period}  ")
            badge.setFont(qfont(FONTS["small_bold_center"]))
            badge.setStyleSheet(f"""
                background-color: {p_info['bg']};
                color: {p_info['fg']};
                border-radius: 8px;
                padding: 4px 8px;
            """)
            p_layout.addWidget(badge)
            p_layout.addStretch()
            self.scroll_layout.addWidget(p_row)

            # Các tiết học trong buổi
            for session in grouped[period]:
                self.build_session_card(session, bg_day, accent)

        if not sessions:
            lbl = QLabel("Không có lịch học hôm nay 🎉")
            lbl.setFont(qfont(FONTS["body_center"]))
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
            lbl.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(lbl)

    def build_session_card(self, session, bg_day, accent):
        card = self.make_card()
        card.setFixedHeight(95)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Color bar
        bar = QFrame()
        bar.setFixedWidth(5)
        bar.setStyleSheet(f"background-color: {accent}; border-radius: 2px;")
        layout.addWidget(bar)
        
        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setAlignment(Qt.AlignVCenter)
        
        time_lbl = QLabel(f"⏱  {session['start']} – {session['end']}")
        time_lbl.setFont(qfont(FONTS["small_center"]))
        time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        content_layout.addWidget(time_lbl)
        
        subj_layout = QHBoxLayout()
        subj_layout.setSpacing(8)
        dot = QLabel("•")
        dot.setStyleSheet(f"color: {accent}; font-size: 15px; border: none; font-weight: bold;")
        subj_lbl = QLabel(session["subject"])
        subj_lbl.setFont(qfont(FONTS["body_bold_center"]))
        subj_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        subj_layout.addWidget(dot)
        subj_layout.addWidget(subj_lbl)
        subj_layout.addStretch()
        content_layout.addLayout(subj_layout)
        
        room_lbl = QLabel(f"📍  {session['room']}")
        room_lbl.setFont(qfont(FONTS["small_center"]))
        room_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        content_layout.addWidget(room_lbl)
        
        layout.addLayout(content_layout, 1)
        
        # Right menu (Loại lớp + Nút ⋮)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        type_lbl = QLabel(session.get("type", "LT"))
        type_lbl.setFont(qfont(FONTS["small_bold_center"]))
        type_lbl.setAlignment(Qt.AlignCenter)
        type_lbl.setStyleSheet(f"""
            background-color: {bg_day};
            color: {accent};
            border-radius: 6px;
            padding: 4px 10px;
            border: none;
        """)
        right_layout.addWidget(type_lbl)
        
        more_lbl = QLabel("⋮")
        more_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 17px; border: none; font-weight: bold;")
        more_lbl.setAlignment(Qt.AlignCenter)
        more_lbl.setCursor(QCursor(Qt.PointingHandCursor))
        right_layout.addWidget(more_lbl)
        
        layout.addLayout(right_layout)
        
        self.scroll_layout.addWidget(card)

    def create_bottom_cards(self, parent_layout):
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Gợi ý AI
        ai_card = self.make_card()
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setContentsMargins(15, 15, 15, 15)
        ai_layout.setSpacing(10)
        
        ai_header = QFrame()
        ai_header.setStyleSheet(f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;")
        ai_h_layout = QHBoxLayout(ai_header)
        ai_h_layout.setContentsMargins(10, 8, 10, 8)
        icon_ai = QLabel("✨")
        icon_ai.setFont(qfont(FONTS["h3_center"]))
        icon_ai.setStyleSheet("color: white; background: transparent;")
        title_ai = QLabel("Gợi ý học tập từ AI")
        title_ai.setFont(qfont(FONTS["h3_center"]))
        title_ai.setStyleSheet("color: white; border: none; background: transparent;")
        ai_h_layout.addWidget(icon_ai)
        ai_h_layout.addWidget(title_ai)
        ai_h_layout.addStretch()
        ai_layout.addWidget(ai_header)
        
        sug_text = self.ai_service.get_study_suggestions()
        sug_lbl = QLabel(sug_text)
        sug_lbl.setWordWrap(True)
        sug_lbl.setFont(qfont(FONTS["small_center"]))
        sug_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        ai_layout.addWidget(sug_lbl, 1)
        
        btn_ai = QPushButton("Xem gợi ý")
        btn_ai.setFixedHeight(40)
        btn_ai.setFixedWidth(100)
        btn_ai.setFont(qfont(FONTS["body_bold_center"]))
        btn_ai.setCursor(QCursor(Qt.PointingHandCursor))
        btn_ai.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['primary']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        ai_layout.addWidget(btn_ai, 0, Qt.AlignLeft)
        
        bottom_layout.addWidget(ai_card, 1)
        
        # Thống kê
        stat_card = self.make_card()
        stat_layout = QVBoxLayout(stat_card)
        stat_layout.setContentsMargins(15, 15, 15, 15)
        stat_layout.setSpacing(10)
        
        stat_header = QFrame()
        stat_header.setStyleSheet(f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;")
        stat_h_layout = QHBoxLayout(stat_header)
        stat_h_layout.setContentsMargins(10, 8, 10, 8)
        title_stat = QLabel("Thống kê hàng tuần")
        title_stat.setFont(qfont(FONTS["h3_center"]))
        title_stat.setStyleSheet("color: white; border: none; background: transparent;")
        stat_h_layout.addWidget(title_stat)
        stat_h_layout.addStretch()
        stat_layout.addWidget(stat_header)
        
        stats = self.study_service.get_stats()
        
        stats_grid = QGridLayout()
        items = [
            ("số buổi", str(stats["total_sessions"])),
            ("Tự học", f"{stats['self_study_hours']}h"),
            ("Hoàn thành", f"{int(stats['completion']*100)}%")
        ]
        
        for i, (lbl, val) in enumerate(items):
            val_lbl = QLabel(val)
            val_lbl.setFont(qfont(FONTS["h2_center"]))
            val_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            
            desc_lbl = QLabel(lbl)
            desc_lbl.setFont(qfont(FONTS["small_center"]))
            desc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
            
            stats_grid.addWidget(val_lbl, 0, i)
            stats_grid.addWidget(desc_lbl, 1, i)
            
        stat_layout.addLayout(stats_grid)
        
        progress = QProgressBar()
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        progress.setValue(int(stats["completion"] * 100))
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['hover']};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        stat_layout.addWidget(progress)
        
        bottom_layout.addWidget(stat_card, 1)
        parent_layout.addLayout(bottom_layout)

    def create_today_tasks(self, parent_layout):
        card = self.make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        hdr = QFrame()
        hdr.setStyleSheet(f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(10, 8, 10, 8)
        title = QLabel("Nhiệm vụ hôm nay")
        title.setFont(qfont(FONTS["h3_center"]))
        title.setStyleSheet("color: white; border: none; background: transparent;")
        hdr_layout.addWidget(title)
        hdr_layout.addStretch()
        layout.addWidget(hdr)
        
        for task in self.study_service.get_tasks():
            t_row = QHBoxLayout()
            t_row.setSpacing(12)
            
            cb = QCheckBox()
            cb.setChecked(task["done"])
            cb.setCursor(QCursor(Qt.PointingHandCursor))
            cb.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 15px;
                    height: 15px;
                    border: 2px solid {COLORS['border']};
                    border-radius: 4px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {COLORS['primary']};
                    border: 2px solid {COLORS['primary']};
                }}
            """)
            t_row.addWidget(cb, 0, Qt.AlignTop)
            
            info_layout = QVBoxLayout()
            info_layout.setSpacing(4)
            name_lbl = QLabel(task["name"])
            name_lbl.setFont(qfont(FONTS["body_bold_center"]))
            name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            name_lbl.setWordWrap(True)
            info_layout.addWidget(name_lbl)
            
            meta_layout = QHBoxLayout()
            meta_layout.setSpacing(10)
            
            dl_lbl = QLabel(f"Deadline: {task['deadline']}")
            dl_lbl.setFont(qfont(FONTS["small_center"]))
            dl_lbl.setStyleSheet(f"color: {COLORS['danger']}; border: none;")
            meta_layout.addWidget(dl_lbl)
            
            meta_layout.addStretch()
            
            info_layout.addLayout(meta_layout)
            t_row.addLayout(info_layout, 1)
            layout.addLayout(t_row)
            
        btn_all = QPushButton("Xem tất cả nhiệm vụ →")
        btn_all.setFixedHeight(36)
        btn_all.setFont(qfont(FONTS["body_bold_center"]))
        btn_all.setCursor(QCursor(Qt.PointingHandCursor))
        btn_all.setStyleSheet(f"""
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
        layout.addWidget(btn_all)
        parent_layout.addWidget(card)

    def create_notifications(self, parent_layout):
        card = self.make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        hdr = QFrame()
        hdr.setStyleSheet(f"background-color: {COLORS.get('header_bg', '#62a6fc')}; border-radius: 8px; border: none;")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(10, 8, 10, 8)
        title = QLabel("Thông báo")
        title.setFont(qfont(FONTS["h3_center"]))
        title.setStyleSheet("color: white; border: none; background: transparent;")
        hdr_layout.addWidget(title)
        
        nots = self.study_service.get_notifications()
        badge = QLabel(str(len(nots)))
        badge.setFont(qfont(FONTS["small_bold_center"]))
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            background-color: {COLORS['danger']};
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            border: none;
        """)
        hdr_layout.addWidget(badge)
        hdr_layout.addStretch()
        layout.addWidget(hdr)
        
        for item in nots:
            row = QHBoxLayout()
            row.setSpacing(10)
            dot = QLabel("•")
            dot.setFont(qfont(FONTS["h2_center"]))
            dot.setStyleSheet(f"color: {COLORS['primary']}; border: none;")
            row.addWidget(dot, 0, Qt.AlignTop)
            
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            txt_lbl = QLabel(item["text"])
            txt_lbl.setFont(qfont(FONTS["body_center"]))
            txt_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
            txt_lbl.setWordWrap(True)
            info_layout.addWidget(txt_lbl)
            
            time_lbl = QLabel(item["time"])
            time_lbl.setFont(qfont(FONTS["small_center"]))
            time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
            info_layout.addWidget(time_lbl)
            
            row.addLayout(info_layout, 1)
            layout.addLayout(row)
            
        btn_all = QPushButton("Xem tất cả thông báo →")
        btn_all.setFixedHeight(36)
        btn_all.setFont(qfont(FONTS["body_bold_center"]))
        btn_all.setCursor(QCursor(Qt.PointingHandCursor))
        btn_all.setStyleSheet(f"""
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
        layout.addWidget(btn_all)
        parent_layout.addWidget(card)
