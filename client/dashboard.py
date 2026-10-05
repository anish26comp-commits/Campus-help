from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from network_client import get_my_requests
from request_page import NewRequestPage
from requests_page import MyRequestsPage
from styles import apply_shadow, set_priority_badge, set_status_badge


class StudentDashboard(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.nav_buttons = []

        self.setWindowTitle("Campus Help — Student Dashboard")
        self.resize(1280, 800)
        self.setMinimumSize(1050, 700)

        self.setup_ui()
        self.refresh_dashboard()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.create_sidebar())

        content = QWidget()
        content.setObjectName("pageBackground")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 28, 32, 28)
        content_layout.setSpacing(16)

        self.pages = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.request_page = NewRequestPage(self.user["id"])
        self.requests_page = MyRequestsPage(self.user["id"])

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.request_page)
        self.pages.addWidget(self.requests_page)

        self.request_page.request_submitted.connect(self.handle_request_submitted)

        content_layout.addWidget(self.pages, 1)
        root.addWidget(content, 1)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(238)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 23, 18, 20)
        layout.setSpacing(7)

        logo = QLabel("CH")
        logo.setObjectName("sidebarLogo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(50, 50)
        layout.addWidget(logo, alignment=Qt.AlignLeft)

        brand = QLabel("Campus Help")
        brand.setObjectName("sidebarBrand")
        layout.addWidget(brand)

        subtitle = QLabel("STUDENT PORTAL")
        subtitle.setObjectName("sidebarSubtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(25)

        self.dashboard_nav = self.create_nav_button("⌂   Dashboard", 0)
        self.new_request_nav = self.create_nav_button("＋   New Help Request", 1)
        self.my_requests_nav = self.create_nav_button("▣   My Requests", 2)

        for button in (self.dashboard_nav, self.new_request_nav, self.my_requests_nav):
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch()

        user_card = QFrame()
        user_card.setObjectName("sidebarUserCard")
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(12, 12, 12, 12)
        user_layout.setSpacing(3)

        avatar = QLabel(self.user.get("name", "S")[:1].upper())
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(34, 34)
        avatar.setStyleSheet(
            "background: #312E81; color: #FFFFFF; border-radius: 10px; font-weight: 800;"
        )

        header_row = QHBoxLayout()
        header_row.addWidget(avatar)

        text_col = QVBoxLayout()
        name = QLabel(self.user.get("name", "Student"))
        name.setObjectName("sidebarUserName")
        email = QLabel(self.user.get("email", ""))
        email.setObjectName("sidebarUserEmail")
        email.setWordWrap(True)
        text_col.addWidget(name)
        text_col.addWidget(email)
        header_row.addLayout(text_col, 1)
        user_layout.addLayout(header_row)

        layout.addWidget(user_card)
        layout.addSpacing(8)

        logout = QPushButton("↪   Logout")
        logout.setObjectName("dangerButton")
        logout.setCursor(Qt.PointingHandCursor)
        logout.clicked.connect(self.logout)
        logout.setMinimumHeight(40)
        layout.addWidget(logout)

        self.set_active_nav(0)
        return sidebar

    def create_nav_button(self, text, page_index):
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self.show_page(page_index))
        return button

    def set_active_nav(self, index):
        for button_index, button in enumerate(self.nav_buttons):
            button.setProperty("active", button_index == index)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        header_row = QHBoxLayout()
        header_col = QVBoxLayout()
        header_col.setSpacing(4)

        greeting = QLabel(f"Good to see you, {self.user['name'].split()[0]} 👋")
        greeting.setObjectName("pageTitle")
        header_col.addWidget(greeting)

        subtitle = QLabel("Everything you need to keep track of your campus support requests.")
        subtitle.setObjectName("pageSubtitle")
        header_col.addWidget(subtitle)

        header_row.addLayout(header_col)
        header_row.addStretch()

        refresh = QPushButton("↻  Refresh")
        refresh.setObjectName("secondaryButton")
        refresh.setCursor(Qt.PointingHandCursor)
        refresh.setToolTip("Refresh your latest request information")
        refresh.clicked.connect(self.refresh_dashboard)
        header_row.addWidget(refresh, alignment=Qt.AlignTop)
        layout.addLayout(header_row)

        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.pending_value = QLabel("0")
        self.progress_value = QLabel("0")
        self.resolved_value = QLabel("0")

        stats.addWidget(self.create_stat_card("PENDING", self.pending_value, "Waiting for review", "⏳"))
        stats.addWidget(self.create_stat_card("IN PROGRESS", self.progress_value, "Currently handled", "↻"))
        stats.addWidget(self.create_stat_card("RESOLVED", self.resolved_value, "Successfully completed", "✓"))
        layout.addLayout(stats)

        quick_card = QFrame()
        quick_card.setObjectName("quickCard")
        quick_layout = QHBoxLayout(quick_card)
        quick_layout.setContentsMargins(21, 17, 21, 17)
        quick_layout.setSpacing(15)

        icon = QLabel("＋")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(40, 40)
        icon.setStyleSheet("background: rgba(255,255,255,0.13); color: white; border-radius: 12px; font-size: 20px; font-weight: 800;")
        quick_layout.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title = QLabel("Need help with something?")
        title.setObjectName("quickTitle")
        sub = QLabel("Create a request and our support team can take it from there.")
        sub.setObjectName("quickSubtitle")
        text_col.addWidget(title)
        text_col.addWidget(sub)
        quick_layout.addLayout(text_col, 1)

        create_button = QPushButton("Create Request  →")
        create_button.setObjectName("primaryButton")
        create_button.setCursor(Qt.PointingHandCursor)
        create_button.setStyleSheet("QPushButton#primaryButton { background: #FFFFFF; color: #4338CA; } QPushButton#primaryButton:hover { background: #EEF2FF; }")
        create_button.clicked.connect(lambda: self.show_page(1))
        quick_layout.addWidget(create_button, alignment=Qt.AlignVCenter)
        layout.addWidget(quick_card)

        recent_header = QHBoxLayout()
        title = QLabel("Recent Requests")
        title.setStyleSheet("font-size: 17px; font-weight: 800; color: #111827;")
        recent_header.addWidget(title)
        recent_header.addStretch()
        hint = QLabel("Double-click a row to open My Requests")
        hint.setObjectName("smallText")
        recent_header.addWidget(hint)
        layout.addLayout(recent_header)

        table_card = QFrame()
        table_card.setObjectName("card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(8, 8, 8, 8)

        self.recent_table = self.create_table(5)
        self.recent_table.setHorizontalHeaderLabels(["ID", "SUBJECT", "CATEGORY", "STATUS", "CREATED"])
        self.recent_table.cellDoubleClicked.connect(lambda *_: self.show_page(2))
        table_layout.addWidget(self.recent_table)
        layout.addWidget(table_card, 1)
        apply_shadow(table_card, blur_radius=24, y_offset=6)

        return page

    def create_stat_card(self, title, value_label, subtitle, icon_text):
        card = QFrame()
        card.setObjectName("statCard")
        row = QHBoxLayout(card)
        row.setContentsMargins(15, 13, 15, 13)
        row.setSpacing(12)

        accent = QFrame()
        accent.setObjectName("statAccent")
        accent.setFixedSize(38, 38)
        accent_layout = QVBoxLayout(accent)
        accent_layout.setContentsMargins(0, 0, 0, 0)
        icon = QLabel(icon_text)
        icon.setAlignment(Qt.AlignCenter)
        accent_layout.addWidget(icon)
        row.addWidget(accent, alignment=Qt.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(1)
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        value_label.setObjectName("statValue")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("statSubtitle")
        col.addWidget(title_label)
        col.addWidget(value_label)
        col.addWidget(subtitle_label)
        row.addLayout(col, 1)
        return card

    @staticmethod
    def create_table(columns):
        table = QTableWidget()
        table.setColumnCount(columns)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.setWordWrap(False)
        table.setMinimumHeight(220)

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setFixedHeight(36)
        table.verticalHeader().setDefaultSectionSize(42)
        return table

    def fill_status_cell(self, table, row, column, status):
        label = QLabel(status)
        label.setObjectName("statusBadge")
        set_status_badge(label, status)
        table.setCellWidget(row, column, label)

    def show_page(self, page_index):
        self.pages.setCurrentIndex(page_index)
        self.set_active_nav(page_index)

        if page_index == 2:
            self.requests_page.load_requests()
        elif page_index == 0:
            self.refresh_dashboard()

    def handle_request_submitted(self):
        self.requests_page.load_requests()
        self.refresh_dashboard()
        self.show_page(2)

    def refresh_dashboard(self):
        response = get_my_requests(self.user["id"])
        if not response.get("success"):
            return

        requests = response.get("requests", [])
        pending = sum(1 for item in requests if item.get("status") == "Pending")
        progress = sum(1 for item in requests if item.get("status") == "In Progress")
        resolved = sum(1 for item in requests if item.get("status") == "Resolved")

        self.pending_value.setText(str(pending))
        self.progress_value.setText(str(progress))
        self.resolved_value.setText(str(resolved))

        recent = requests[:6]
        self.recent_table.setRowCount(len(recent))

        for row, request in enumerate(recent):
            items = [
                f"#{request['request_id']}",
                request["subject"],
                request["category"],
                request["status"],
                request["created_at"],
            ]
            for col, value in enumerate(items):
                if col == 3:
                    self.fill_status_cell(self.recent_table, row, col, request["status"])
                else:
                    item = QTableWidgetItem(str(value))
                    if col == 0:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.recent_table.setItem(row, col, item)

        header = self.recent_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def logout(self):
        self.logout_requested.emit()
        self.close()
