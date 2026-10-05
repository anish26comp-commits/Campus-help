import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QFrame,
    QFileDialog,
)

from network_client import create_help_request, upload_attachment, save_attachment_metadata
from styles import apply_shadow, show_message


class NewRequestPage(QWidget):
    request_submitted = Signal()

    def __init__(self, student_id):
        super().__init__()
        self.student_id = student_id
        self.selected_file = None
        self.setup_ui()

    def setup_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(15)

        header_col = QVBoxLayout()
        header_col.setSpacing(4)
        title = QLabel("Create a Help Request")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Describe the issue clearly so the right support team can respond quickly.")
        subtitle.setObjectName("pageSubtitle")
        header_col.addWidget(title)
        header_col.addWidget(subtitle)
        page_layout.addLayout(header_col)

        body = QHBoxLayout()
        body.setSpacing(15)

        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setSpacing(7)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.category = QComboBox()
        self.category.addItems([
            "IT / Computer",
            "Network / Wi-Fi",
            "Classroom / Projector",
            "Laboratory Equipment",
            "Library",
            "Academic",
            "Other",
        ])
        top_row.addLayout(self.field_block("CATEGORY", self.category), 2)

        self.priority = QComboBox()
        self.priority.addItems(["Low", "Normal", "High"])
        self.priority.setCurrentText("Normal")
        top_row.addLayout(self.field_block("PRIORITY", self.priority), 1)
        form_layout.addLayout(top_row)

        self.subject = QLineEdit()
        self.subject.setPlaceholderText("Briefly describe your issue")
        self.subject.setMinimumHeight(42)
        form_layout.addLayout(self.field_block("SUBJECT", self.subject))

        self.description = QTextEdit()
        self.description.setPlaceholderText("What happened? When did it start? What have you already tried?")
        self.description.setMinimumHeight(150)
        self.description.setMaximumHeight(210)
        form_layout.addLayout(self.field_block("DESCRIPTION", self.description))

        attach_label = QLabel("ATTACHMENT")
        attach_label.setObjectName("sectionLabel")
        form_layout.addWidget(attach_label)

        attachment_row = QHBoxLayout()
        attachment_row.setSpacing(9)

        self.file_label = QLabel("No file selected  •  Optional")
        self.file_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.file_label.setMinimumHeight(42)
        self.file_label.setStyleSheet("""
            QLabel {
                background: #F8FAFC;
                border: 1px dashed #CBD5E1;
                border-radius: 10px;
                padding: 0 12px;
                color: #94A3B8;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        choose = QPushButton("Choose File")
        choose.setObjectName("secondaryButton")
        choose.setCursor(Qt.PointingHandCursor)
        choose.setMinimumHeight(42)
        choose.clicked.connect(self.choose_file)

        attachment_row.addWidget(self.file_label, 1)
        attachment_row.addWidget(choose)
        form_layout.addLayout(attachment_row)

        note = QLabel("Maximum attachment size: 10 MB")
        note.setObjectName("smallText")
        form_layout.addWidget(note)

        form_layout.addSpacing(5)

        self.submit_button = QPushButton("Submit Help Request   →")
        self.submit_button.setObjectName("primaryButton")
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setMinimumHeight(44)
        self.submit_button.clicked.connect(self.submit_request)
        form_layout.addWidget(self.submit_button)

        body.addWidget(form_card, 3)

        guide = QFrame()
        guide.setObjectName("softCard")
        guide_layout = QVBoxLayout(guide)
        guide_layout.setContentsMargins(20, 20, 20, 20)
        guide_layout.setSpacing(11)
        guide.setMinimumWidth(260)
        guide.setMaximumWidth(320)

        guide_title = QLabel("Request checklist")
        guide_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #111827;")
        guide_layout.addWidget(guide_title)

        guide_sub = QLabel("A clear request makes resolution faster.")
        guide_sub.setObjectName("pageSubtitle")
        guide_sub.setWordWrap(True)
        guide_layout.addWidget(guide_sub)

        tips = [
            ("01", "Use a specific subject"),
            ("02", "Explain the problem in detail"),
            ("03", "Choose the correct priority"),
            ("04", "Attach screenshots when useful"),
        ]

        for number, text in tips:
            row = QHBoxLayout()
            badge = QLabel(number)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(30, 30)
            badge.setStyleSheet("background: #EEF2FF; color: #4F46E5; border-radius: 9px; font-size: 10px; font-weight: 800;")
            label = QLabel(text)
            label.setStyleSheet("font-size: 11px; font-weight: 700; color: #374151;")
            label.setWordWrap(True)
            row.addWidget(badge)
            row.addWidget(label, 1)
            guide_layout.addLayout(row)

        guide_layout.addStretch()

        network = QFrame()
        network.setObjectName("card")
        network_layout = QVBoxLayout(network)
        network_layout.setContentsMargins(12, 11, 12, 11)
        network_layout.setSpacing(3)
        network_title = QLabel("Connected services")
        network_title.setStyleSheet("font-size: 10px; font-weight: 800; color: #64748B;")
        network_text = QLabel("TCP request  •  FTP attachment  •  SMTP update")
        network_text.setStyleSheet("font-size: 10px; color: #94A3B8;")
        network_text.setWordWrap(True)
        network_layout.addWidget(network_title)
        network_layout.addWidget(network_text)
        guide_layout.addWidget(network)

        body.addWidget(guide, 1)
        page_layout.addLayout(body, 1)

        apply_shadow(form_card, blur_radius=22, y_offset=6)

    @staticmethod
    def field_block(label_text, widget):
        block = QVBoxLayout()
        block.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("sectionLabel")
        block.addWidget(label)
        block.addWidget(widget)
        return block

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Attachment",
            "",
            "Documents (*.pdf *.doc *.docx *.txt);;Images (*.png *.jpg *.jpeg);;All Files (*)",
        )

        if not file_path:
            return

        max_size = 10 * 1024 * 1024
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            show_message(self, "File Error", "Unable to read the selected file.")
            return

        if file_size > max_size:
            show_message(self, "File Too Large", "Please select a file smaller than 10 MB.")
            return

        self.selected_file = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.file_label.setStyleSheet("""
            QLabel {
                background: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 10px;
                padding: 0 12px;
                color: #4338CA;
                font-size: 11px;
                font-weight: 700;
            }
        """)

    def submit_request(self):
        subject = self.subject.text().strip()
        description = self.description.toPlainText().strip()
        category = self.category.currentText()
        priority = self.priority.currentText()

        if not subject:
            show_message(self, "Missing Subject", "Please enter a subject.")
            self.subject.setFocus()
            return

        if not description:
            show_message(self, "Missing Description", "Please describe the problem.")
            self.description.setFocus()
            return

        self.submit_button.setEnabled(False)
        self.submit_button.setText("Submitting request…")

        try:
            response = create_help_request(
                self.student_id,
                category,
                subject,
                description,
                priority,
            )

            if not response.get("success"):
                show_message(
                    self,
                    "Submission Failed",
                    response.get("message", "Unable to submit request."),
                )
                return

            request_id = response.get("request_id")

            if self.selected_file:
                upload_result = upload_attachment(self.selected_file, request_id)

                if not upload_result.get("success"):
                    show_message(
                        self,
                        "Attachment Upload Failed",
                        "The request was created, but the attachment could not be uploaded.\n\n"
                        + upload_result.get("message", "FTP upload failed."),
                    )
                else:
                    metadata_result = save_attachment_metadata(
                        request_id,
                        upload_result["filename"],
                        upload_result["remote_path"],
                    )

                    if not metadata_result.get("success"):
                        show_message(
                            self,
                            "Attachment Error",
                            "The file was uploaded, but its attachment information could not be saved.",
                        )

            show_message(
                self,
                "Request Submitted",
                f"Your help request has been submitted successfully.\n\nRequest ID: #{request_id}",
            )

            self.reset_form()
            self.request_submitted.emit()

        finally:
            self.submit_button.setEnabled(True)
            self.submit_button.setText("Submit Help Request   →")

    def reset_form(self):
        self.subject.clear()
        self.description.clear()
        self.category.setCurrentIndex(0)
        self.priority.setCurrentText("Normal")
        self.selected_file = None
        self.file_label.setText("No file selected  •  Optional")
        self.file_label.setStyleSheet("""
            QLabel {
                background: #F8FAFC;
                border: 1px dashed #CBD5E1;
                border-radius: 10px;
                padding: 0 12px;
                color: #94A3B8;
                font-size: 11px;
                font-weight: 600;
            }
        """)
