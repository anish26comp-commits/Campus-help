from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QDialog,
    QTextEdit,
    QFrame,
    QListWidget,
    QFileDialog,
)

from network_client import get_my_requests, get_my_request_details, download_attachment
from styles import apply_shadow, set_priority_badge, set_status_badge, show_message


class RequestDetailsDialog(QDialog):
    def __init__(self, request, parent=None):
        super().__init__(parent)
        self.request = request
        self.attachments = request.get("attachments", [])

        self.setWindowTitle(f"Campus Help — Request #{request['request_id']}")
        self.resize(720, 760)
        self.setMinimumSize(650, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        eyebrow = QLabel(f"REQUEST #{self.request['request_id']}")
        eyebrow.setObjectName("eyebrow")
        title_col.addWidget(eyebrow)

        title = QLabel(self.request["subject"])
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #111827;")
        title.setWordWrap(True)
        title_col.addWidget(title)
        top_row.addLayout(title_col, 1)

        status = QLabel(self.request["status"])
        status.setObjectName("statusBadge")
        set_status_badge(status, self.request["status"])
        top_row.addWidget(status, alignment=Qt.AlignTop)
        layout.addLayout(top_row)

        meta = QFrame()
        meta.setObjectName("softCard")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(13, 12, 13, 12)
        meta_layout.setSpacing(18)

        self.add_meta(meta_layout, "CATEGORY", self.request["category"])

        priority_col = QVBoxLayout()
        priority_title = QLabel("PRIORITY")
        priority_title.setObjectName("sectionLabel")
        priority_badge = QLabel(self.request["priority"])
        priority_badge.setObjectName("priorityBadge")
        set_priority_badge(priority_badge, self.request["priority"])
        priority_col.addWidget(priority_title)
        priority_col.addWidget(priority_badge, alignment=Qt.AlignLeft)
        meta_layout.addLayout(priority_col)

        self.add_meta(meta_layout, "CREATED", self.request["created_at"])
        meta_layout.addStretch()
        layout.addWidget(meta)

        layout.addWidget(self.section_title("DESCRIPTION"))

        description = QTextEdit()
        description.setReadOnly(True)
        description.setText(self.request["description"])
        description.setMaximumHeight(120)
        layout.addWidget(description)

        layout.addWidget(self.section_title("ATTACHMENTS"))

        attachment_row = QHBoxLayout()
        self.attachment_list = QListWidget()
        self.attachment_list.setMinimumHeight(78)
        self.populate_attachments()
        attachment_row.addWidget(self.attachment_list, 1)

        download_button = QPushButton("Download")
        download_button.setObjectName("secondaryButton")
        download_button.setCursor(Qt.PointingHandCursor)
        download_button.setMinimumHeight(42)
        download_button.setEnabled(bool(self.attachments))
        download_button.clicked.connect(self.download_selected_attachment)
        attachment_row.addWidget(download_button, alignment=Qt.AlignBottom)
        layout.addLayout(attachment_row)

        layout.addWidget(self.section_title("ACTIVITY & RESPONSES"))

        activity = QTextEdit()
        activity.setReadOnly(True)
        updates = self.request.get("updates", [])

        if updates:
            lines = []
            for update in updates:
                lines.append(
                    f"● {update['message']}\n"
                    f"   {update['updated_by']}  •  {update['updated_at']}"
                )
            activity.setPlainText("\n\n".join(lines))
        else:
            activity.setPlainText("No updates or responses yet.")

        activity.setMinimumHeight(170)
        layout.addWidget(activity, 1)

        bottom = QHBoxLayout()
        bottom.addStretch()
        close = QPushButton("Close")
        close.setObjectName("primaryButton")
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.accept)
        bottom.addWidget(close)
        layout.addLayout(bottom)

        apply_shadow(meta, blur_radius=18, y_offset=4)

    @staticmethod
    def section_title(text):
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    @staticmethod
    def add_meta(layout, title, value):
        col = QVBoxLayout()
        col.setSpacing(3)
        title_label = QLabel(title)
        title_label.setObjectName("sectionLabel")
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-size: 11px; font-weight: 700; color: #374151;")
        value_label.setWordWrap(True)
        col.addWidget(title_label)
        col.addWidget(value_label)
        layout.addLayout(col)

    def populate_attachments(self):
        self.attachment_list.clear()
        if not self.attachments:
            self.attachment_list.addItem("No attachments")
            return

        for attachment in self.attachments:
            self.attachment_list.addItem(f"📎  {attachment['filename']}")

    def download_selected_attachment(self):
        if not self.attachments:
            show_message(self, "No Attachments", "This request has no attachments.")
            return

        row = self.attachment_list.currentRow()
        if row < 0 or row >= len(self.attachments):
            show_message(self, "Select Attachment", "Please select an attachment first.", QMessageBox.Warning)
            return

        attachment = self.attachments[row]
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Attachment",
            attachment["filename"],
            "All Files (*)",
        )
        if not save_path:
            return

        result = download_attachment(attachment["filepath"], save_path)
        if result.get("success"):
            show_message(self, "Download Complete", "Attachment downloaded successfully.")
        else:
            show_message(
                self,
                "Download Failed",
                result.get("message", "Unable to download attachment."),
                QMessageBox.Warning,
            )


class MyRequestsPage(QWidget):
    def __init__(self, student_id):
        super().__init__()
        self.student_id = student_id
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title = QLabel("My Requests")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Review your submitted requests, status updates, attachments and responses.")
        subtitle.setObjectName("pageSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col)
        header.addStretch()

        refresh = QPushButton("↻  Refresh")
        refresh.setObjectName("secondaryButton")
        refresh.setCursor(Qt.PointingHandCursor)
        refresh.clicked.connect(self.load_requests)
        header.addWidget(refresh, alignment=Qt.AlignTop)
        layout.addLayout(header)

        summary = QHBoxLayout()
        summary.setSpacing(10)
        self.count_total = QLabel("0")
        self.count_pending = QLabel("0")
        self.count_progress = QLabel("0")
        self.count_resolved = QLabel("0")
        summary.addWidget(self.summary_chip("TOTAL", self.count_total))
        summary.addWidget(self.summary_chip("PENDING", self.count_pending))
        summary.addWidget(self.summary_chip("IN PROGRESS", self.count_progress))
        summary.addWidget(self.summary_chip("RESOLVED", self.count_resolved))
        summary.addStretch()
        layout.addLayout(summary)

        table_card = QFrame()
        table_card.setObjectName("card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "SUBJECT", "CATEGORY", "PRIORITY", "STATUS", "CREATED"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.cellDoubleClicked.connect(self.open_selected_request)
        self.table.setMinimumHeight(260)
        table_layout.addWidget(self.table)
        layout.addWidget(table_card, 1)

        help_row = QHBoxLayout()
        help_icon = QLabel("i")
        help_icon.setAlignment(Qt.AlignCenter)
        help_icon.setFixedSize(20, 20)
        help_icon.setStyleSheet("background: #EEF2FF; color: #4F46E5; border-radius: 10px; font-weight: 800; font-size: 10px;")
        help = QLabel("Double-click any request to open the full timeline and download attachments.")
        help.setObjectName("smallText")
        help_row.addWidget(help_icon)
        help_row.addWidget(help)
        help_row.addStretch()
        layout.addLayout(help_row)

    @staticmethod
    def summary_chip(title, value):
        chip = QFrame()
        chip.setObjectName("softCard")
        row = QHBoxLayout(chip)
        row.setContentsMargins(11, 8, 11, 8)
        row.setSpacing(7)
        title_label = QLabel(title)
        title_label.setObjectName("sectionLabel")
        value.setStyleSheet("font-size: 14px; font-weight: 800; color: #111827;")
        row.addWidget(title_label)
        row.addWidget(value)
        return chip

    def fill_status_cell(self, row, status):
        label = QLabel(status)
        label.setObjectName("statusBadge")
        set_status_badge(label, status)
        self.table.setCellWidget(row, 4, label)

    def fill_priority_cell(self, row, priority):
        label = QLabel(priority)
        label.setObjectName("priorityBadge")
        set_priority_badge(label, priority)
        self.table.setCellWidget(row, 3, label)

    def load_requests(self):
        response = get_my_requests(self.student_id)
        if not response.get("success"):
            show_message(
                self,
                "Unable to Load Requests",
                response.get("message", "Unable to retrieve requests."),
                QMessageBox.Warning,
            )
            return

        requests = response.get("requests", [])
        pending = sum(1 for item in requests if item.get("status") == "Pending")
        progress = sum(1 for item in requests if item.get("status") == "In Progress")
        resolved = sum(1 for item in requests if item.get("status") == "Resolved")

        self.count_total.setText(str(len(requests)))
        self.count_pending.setText(str(pending))
        self.count_progress.setText(str(progress))
        self.count_resolved.setText(str(resolved))

        self.table.clearContents()
        self.table.setRowCount(len(requests) if requests else 1)

        if not requests:
            item = QTableWidgetItem("No help requests submitted yet.")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 6)
            return

        self.table.clearSpans()
        for row, request in enumerate(requests):
            values = [
                f"#{request['request_id']}",
                request["subject"],
                request["category"],
                request["priority"],
                request["status"],
                request["created_at"],
            ]
            for col, value in enumerate(values):
                if col == 3:
                    continue
                if col == 4:
                    continue
                item = QTableWidgetItem(str(value))
                if col == 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
            self.fill_priority_cell(row, request["priority"])
            self.fill_status_cell(row, request["status"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

    def open_selected_request(self, row, column):
        item = self.table.item(row, 0)
        if item is None:
            return

        try:
            request_id = int(item.text().replace("#", ""))
        except ValueError:
            return

        response = get_my_request_details(request_id)
        if not response.get("success"):
            show_message(
                self,
                "Unable to Open Request",
                response.get("message", "Unable to retrieve request details."),
                QMessageBox.Warning,
            )
            return

        request = response.get("request")
        if not request:
            show_message(self, "Request Error", "Request details were not returned.", QMessageBox.Warning)
            return

        dialog = RequestDetailsDialog(request, self)
        dialog.exec()
