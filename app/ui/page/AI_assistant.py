from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QVBoxLayout, QWidget, QSizePolicy
)

from config import COLORS, FONTS

def qfont(font_tuple):
    family = font_tuple[0]
    size = font_tuple[1]
    weight = QFont.Bold if len(font_tuple) > 2 and font_tuple[2] == "bold" else QFont.Normal
    f = QFont(family, size)
    f.setWeight(weight)
    return f

class AIAssistantPage(QFrame):
    TOOLS = [
        ("🧮", "#FEF3C7", "Giải toán",           "Giải bài tập, chứng minh"),
        ("📄", "#DCFCE7", "Tóm tắt tài liệu",    "Tóm tắt nhanh nội dung"),
        ("🌐", "#EDE9FE", "Dịch thuật",           "Dịch văn bản, tài liệu"),
        ("💡", "#DBEAFE", "Hỏi đáp kiến thức",   "Giải đáp mọi câu hỏi"),
        ("📝", "#FFE4E6", "Tạo đề ôn tập",        "Tạo đề cương, trắc nghiệm"),
    ]

    HISTORY = [
        ("Giải toán giới hạn hàm số",      "10:34"),
        ("Tóm tắt bài thơ Tây Tiến",       "Hôm qua"),
        ("Lập kế hoạch học tập tuần",      "2 ngày trước"),
        ("Giải bài tập Vật lý lớp 11",     "3 ngày trước"),
        ("Dịch đoạn văn tiếng Anh",        "5 ngày trước"),
    ]

    SUGGESTIONS_TODAY = [
        "Ôn tập chủ đề Giới hạn – Toán 11",
        "Làm 10 câu trắc nghiệm Vật lý",
        "Tóm tắt chương 3 – Hóa học 12",
    ]

    QUICK_PROMPTS = [
        "Giải bài toán này giúp mình",
        "Tóm tắt nội dung tài liệu",
        "Lập kế hoạch học tập",
        "Giải thích khái niệm",
        "Ôn tập trắc nghiệm",
    ]

    def __init__(self, master, ai_service=None):
        super().__init__(master)
        self.ai_service = ai_service
        
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Cột trái (chat)
        self.left_col = QFrame()
        self.left_col.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout(self.left_col)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(15)
        
        # Cột phải (panel)
        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setFixedWidth(340)
        self.right_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }")
        
        self.right_content = QWidget()
        self.right_content.setStyleSheet("background: transparent;")
        self.right_layout = QVBoxLayout(self.right_content)
        self.right_layout.setContentsMargins(0, 0, 10, 0)
        self.right_layout.setSpacing(20)
        self.right_layout.setAlignment(Qt.AlignTop)
        self.right_scroll.setWidget(self.right_content)
        
        main_layout.addWidget(self.left_col, 1)
        main_layout.addWidget(self.right_scroll, 0)
        
        self.create_header()
        self.create_quick_prompts()
        self.create_chat_area()
        self.create_input_box()
        self.create_right_panel()

    def make_card(self):
        card = QFrame()
        card.setObjectName("chat_card")
        card.setStyleSheet(f"""
            #chat_card {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        return card

    def create_header(self):
        header = QFrame()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        title = QLabel("Trợ lý AI")
        title.setFont(qfont(FONTS["h1_ai"]))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        sub = QLabel("Hỏi gì cũng được, AI luôn sẵn sàng giúp bạn!")
        sub.setFont(qfont(FONTS["body_ai"]))
        sub.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        
        title_box.addWidget(title)
        title_box.addWidget(sub)
        
        h_layout.addLayout(title_box)
        h_layout.addStretch()
        
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        
        for text, is_primary in [
            ("🕐 Lịch sử chat", False),
            ("📋 Ghi chú",       False),
            ("+ Chat mới",        True),
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            if is_primary:
                btn.setFont(qfont(FONTS["body_bold_ai"]))
                btn.setStyleSheet(f"""
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
            else:
                btn.setFont(qfont(FONTS["body_ai"]))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['card']};
                        color: {COLORS['text_primary']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                        padding: 0 15px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['hover']};
                    }}
                """)
            btn_box.addWidget(btn)
            
        h_layout.addLayout(btn_box)
        self.left_layout.addWidget(header)

    def create_quick_prompts(self):
        card = self.make_card()
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(15, 10, 15, 10)
        c_layout.setSpacing(10)
        
        lbl = QLabel("Gợi ý nhanh")
        lbl.setFont(qfont(FONTS["body_bold_ai"]))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        c_layout.addWidget(lbl)
        
        # Tạo Scroll Area để chứa các nút gợi ý, tránh việc bị ép size làm khuyết chữ
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(45) # Chiều cao đủ cho nút 32px + một chút padding
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Ẩn thanh cuộn để giao diện sạch sẽ
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        chips_row = QHBoxLayout(scroll_content)
        chips_row.setContentsMargins(0, 0, 0, 0)
        chips_row.setSpacing(10)
        chips_row.setAlignment(Qt.AlignLeft)
        
        for prompt in self.QUICK_PROMPTS:
            btn = QPushButton(prompt)
            btn.setFixedHeight(32)
            # Cho phép nút tự mở rộng theo độ dài văn bản
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            btn.setFont(qfont(FONTS["small_ai"]))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['card']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 16px;
                    padding: 0 15px;
                }}
                QPushButton:hover {{
                    background-color: #DBEAFE;
                    border: 1px solid {COLORS['primary']};
                }}
            """)
            chips_row.addWidget(btn)
        
        chips_row.addStretch() # Đẩy các nút về bên trái
        scroll.setWidget(scroll_content)
        c_layout.addWidget(scroll)
        
        self.left_layout.addWidget(card)

    def create_chat_area(self):
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: transparent; } QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 4px; }")
        
        self.chat_content = QWidget()
        self.chat_content.setStyleSheet("background: transparent;")
        self.chat_area_layout = QVBoxLayout(self.chat_content)
        self.chat_area_layout.setContentsMargins(0, 0, 10, 0)
        self.chat_area_layout.setSpacing(15)
        self.chat_area_layout.setAlignment(Qt.AlignTop)
        
        self.chat_scroll.setWidget(self.chat_content)
        self.left_layout.addWidget(self.chat_scroll, 1) # stretch 1
        
        # Add samples
        self.add_user_message(
            "Bạn có thể giải bài toán này giúp mình được không?",
            timestamp="10:30",
            attachment={"name": "de_thi_toan_hk2_2024.pdf", "size": "1.2 MB"},
        )
        self.add_ai_message(
            "Tất nhiên rồi! Mình sẽ giúp bạn giải bài toán trong file bạn vừa gửi.\n\n"
            "Câu 1:\nĐề bài: Tính giới hạn của hàm số khi x tiến tới 2\n\n"
            "Lời giải:\nTa có thể rút gọn biểu thức rồi thay giá trị x = 2.\n"
            "Kết quả cuối cùng là 4.",
            timestamp="10:32"
        )
        self.add_user_message(
            "Giải thích giúp mình tại sao lại khử được x - 2 ở tử và mẫu?",
            timestamp="10:33"
        )
        self.add_ai_message(
            "Ta có phép khử x − 2 ở tử và mẫu vì khi xét giới hạn x tiến tới 2 "
            "thì x không bằng 2. Do đó x − 2 khác 0 trong quá trình biến đổi.",
            timestamp="10:34"
        )

    def add_user_message(self, text, timestamp="", attachment=None):
        wrapper = QFrame()
        w_layout = QHBoxLayout(wrapper)
        w_layout.setContentsMargins(0, 0, 0, 0)
        
        w_layout.addStretch() # Push to right
        
        bubble_wrap = QVBoxLayout()
        bubble_wrap.setAlignment(Qt.AlignRight)
        
        bubble = QFrame()
        bubble.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.get('chat_user', '#EAF2FF')};
                border-radius: 14px;
            }}
        """)
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(15, 12, 15, 12)
        b_layout.setSpacing(8)
        
        lbl = QLabel(text)
        lbl.setFont(qfont(FONTS["body_ai"]))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; background: transparent;")
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(450)
        b_layout.addWidget(lbl)
        
        if attachment:
            att_card = QFrame()
            att_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['card']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 10px;
                }}
            """)
            a_layout = QHBoxLayout(att_card)
            a_layout.setContentsMargins(10, 10, 10, 10)
            a_layout.setSpacing(10)
            
            pdf_icon = QLabel("PDF")
            pdf_icon.setFixedSize(40, 40)
            pdf_icon.setAlignment(Qt.AlignCenter)
            pdf_icon.setStyleSheet("background-color: #FDDEDE; color: #E74C3C; border-radius: 8px; font-weight: bold; border: none;")
            a_layout.addWidget(pdf_icon)
            
            info = QVBoxLayout()
            name_lbl = QLabel(attachment["name"])
            name_lbl.setFont(qfont(FONTS["small_bold_ai"]))
            name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; background: transparent;")
            info.addWidget(name_lbl)
            
            size_lbl = QLabel(attachment["size"])
            size_lbl.setFont(qfont(FONTS["small_ai"]))
            size_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
            info.addWidget(size_lbl)
            a_layout.addLayout(info, 1)
            
            eye_icon = QLabel("👁")
            eye_icon.setStyleSheet("font-size: 15px; border: none; background: transparent;")
            a_layout.addWidget(eye_icon)
            
            b_layout.addWidget(att_card)
            
        time_lbl = QLabel(timestamp)
        time_lbl.setFont(qfont(FONTS["small_ai"]))
        time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
        time_lbl.setAlignment(Qt.AlignRight)
        
        bubble_wrap.addWidget(bubble)
        bubble_wrap.addWidget(time_lbl)
        
        w_layout.addLayout(bubble_wrap)
        self.chat_area_layout.addWidget(wrapper)

    def add_ai_message(self, text, timestamp=""):
        wrapper = QFrame()
        w_layout = QHBoxLayout(wrapper)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        avatar = QLabel("🤖")
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background-color: #DBEAFE; border-radius: 19px; font-size: 17px;")
        
        av_layout = QVBoxLayout()
        av_layout.addWidget(avatar)
        av_layout.addStretch()
        w_layout.addLayout(av_layout)
        
        bubble_wrap = QVBoxLayout()
        
        bubble = QFrame()
        bubble.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.get('chat_ai', '#FFFFFF')};
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(15, 12, 15, 12)
        b_layout.setSpacing(8)
        
        lbl = QLabel(text)
        lbl.setFont(qfont(FONTS["body_ai"]))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; background: transparent;")
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(500)
        b_layout.addWidget(lbl)
        
        bottom = QHBoxLayout()
        time_lbl = QLabel(timestamp)
        time_lbl.setFont(qfont(FONTS["small_ai"]))
        time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; background: transparent;")
        bottom.addWidget(time_lbl)
        bottom.addStretch()
        
        for label in ["📋 Copy", "👍 Like", "👎 Dislike"]:
            btn = QPushButton(label)
            btn.setFixedHeight(26)
            btn.setFont(qfont(FONTS["small_ai"]))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: none;
                    padding: 0 5px;
                }}
                QPushButton:hover {{
                    color: {COLORS['primary']};
                    background-color: {COLORS['hover']};
                    border-radius: 4px;
                }}
            """)
            bottom.addWidget(btn)
            
        b_layout.addLayout(bottom)
        bubble_wrap.addWidget(bubble)
        
        w_layout.addLayout(bubble_wrap)
        w_layout.addStretch() # Push to left
        self.chat_area_layout.addWidget(wrapper)

    def create_input_box(self):
        container = QFrame()
        container.setObjectName("input_card")
        container.setStyleSheet(f"""
            #input_card {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
            }}
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setSpacing(10)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập câu hỏi của bạn...")
        self.text_input.setFixedHeight(60)
        self.text_input.setFont(qfont(FONTS["body_ai"]))
        self.text_input.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background: transparent;
                color: {COLORS['text_primary']};
            }}
        """)
        c_layout.addWidget(self.text_input)
        
        tool_row = QHBoxLayout()
        for text in ["+", "📎 Đính kèm", "🖼 Tải hình ảnh"]:
            btn = QPushButton(text)
            btn.setFixedHeight(32)
            btn.setFont(qfont(FONTS["small_ai"]))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 0 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['hover']};
                }}
            """)
            tool_row.addWidget(btn)
            
        tool_row.addStretch()
        
        btn_mic = QPushButton("🎙")
        btn_mic.setFixedSize(36, 36)
        btn_mic.setFont(qfont(("Segoe UI", 13)))
        btn_mic.setCursor(QCursor(Qt.PointingHandCursor))
        btn_mic.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 18px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        tool_row.addWidget(btn_mic)
        
        btn_send = QPushButton("➤")
        btn_send.setFixedSize(38, 38)
        btn_send.setFont(qfont(("Segoe UI", 13, "bold")))
        btn_send.setCursor(QCursor(Qt.PointingHandCursor))
        btn_send.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 19px;
            }}
            QPushButton:hover {{
                background-color: #357FE0;
            }}
        """)
        tool_row.addWidget(btn_send)
        
        c_layout.addLayout(tool_row)
        self.left_layout.addWidget(container)
        
        disclaimer = QLabel("AI có thể mắc lỗi. Hãy kiểm tra thông tin quan trọng.")
        disclaimer.setFont(qfont(FONTS["small_ai"]))
        disclaimer.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")
        self.left_layout.addWidget(disclaimer)

    def create_right_panel(self):
        # Card Lịch sử hội thoại
        hist_card = self.make_card()
        h_layout = QVBoxLayout(hist_card)
        h_layout.setContentsMargins(10, 10, 10, 10)
        h_layout.setSpacing(10)
        
        hdr = QFrame()
        hdr.setStyleSheet(f"background-color: {COLORS['primary']}; border-radius: 8px;")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(10, 8, 10, 8)
        lbl = QLabel("Lịch sử hội thoại")
        lbl.setFont(qfont(FONTS["h3_ai"]))
        lbl.setStyleSheet("color: white; background: transparent; border: none;")
        hdr_layout.addWidget(lbl)
        hdr_layout.addStretch()
        h_layout.addWidget(hdr)
        
        for title, time in self.HISTORY:
            item = QFrame()
            item.setCursor(QCursor(Qt.PointingHandCursor))
            item.setStyleSheet(f"""
                QFrame:hover {{
                    background-color: {COLORS['hover']};
                    border-radius: 6px;
                }}
            """)
            i_layout = QVBoxLayout(item)
            i_layout.setContentsMargins(8, 6, 8, 6)
            i_layout.setSpacing(2)
            
            t_lbl = QLabel(title)
            t_lbl.setFont(qfont(FONTS["small_bold_ai"]))
            t_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
            t_lbl.setWordWrap(True)
            
            time_lbl = QLabel(time)
            time_lbl.setFont(qfont(FONTS["small_ai"]))
            time_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")
            
            i_layout.addWidget(t_lbl)
            i_layout.addWidget(time_lbl)
            h_layout.addWidget(item)
            
        btn_more = QPushButton("Xem thêm ↓")
        btn_more.setFixedHeight(32)
        btn_more.setFont(qfont(FONTS["small_bold_ai"]))
        btn_more.setCursor(QCursor(Qt.PointingHandCursor))
        btn_more.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                color: #357FE0;
            }}
        """)
        h_layout.addWidget(btn_more)
        self.right_layout.addWidget(hist_card)
        
        # Card Gợi ý hôm nay
        sug_card = self.make_card()
        s_layout = QVBoxLayout(sug_card)
        s_layout.setContentsMargins(10, 10, 10, 15)
        s_layout.setSpacing(10)
        
        s_hdr = QFrame()
        s_hdr.setStyleSheet(f"background-color: {COLORS['primary']}; border-radius: 8px;")
        sh_layout = QHBoxLayout(s_hdr)
        sh_layout.setContentsMargins(10, 8, 10, 8)
        slbl = QLabel("Gợi ý hôm nay")
        slbl.setFont(qfont(FONTS["h3_ai"]))
        slbl.setStyleSheet("color: white; background: transparent; border: none;")
        sh_layout.addWidget(slbl)
        sh_layout.addStretch()
        s_layout.addWidget(s_hdr)
        
        for sug in self.SUGGESTIONS_TODAY:
            row = QHBoxLayout()
            row.setContentsMargins(8, 2, 8, 2)
            dot = QLabel("›")
            dot.setFont(qfont(FONTS["body_bold_ai"]))
            dot.setStyleSheet(f"color: {COLORS['primary']}; background: transparent; border: none;")
            
            txt = QLabel(sug)
            txt.setFont(qfont(FONTS["small_ai"]))
            txt.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
            txt.setWordWrap(True)
            
            row.addWidget(dot)
            row.addWidget(txt, 1)
            s_layout.addLayout(row)
            
        self.right_layout.addWidget(sug_card)
