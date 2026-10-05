import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from network_client import login_user, register_user, logout_user
from styles import APP_STYLE, apply_shadow, show_message
from dashboard import StudentDashboard
from admin_dashboard import AdminDashboard


class PasswordField(QWidget):
    def __init__(self, placeholder="Password"):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.field = QLineEdit()
        self.field.setPlaceholderText(placeholder)
        self.field.setEchoMode(QLineEdit.Password)
        self.field.setMinimumHeight(42)

        self.toggle = QPushButton("Show")
        self.toggle.setObjectName("passwordToggle")
        self.toggle.setCursor(Qt.PointingHandCursor)
        self.toggle.clicked.connect(self.toggle_password)

        # Avoid a double border where the two controls meet.
        self.field.setStyleSheet("border-radius: 11px 0 0 11px;")

        layout.addWidget(self.field, 1)
        layout.addWidget(self.toggle)

    def toggle_password(self):
        visible = self.field.echoMode() == QLineEdit.Normal
        self.field.setEchoMode(QLineEdit.Password if visible else QLineEdit.Normal)
        self.toggle.setText("Show" if visible else "Hide")

    def text(self):
        return self.field.text()

    def clear(self):
        self.field.clear()

    def setFocus(self):
        self.field.setFocus()


class BrandingPanel(QFrame):
    def __init__(self, mode="student"):
        super().__init__()
        self.setObjectName("brandingPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 40, 42, 40)
        layout.setSpacing(15)

        logo = QLabel("CH")
        logo.setObjectName("brandBadge")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(64, 64)
        layout.addWidget(logo, alignment=Qt.AlignLeft)

        eyebrow = QLabel("CAMPUS SUPPORT PLATFORM")
        eyebrow.setObjectName("brandPill")
        eyebrow.setFixedWidth(185)
        eyebrow.setAlignment(Qt.AlignCenter)
        layout.addWidget(eyebrow, alignment=Qt.AlignLeft)

        layout.addSpacing(8)

        brand = QLabel("Campus Help")
        brand.setObjectName("brandName")
        layout.addWidget(brand)

        tagline = QLabel("Your campus support,\nconnected in one place.")
        tagline.setObjectName("brandTagline")
        layout.addWidget(tagline)

        description = QLabel(
            "Submit assistance requests, monitor progress, send attachments, "
            "and receive email updates through your campus LAN."
        )
        description.setObjectName("brandDescription")
        description.setWordWrap(True)
        description.setMaximumWidth(330)
        layout.addWidget(description)

        layout.addSpacing(12)

        feature_card = QFrame()
        feature_card.setObjectName("infoStrip")
        feature_layout = QVBoxLayout(feature_card)
        feature_layout.setContentsMargins(15, 13, 15, 13)
        feature_layout.setSpacing(6)

        features = [
            "✓  Centralized help requests",
            "✓  Live request status tracking",
            "✓  Secure attachment transfers",
            "✓  Email notifications",
        ]
        for text in features:
            label = QLabel(text)
            label.setStyleSheet("color: #EEF2FF; font-size: 12px; font-weight: 600;")
            feature_layout.addWidget(label)

        # Keep the strip compatible with the purple branding surface.
        feature_card.setStyleSheet("""
            QFrame#infoStrip {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 14px;
            }
        """)
        layout.addWidget(feature_card)

        layout.addStretch()

        secure = QLabel("●  Campus LAN services online")
        secure.setStyleSheet("color: #D1FAE5; font-size: 11px; font-weight: 700;")
        layout.addWidget(secure)

        version = QLabel("TCP  •  UDP  •  FTP  •  HTTP  •  SMTP")
        version.setStyleSheet("color: #C7D2FE; font-size: 10px; font-weight: 700;")
        layout.addWidget(version)


class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(54, 46, 54, 46)
        layout.setSpacing(10)

        eyebrow = QLabel("STUDENT PORTAL")
        eyebrow.setObjectName("authEyebrow")
        layout.addWidget(eyebrow)

        title = QLabel("Welcome back")
        title.setObjectName("authTitle")
        layout.addWidget(title)

        subtitle = QLabel("Sign in to manage your campus support requests.")
        subtitle.setObjectName("authSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setMinimumHeight(42)
        self.add_field(layout, "EMAIL ADDRESS", self.email_input)

        self.password_input = PasswordField("Enter your password")
        self.add_field(layout, "PASSWORD", self.password_input)

        self.message = QLabel("")
        self.message.setObjectName("messageLabel")
        self.message.setWordWrap(True)
        self.message.setMinimumHeight(18)
        layout.addWidget(self.message)

        sign_in = QPushButton("Sign In   →")
        sign_in.setObjectName("primaryButton")
        sign_in.setCursor(Qt.PointingHandCursor)
        sign_in.setMinimumHeight(44)
        sign_in.clicked.connect(self.handle_login)
        layout.addWidget(sign_in)

        register_button = QPushButton("Create a student account")
        register_button.setObjectName("textButton")
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.clicked.connect(self.show_register)
        layout.addWidget(register_button, alignment=Qt.AlignCenter)

        layout.addStretch()

        footer = QLabel("Your credentials are processed through the campus LAN server.")
        footer.setObjectName("smallText")
        footer.setWordWrap(True)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.field.returnPressed.connect(self.handle_login)

        self.email_input.setFocus()

    @staticmethod
    def add_field(layout, label_text, widget):
        label = QLabel(label_text)
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addSpacing(5)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        self.message.clear()

        if not email or not password:
            self.message.setText("Please enter your email and password.")
            return

        response = login_user(email, password)

        if response.get("success"):
            user = response.get("user", {})
            self.email_input.clear()
            self.password_input.clear()

            if user.get("role") == "admin":
                self.parent_window.open_admin_dashboard(user)
            else:
                self.parent_window.open_dashboard(user)
        else:
            self.message.setText(response.get("message", "Login failed."))

    def show_register(self):
        self.email_input.clear()
        self.password_input.clear()
        self.message.clear()
        self.parent_window.show_register_page()


class RegisterPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(54, 38, 54, 38)
        layout.setSpacing(8)

        eyebrow = QLabel("NEW STUDENT ACCOUNT")
        eyebrow.setObjectName("authEyebrow")
        layout.addWidget(eyebrow)

        title = QLabel("Create your account")
        title.setObjectName("authTitle")
        layout.addWidget(title)

        subtitle = QLabel("Register once, then use Campus Help to track every request.")
        subtitle.setObjectName("authSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(14)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setMinimumHeight(41)
        LoginPage.add_field(layout, "FULL NAME", self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your student email")
        self.email_input.setMinimumHeight(41)
        LoginPage.add_field(layout, "EMAIL ADDRESS", self.email_input)

        self.password_input = PasswordField("Create a password")
        LoginPage.add_field(layout, "PASSWORD", self.password_input)

        self.confirm_input = PasswordField("Confirm your password")
        LoginPage.add_field(layout, "CONFIRM PASSWORD", self.confirm_input)

        role_note = QFrame()
        role_note.setObjectName("infoStrip")
        role_layout = QHBoxLayout(role_note)
        role_layout.setContentsMargins(12, 8, 12, 8)
        role_layout.setSpacing(8)
        role_icon = QLabel("●")
        role_icon.setStyleSheet("color: #4F46E5; font-size: 10px;")
        role_text = QLabel("Student accounts are created here. Administrator accounts are managed separately.")
        role_text.setWordWrap(True)
        role_layout.addWidget(role_icon)
        role_layout.addWidget(role_text, 1)
        layout.addWidget(role_note)

        self.message = QLabel("")
        self.message.setObjectName("messageLabel")
        self.message.setWordWrap(True)
        self.message.setMinimumHeight(18)
        layout.addWidget(self.message)

        register_button = QPushButton("Create Account   →")
        register_button.setObjectName("primaryButton")
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.setMinimumHeight(43)
        register_button.clicked.connect(self.handle_register)
        layout.addWidget(register_button)

        back_button = QPushButton("← Back to sign in")
        back_button.setObjectName("textButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.show_login)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        layout.addStretch()

    def handle_register(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        self.message.clear()

        if not name or not email or not password or not confirm:
            self.message.setText("Please complete all required fields.")
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            self.message.setText("Please enter a valid email address.")
            return

        if len(password) < 6:
            self.message.setText("Password must contain at least 6 characters.")
            return

        if password != confirm:
            self.message.setText("Passwords do not match.")
            return

        response = register_user(name, email, password)

        if response.get("success"):
            self.clear_fields()
            show_message(
                self,
                "Account Created",
                "Your student account has been created successfully.",
            )
            self.show_login()
        else:
            self.message.setText(response.get("message", "Registration failed."))

    def clear_fields(self):
        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.message.clear()

    def show_login(self):
        self.parent_window.show_login_page()


class CampusHelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = None

        self.setObjectName("mainWindow")
        self.setWindowTitle("Campus Help — Student Portal")
        self.resize(1180, 740)
        self.setMinimumSize(980, 650)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(22)

        self.branding_panel = BrandingPanel()
        self.branding_panel.setMinimumWidth(390)
        self.branding_panel.setMaximumWidth(470)
        main_layout.addWidget(self.branding_panel, 4)

        self.auth_card = QFrame()
        self.auth_card.setObjectName("authCard")
        self.auth_card.setMinimumWidth(500)

        card_layout = QVBoxLayout(self.auth_card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        self.pages = QStackedWidget()
        self.login_page = LoginPage(self)
        self.register_page = RegisterPage(self)
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.register_page)
        card_layout.addWidget(self.pages)

        main_layout.addWidget(self.auth_card, 6)
        apply_shadow(self.auth_card, blur_radius=42, x_offset=0, y_offset=12)

    def show_login_page(self):
        self.pages.setCurrentWidget(self.login_page)
        self.login_page.email_input.setFocus()

    def show_register_page(self):
        self.pages.setCurrentWidget(self.register_page)
        self.register_page.name_input.setFocus()

    def open_dashboard(self, user):
        self.current_user = user
        self.dashboard_window = StudentDashboard(user)
        self.dashboard_window.logout_requested.connect(self.handle_dashboard_logout)
        self.hide()
        self.dashboard_window.show()

    def open_admin_dashboard(self, user):
        self.current_user = user
        self.admin_dashboard_window = AdminDashboard(user)
        self.admin_dashboard_window.logout_requested.connect(self.handle_dashboard_logout)
        self.hide()
        self.admin_dashboard_window.show()

    def handle_dashboard_logout(self):
        logout_user()
        self.current_user = None
        self.show_login_page()
        self.show()
        self.activateWindow()

    def logout(self):
        self.current_user = None
        self.show_login_page()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    window = CampusHelpWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
