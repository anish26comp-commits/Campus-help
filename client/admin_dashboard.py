from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QTextEdit,
    QSplitter,
    QMessageBox,
    QListWidget,
    QFileDialog,
    QLineEdit,
    QScrollArea,
)

from network_client import (
    get_all_requests,
    get_request_details,
    update_request_status,
    add_request_update,
    download_attachment,
    logout_user,
)
from styles import set_priority_badge, set_status_badge, show_message


class AdminDashboard(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user):
        super().__init__()

        self.user = user
        self.selected_request_id = None
        self.current_attachments = []
        self.all_requests = []

        self.setWindowTitle("Campus Help — Administration")
        self.resize(1380, 860)
        self.setMinimumSize(1120, 720)

        self.setup_ui()
        self.load_requests()

    # ============================================================
    # MAIN UI
    # ============================================================

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.create_sidebar())

        content = QWidget()
        content.setObjectName("pageBackground")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(14)

        # --------------------------------------------------------
        # Header
        # --------------------------------------------------------

        header = QHBoxLayout()
        header.setSpacing(16)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        eyebrow = QLabel("ADMINISTRATION")
        eyebrow.setObjectName("eyebrow")

        title = QLabel("Support Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Review requests, update statuses, and respond to students from one workspace."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        title_col.addWidget(eyebrow)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        header.addLayout(title_col, 1)

        refresh_button = QPushButton("↻  Refresh")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.setToolTip("Reload the request queue from the server")
        refresh_button.clicked.connect(lambda: self.load_requests())
        refresh_button.setMinimumHeight(40)
        refresh_button.setMinimumWidth(105)
        header.addWidget(refresh_button, alignment=Qt.AlignTop)

        layout.addLayout(header)

        # --------------------------------------------------------
        # Statistics
        # --------------------------------------------------------

        stats = QHBoxLayout()
        stats.setSpacing(10)

        self.total_value = QLabel("0")
        self.pending_value = QLabel("0")
        self.progress_value = QLabel("0")
        self.resolved_value = QLabel("0")

        stats.addWidget(
            self.create_stat_card("TOTAL", self.total_value, "All requests", "#")
        )
        stats.addWidget(
            self.create_stat_card("PENDING", self.pending_value, "Needs attention", "!")
        )
        stats.addWidget(
            self.create_stat_card("IN PROGRESS", self.progress_value, "Being handled", "↻")
        )
        stats.addWidget(
            self.create_stat_card("RESOLVED", self.resolved_value, "Completed", "✓")
        )

        layout.addLayout(stats)

        # --------------------------------------------------------
        # Queue Toolbar
        # --------------------------------------------------------

        toolbar = QHBoxLayout()
        toolbar.setSpacing(9)

        search_label = QLabel("REQUEST QUEUE")
        search_label.setObjectName("sectionLabel")
        toolbar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by ID, student, subject or category…"
        )
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.filter_requests)
        toolbar.addWidget(self.search_input, 1)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            ["All Statuses", "Pending", "In Progress", "Resolved"]
        )
        self.filter_combo.setMinimumHeight(40)
        self.filter_combo.setMinimumWidth(135)
        self.filter_combo.currentTextChanged.connect(self.filter_requests)
        toolbar.addWidget(self.filter_combo)

        layout.addLayout(toolbar)

        # --------------------------------------------------------
        # Request list + detail workspace
        # --------------------------------------------------------

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(7)
        splitter.setMinimumHeight(400)

        # Request table card
        list_card = QFrame()
        list_card.setObjectName("card")
        list_card.setMinimumWidth(560)

        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(8, 8, 8, 8)
        list_layout.setSpacing(0)

        self.request_table = QTableWidget()
        self.request_table.setColumnCount(6)
        self.request_table.setHorizontalHeaderLabels(
            ["ID", "STUDENT", "SUBJECT", "CATEGORY", "PRIORITY", "STATUS"]
        )
        self.request_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.request_table.setSelectionMode(QTableWidget.SingleSelection)
        self.request_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.request_table.setShowGrid(False)
        self.request_table.setAlternatingRowColors(False)
        self.request_table.setWordWrap(False)
        self.request_table.setFocusPolicy(Qt.StrongFocus)
        self.request_table.verticalHeader().setVisible(False)
        self.request_table.verticalHeader().setDefaultSectionSize(44)
        self.request_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.request_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.request_table.itemSelectionChanged.connect(self.handle_selection_changed)

        header = self.request_table.horizontalHeader()
        header.setMinimumSectionSize(50)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.request_table.setColumnWidth(0, 58)
        self.request_table.setColumnWidth(1, 120)
        self.request_table.setColumnWidth(3, 145)
        self.request_table.setColumnWidth(4, 92)
        self.request_table.setColumnWidth(5, 108)

        list_layout.addWidget(self.request_table)
        splitter.addWidget(list_card)

        # Details card
        detail_card = self.create_details_panel()
        splitter.addWidget(detail_card)

        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([760, 450])

        layout.addWidget(splitter, 1)
        root.addWidget(content, 1)

    # ============================================================
    # SIDEBAR
    # ============================================================

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

        title = QLabel("Campus Help")
        title.setObjectName("sidebarBrand")
        layout.addWidget(title)

        subtitle = QLabel("ADMINISTRATION")
        subtitle.setObjectName("sidebarSubtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(25)

        requests_button = QPushButton("▣   Request Queue")
        requests_button.setObjectName("navButton")
        requests_button.setProperty("active", True)
        requests_button.setCursor(Qt.PointingHandCursor)
        requests_button.clicked.connect(lambda: self.load_requests())
        layout.addWidget(requests_button)

        layout.addStretch()

        user_card = QFrame()
        user_card.setObjectName("sidebarUserCard")

        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(12, 12, 12, 12)
        user_layout.setSpacing(3)

        admin_name = QLabel(self.user.get("name", "Administrator"))
        admin_name.setObjectName("sidebarUserName")

        admin_email = QLabel(self.user.get("email", ""))
        admin_email.setObjectName("sidebarUserEmail")
        admin_email.setWordWrap(True)

        role = QLabel("ADMINISTRATOR")
        role.setObjectName("sidebarRole")

        user_layout.addWidget(admin_name)
        user_layout.addWidget(admin_email)
        user_layout.addSpacing(3)
        user_layout.addWidget(role)

        layout.addWidget(user_card)
        layout.addSpacing(8)

        logout = QPushButton("↪   Logout")
        logout.setObjectName("dangerButton")
        logout.setCursor(Qt.PointingHandCursor)
        logout.clicked.connect(self.logout)
        logout.setMinimumHeight(40)
        layout.addWidget(logout)

        return sidebar

    # ============================================================
    # STAT CARD
    # ============================================================

    def create_stat_card(self, title, value, subtitle, icon):
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(78)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 11, 14, 11)
        row.setSpacing(10)

        accent = QFrame()
        accent.setObjectName("statAccent")
        accent.setFixedSize(36, 36)

        accent_layout = QVBoxLayout(accent)
        accent_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        accent_layout.addWidget(icon_label)

        row.addWidget(accent, alignment=Qt.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(1)

        heading = QLabel(title)
        heading.setObjectName("statTitle")

        value.setObjectName("statValue")

        small = QLabel(subtitle)
        small.setObjectName("statSubtitle")

        col.addWidget(heading)
        col.addWidget(value)
        col.addWidget(small)

        row.addLayout(col, 1)
        return card

    # ============================================================
    # DETAILS PANEL
    # ============================================================

    def create_details_panel(self):
        panel = QFrame()
        panel.setObjectName("card")
        panel.setMinimumWidth(390)

        outer_layout = QVBoxLayout(panel)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # The detail area is intentionally scrollable. This prevents the
        # lower controls from overlapping when the window is shorter or
        # when long text/filenames increase widget height.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setObjectName("detailScroll")

        # Keep the scrollable detail viewport explicitly white.
        # Without an explicit viewport background, Qt can inherit a dark
        # palette on some Windows configurations.
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #FFFFFF;
                border: none;
            }
            QScrollArea > QWidget {
                background-color: #FFFFFF;
                border: none;
            }
        """)
        scroll.viewport().setStyleSheet(
            "background-color: #FFFFFF; border: none;"
        )

        detail_content = QWidget()
        detail_content.setObjectName("detailContent")
        detail_content.setMinimumWidth(350)
        detail_content.setStyleSheet("""
            QWidget#detailContent {
                background-color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout(detail_content)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(9)

        # --------------------------------------------------------
        # Header
        # --------------------------------------------------------

        header = QHBoxLayout()
        header.setSpacing(10)

        header_col = QVBoxLayout()
        header_col.setSpacing(2)

        self.detail_eyebrow = QLabel("REQUEST DETAILS")
        self.detail_eyebrow.setObjectName("eyebrow")

        self.detail_title = QLabel("Select a request")
        self.detail_title.setObjectName("detailTitle")
        self.detail_title.setWordWrap(True)

        header_col.addWidget(self.detail_eyebrow)
        header_col.addWidget(self.detail_title)
        header.addLayout(header_col, 1)

        self.detail_status_badge = QLabel("—")
        self.detail_status_badge.setObjectName("statusBadge")
        self.detail_status_badge.setAlignment(Qt.AlignCenter)
        self.detail_status_badge.setMinimumWidth(78)
        header.addWidget(self.detail_status_badge, alignment=Qt.AlignTop)

        layout.addLayout(header)

        self.detail_student = QLabel(
            "Choose a request from the queue to view the full details."
        )
        self.detail_student.setObjectName("pageSubtitle")
        self.detail_student.setWordWrap(True)
        layout.addWidget(self.detail_student)

        # --------------------------------------------------------
        # Metadata
        # --------------------------------------------------------

        meta_card = QFrame()
        meta_card.setObjectName("softCard")

        meta_layout = QHBoxLayout(meta_card)
        meta_layout.setContentsMargins(12, 10, 12, 10)
        meta_layout.setSpacing(10)

        self.detail_category = QLabel("—")
        self.detail_priority_badge = QLabel("—")
        self.detail_created = QLabel("—")

        meta_layout.addLayout(
            self.meta_block("CATEGORY", self.detail_category), 1
        )

        priority_block = QVBoxLayout()
        priority_block.setSpacing(3)
        priority_title = QLabel("PRIORITY")
        priority_title.setObjectName("sectionLabel")
        priority_block.addWidget(priority_title)
        priority_block.addWidget(
            self.detail_priority_badge,
            alignment=Qt.AlignLeft,
        )
        meta_layout.addLayout(priority_block, 1)

        meta_layout.addLayout(
            self.meta_block("CREATED", self.detail_created), 1
        )

        layout.addWidget(meta_card)

        # --------------------------------------------------------
        # Description
        # --------------------------------------------------------

        layout.addWidget(self.section_title("DESCRIPTION"))

        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        self.detail_description.setMinimumHeight(82)
        self.detail_description.setMaximumHeight(125)
        self.detail_description.setPlaceholderText("No description available.")
        layout.addWidget(self.detail_description)

        # --------------------------------------------------------
        # Attachments
        # --------------------------------------------------------

        layout.addWidget(self.section_title("ATTACHMENTS"))

        attachment_row = QHBoxLayout()
        attachment_row.setSpacing(10)

        self.attachment_list = QListWidget()
        self.attachment_list.setMinimumHeight(64)
        self.attachment_list.setMaximumHeight(110)
        self.attachment_list.setSelectionMode(QListWidget.SingleSelection)
        self.attachment_list.currentRowChanged.connect(
            self.handle_attachment_selection
        )
        attachment_row.addWidget(self.attachment_list, 1)

        self.download_attachment_button = QPushButton("Download")
        self.download_attachment_button.setObjectName("secondaryButton")
        self.download_attachment_button.setCursor(Qt.PointingHandCursor)
        self.download_attachment_button.setMinimumHeight(40)
        self.download_attachment_button.setFixedWidth(105)
        self.download_attachment_button.clicked.connect(
            self.download_selected_attachment
        )
        self.download_attachment_button.setEnabled(False)
        attachment_row.addWidget(
            self.download_attachment_button,
            alignment=Qt.AlignVCenter,
        )

        layout.addLayout(attachment_row)

        # --------------------------------------------------------
        # Update Status
        # --------------------------------------------------------

        layout.addWidget(self.section_title("UPDATE STATUS"))

        status_row = QHBoxLayout()
        status_row.setSpacing(10)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "In Progress", "Resolved"])
        self.status_combo.setMinimumHeight(40)
        self.status_combo.setEnabled(False)
        status_row.addWidget(self.status_combo, 1)

        self.update_status_button = QPushButton("Apply Status")
        self.update_status_button.setObjectName("primaryButton")
        self.update_status_button.setCursor(Qt.PointingHandCursor)
        self.update_status_button.setMinimumHeight(40)
        self.update_status_button.setFixedWidth(120)
        self.update_status_button.clicked.connect(self.update_status)
        self.update_status_button.setEnabled(False)
        status_row.addWidget(self.update_status_button)

        layout.addLayout(status_row)

        # --------------------------------------------------------
        # Admin Response
        # --------------------------------------------------------

        layout.addWidget(self.section_title("ADMIN RESPONSE"))

        self.response_text = QTextEdit()
        self.response_text.setPlaceholderText(
            "Write a concise response to the student…"
        )
        self.response_text.setMinimumHeight(82)
        self.response_text.setMaximumHeight(105)
        self.response_text.setEnabled(False)
        layout.addWidget(self.response_text)

        self.response_hint = QLabel(
            "The student will receive an email notification when the response is sent."
        )
        self.response_hint.setObjectName("smallText")
        self.response_hint.setWordWrap(True)
        layout.addWidget(self.response_hint)

        self.response_button = QPushButton("Send Response   →")
        self.response_button.setObjectName("secondaryButton")
        self.response_button.setCursor(Qt.PointingHandCursor)
        self.response_button.setMinimumHeight(42)
        self.response_button.clicked.connect(self.send_response)
        self.response_button.setEnabled(False)
        layout.addWidget(self.response_button)

        layout.addStretch(1)

        scroll.setWidget(detail_content)
        outer_layout.addWidget(scroll)

        self._detail_scroll = scroll
        self._detail_content = detail_content

        self.clear_details()
        return panel

    @staticmethod
    def meta_block(title, value_label):
        block = QVBoxLayout()
        block.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("sectionLabel")

        value_label.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #374151;"
        )
        value_label.setWordWrap(True)

        block.addWidget(title_label)
        block.addWidget(value_label)
        return block

    @staticmethod
    def section_title(text):
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    # ============================================================
    # LOAD / FILTER
    # ============================================================

    def load_requests(self, preserve_request_id=None):
        response = get_all_requests()

        if not response.get("success"):
            show_message(
                self,
                "Unable to Load Requests",
                response.get("message", "Unable to load requests."),
                QMessageBox.Warning,
            )
            return

        self.all_requests = response.get("requests", [])

        pending = sum(
            1 for item in self.all_requests
            if item.get("status") == "Pending"
        )
        progress = sum(
            1 for item in self.all_requests
            if item.get("status") == "In Progress"
        )
        resolved = sum(
            1 for item in self.all_requests
            if item.get("status") == "Resolved"
        )

        self.total_value.setText(str(len(self.all_requests)))
        self.pending_value.setText(str(pending))
        self.progress_value.setText(str(progress))
        self.resolved_value.setText(str(resolved))

        self.filter_requests(preserve_request_id=preserve_request_id)

        if preserve_request_id is not None:
            self.select_request_row(preserve_request_id)
        else:
            self.clear_details()

    def filter_requests(self, preserve_request_id=None):
        query = self.search_input.text().strip().lower()
        status_filter = self.filter_combo.currentText()

        filtered = []

        for request in self.all_requests:
            haystack = " ".join(
                [
                    str(request.get("request_id", "")),
                    str(request.get("student_name", "")),
                    str(request.get("subject", "")),
                    str(request.get("category", "")),
                    str(request.get("priority", "")),
                ]
            ).lower()

            if query and query not in haystack:
                continue

            if (
                status_filter != "All Statuses"
                and request.get("status") != status_filter
            ):
                continue

            filtered.append(request)

        self.request_table.blockSignals(True)
        self.request_table.clearSpans()
        self.request_table.clearContents()
        self.request_table.setRowCount(len(filtered) if filtered else 1)

        if not filtered:
            item = QTableWidgetItem(
                "No requests match the current search or filter."
            )
            item.setTextAlignment(Qt.AlignCenter)
            self.request_table.setItem(0, 0, item)
            self.request_table.setSpan(0, 0, 1, 6)
            self.request_table.setRowHeight(0, 54)
            self.request_table.clearSelection()
            self.request_table.blockSignals(False)

            if preserve_request_id is None:
                self.clear_details()
            elif self.selected_request_id not in {
                item.get("request_id") for item in filtered
            }:
                self.clear_details()
            return

        visible_ids = set()

        for row, request in enumerate(filtered):
            request_id = request.get("request_id")
            visible_ids.add(request_id)

            values = [
                f"#{request_id}",
                request.get("student_name", ""),
                request.get("subject", ""),
                request.get("category", ""),
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))

                if col == 0:
                    item.setTextAlignment(Qt.AlignCenter)

                self.request_table.setItem(row, col, item)

            priority = QLabel(str(request.get("priority", "Normal")))
            set_priority_badge(priority, request.get("priority", "Normal"))
            self.request_table.setCellWidget(row, 4, priority)

            status = QLabel(str(request.get("status", "Pending")))
            set_status_badge(status, request.get("status", "Pending"))
            self.request_table.setCellWidget(row, 5, status)

            self.request_table.setRowHeight(row, 44)

        self.request_table.blockSignals(False)

        if preserve_request_id is None:
            self.request_table.clearSelection()
        elif preserve_request_id in visible_ids:
            self.select_request_row(
                preserve_request_id,
                load_details=False,
            )
        elif self.selected_request_id not in visible_ids:
            self.clear_details()

    # ============================================================
    # DETAILS / SELECTION
    # ============================================================

    def clear_details(self):
        self.selected_request_id = None
        self.current_attachments = []

        self.detail_title.setText("Select a request")
        self.detail_student.setText(
            "Choose a request from the queue to view the full details."
        )
        self.detail_category.setText("—")
        self.detail_created.setText("—")
        self.detail_description.clear()

        self.attachment_list.blockSignals(True)
        self.attachment_list.clear()
        self.attachment_list.addItem("No request selected")
        self.attachment_list.clearSelection()
        self.attachment_list.blockSignals(False)

        self.detail_status_badge.setText("—")
        self.detail_status_badge.setProperty("status", "")
        self.detail_status_badge.style().unpolish(self.detail_status_badge)
        self.detail_status_badge.style().polish(self.detail_status_badge)

        self.detail_priority_badge.setText("—")
        self.detail_priority_badge.setProperty("priority", "")
        self.detail_priority_badge.style().unpolish(self.detail_priority_badge)
        self.detail_priority_badge.style().polish(self.detail_priority_badge)

        self.status_combo.setCurrentText("Pending")
        self.status_combo.setEnabled(False)
        self.update_status_button.setEnabled(False)

        self.response_text.clear()
        self.response_text.setEnabled(False)
        self.response_button.setEnabled(False)

        self.download_attachment_button.setEnabled(False)

    def handle_selection_changed(self):
        selected = self.request_table.selectedItems()

        if not selected:
            return

        row = selected[0].row()
        item = self.request_table.item(row, 0)

        if item is None:
            return

        try:
            request_id = int(item.text().replace("#", ""))
        except ValueError:
            return

        self.load_request_details(request_id)

    def select_request_row(self, request_id, load_details=True):
        for row in range(self.request_table.rowCount()):
            item = self.request_table.item(row, 0)

            if item is None:
                continue

            try:
                current_id = int(item.text().replace("#", ""))
            except ValueError:
                continue

            if current_id == request_id:
                self.request_table.selectRow(row)

                if load_details:
                    self.load_request_details(request_id)

                return

    def load_request_details(self, request_id):
        response = get_request_details(request_id)

        if not response.get("success"):
            show_message(
                self,
                "Request Error",
                response.get("message", "Unable to load request."),
                QMessageBox.Warning,
            )
            return

        request = response["request"]
        self.selected_request_id = request_id

        self.detail_title.setText(
            f"#{request_id}  •  {request.get('subject', 'Untitled request')}"
        )
        self.detail_student.setText(
            f"{request.get('student_name', '')}  •  "
            f"{request.get('student_email', '')}"
        )
        self.detail_category.setText(request.get("category", "—"))
        self.detail_created.setText(request.get("created_at", "—"))
        self.detail_description.setPlainText(
            request.get("description", "")
        )

        status = request.get("status", "Pending")
        priority = request.get("priority", "Normal")

        self.detail_status_badge.setText(status)
        set_status_badge(self.detail_status_badge, status)

        self.detail_priority_badge.setText(priority)
        set_priority_badge(self.detail_priority_badge, priority)

        self.status_combo.setCurrentText(status)
        self.status_combo.setEnabled(True)
        self.update_status_button.setEnabled(True)

        self.response_text.setEnabled(True)
        self.response_button.setEnabled(True)
        self.response_text.clear()

        self.current_attachments = request.get("attachments", [])

        self.attachment_list.blockSignals(True)
        self.attachment_list.clear()

        if self.current_attachments:
            for attachment in self.current_attachments:
                filename = attachment.get("filename", "Unnamed file")
                self.attachment_list.addItem(f"📎  {filename}")
        else:
            self.attachment_list.addItem("No attachments")

        self.attachment_list.clearSelection()
        self.attachment_list.blockSignals(False)

        self.download_attachment_button.setEnabled(False)

    def handle_attachment_selection(self, row):
        enabled = (
            bool(self.current_attachments)
            and 0 <= row < len(self.current_attachments)
        )
        self.download_attachment_button.setEnabled(enabled)

    # ============================================================
    # ATTACHMENT DOWNLOAD
    # ============================================================

    def download_selected_attachment(self):
        if not self.current_attachments:
            show_message(
                self,
                "No Attachments",
                "This request has no attachments.",
            )
            return

        row = self.attachment_list.currentRow()

        if row < 0 or row >= len(self.current_attachments):
            show_message(
                self,
                "Select Attachment",
                "Please select an attachment first.",
                QMessageBox.Warning,
            )
            return

        attachment = self.current_attachments[row]
        filename = attachment.get("filename", "attachment")

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Attachment",
            filename,
            "All Files (*)",
        )

        if not save_path:
            return

        self.download_attachment_button.setEnabled(False)
        result = download_attachment(
            attachment.get("filepath", ""),
            save_path,
        )

        if result.get("success"):
            show_message(
                self,
                "Download Complete",
                "Attachment downloaded successfully.",
            )
        else:
            show_message(
                self,
                "Download Failed",
                result.get(
                    "message",
                    "Unable to download attachment.",
                ),
                QMessageBox.Warning,
            )

        self.handle_attachment_selection(row)

    # ============================================================
    # STATUS / RESPONSE
    # ============================================================

    def update_status(self):
        if self.selected_request_id is None:
            show_message(
                self,
                "No Request Selected",
                "Please select a request first.",
                QMessageBox.Warning,
            )
            return

        request_id = self.selected_request_id
        status = self.status_combo.currentText()

        self.update_status_button.setEnabled(False)

        response = update_request_status(request_id, status)

        if response.get("success"):
            show_message(
                self,
                "Status Updated",
                "Request status updated successfully.",
            )
            self.load_requests(preserve_request_id=request_id)
        else:
            self.update_status_button.setEnabled(True)
            show_message(
                self,
                "Update Failed",
                response.get(
                    "message",
                    "Unable to update request status.",
                ),
                QMessageBox.Warning,
            )

    def send_response(self):
        if self.selected_request_id is None:
            show_message(
                self,
                "No Request Selected",
                "Please select a request first.",
                QMessageBox.Warning,
            )
            return

        message = self.response_text.toPlainText().strip()

        if not message:
            show_message(
                self,
                "Empty Response",
                "Please enter a response before sending.",
                QMessageBox.Warning,
            )
            self.response_text.setFocus()
            return

        self.response_button.setEnabled(False)

        response = add_request_update(
            self.selected_request_id,
            message,
        )

        if response.get("success"):
            current_id = self.selected_request_id
            self.response_text.clear()

            show_message(
                self,
                "Response Sent",
                "Your response has been sent to the student.",
            )

            self.load_request_details(current_id)
        else:
            self.response_button.setEnabled(True)
            show_message(
                self,
                "Response Failed",
                response.get(
                    "message",
                    "Unable to send response.",
                ),
                QMessageBox.Warning,
            )

    # ============================================================
    # LOGOUT
    # ============================================================

    def logout(self):
        logout_user()
        self.logout_requested.emit()
        self.close()
