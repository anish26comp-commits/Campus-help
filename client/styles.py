# ============================================================
# Campus Help - Global UI Theme
# ============================================================

from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QMessageBox,
)
from PySide6.QtGui import QColor


# ============================================================
# Main Application Style
# ============================================================

APP_STYLE = """
/* ==========================================================
   GLOBAL
   ========================================================== */

QWidget {
    font-family: "Segoe UI";
    color: #111827;
}

QMainWindow,
QDialog {
    background: #F4F6FB;
}

QToolTip {
    background: #111827;
    color: #FFFFFF;
    border: 1px solid #374151;
    padding: 7px 9px;
    border-radius: 7px;
}

/* ==========================================================
   AUTHENTICATION
   ========================================================== */

#mainWindow {
    background: #EEF2FF;
}

#brandingPanel {
    background: #4F46E5;
    border-radius: 26px;
}

#brandBadge {
    background: #6366F1;
    color: #FFFFFF;
    border-radius: 18px;
    font-size: 21px;
    font-weight: 800;
}

#brandName {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 800;
}

#brandTagline {
    color: #EEF2FF;
    font-size: 17px;
    font-weight: 600;
}

#brandDescription {
    color: #C7D2FE;
    font-size: 13px;
    line-height: 1.5;
}

#brandPill {
    background: rgba(255, 255, 255, 0.12);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 999px;
    padding: 7px 11px;
    font-size: 11px;
    font-weight: 700;
}

#authCard {
    background: #FFFFFF;
    border-radius: 26px;
}

#authTitle {
    color: #111827;
    font-size: 30px;
    font-weight: 800;
}

#authSubtitle {
    color: #6B7280;
    font-size: 14px;
}

#authEyebrow {
    color: #4F46E5;
    font-size: 11px;
    font-weight: 800;
}

#sectionLabel {
    color: #374151;
    font-size: 11px;
    font-weight: 800;
}

#messageLabel {
    color: #DC2626;
    font-size: 12px;
    font-weight: 600;
}

#successLabel {
    color: #059669;
    font-size: 12px;
    font-weight: 600;
}

#smallText {
    color: #9CA3AF;
    font-size: 11px;
}

#infoStrip {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
}

#infoStrip QLabel {
    color: #6B7280;
    font-size: 11px;
}

/* ==========================================================
   INPUTS
   ========================================================== */

QLineEdit,
QTextEdit,
QComboBox {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 11px;
    padding: 11px 13px;
    color: #111827;
    font-size: 13px;
    selection-background-color: #C7D2FE;
}

QLineEdit:hover,
QTextEdit:hover,
QComboBox:hover {
    border: 1px solid #C7D2FE;
}

QLineEdit:focus,
QTextEdit:focus,
QComboBox:focus {
    background: #FFFFFF;
    border: 2px solid #6366F1;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    color: #111827;
    selection-background-color: #EEF2FF;
    selection-color: #4338CA;
    padding: 5px;
}

QTextEdit {
    padding-top: 10px;
}

/* ==========================================================
   BUTTONS
   ========================================================== */

QPushButton {
    min-height: 38px;
    border: none;
    border-radius: 10px;
    padding: 0 15px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#primaryButton {
    background: #4F46E5;
    color: #FFFFFF;
}

QPushButton#primaryButton:hover {
    background: #4338CA;
}

QPushButton#primaryButton:pressed {
    background: #3730A3;
}

QPushButton#primaryButton:disabled {
    background: #A5B4FC;
    color: #EEF2FF;
}

QPushButton#secondaryButton {
    background: #EEF2FF;
    color: #4338CA;
}

QPushButton#secondaryButton:hover {
    background: #E0E7FF;
}

QPushButton#secondaryButton:disabled {
    background: #F3F4F6;
    color: #9CA3AF;
}

QPushButton#ghostButton {
    background: transparent;
    color: #4F46E5;
}

QPushButton#ghostButton:hover {
    background: #EEF2FF;
}

QPushButton#dangerButton {
    background: #FEF2F2;
    color: #B91C1C;
}

QPushButton#dangerButton:hover {
    background: #FEE2E2;
}

QPushButton#textButton {
    background: transparent;
    color: #4F46E5;
    min-height: 30px;
    padding: 0 5px;
}

QPushButton#textButton:hover {
    color: #3730A3;
}

#passwordToggle {
    background: #F8FAFC;
    color: #6B7280;
    border: 1px solid #E5E7EB;
    border-left: none;
    border-radius: 0 11px 11px 0;
    min-height: 42px;
    min-width: 58px;
    padding: 0 10px;
    font-size: 11px;
}

#passwordToggle:hover {
    color: #4F46E5;
    background: #FFFFFF;
}

/* ==========================================================
   SIDEBAR / NAVIGATION
   ========================================================== */

#sidebar {
    background: #0F172A;
}

#sidebarBrand {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
}

#sidebarSubtitle {
    color: #94A3B8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}

#sidebarLogo {
    background: #4F46E5;
    color: #FFFFFF;
    border-radius: 15px;
    font-size: 18px;
    font-weight: 800;
}

QPushButton#navButton {
    background: transparent;
    color: #CBD5E1;
    text-align: left;
    min-height: 43px;
    border-radius: 11px;
    padding: 0 14px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#navButton:hover {
    background: #1E293B;
    color: #FFFFFF;
}

QPushButton#navButton[active="true"] {
    background: #312E81;
    color: #FFFFFF;
}

#sidebarUserCard {
    background: #172033;
    border: 1px solid #243047;
    border-radius: 13px;
}

#sidebarUserName {
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 800;
}

#sidebarUserEmail {
    color: #94A3B8;
    font-size: 10px;
}

#sidebarRole {
    color: #A5B4FC;
    font-size: 10px;
    font-weight: 800;
}

/* ==========================================================
   PAGE / CARDS
   ========================================================== */

#pageBackground {
    background: #F4F6FB;
}

#pageTitle {
    color: #111827;
    font-size: 27px;
    font-weight: 800;
}

#pageSubtitle {
    color: #6B7280;
    font-size: 13px;
}

#eyebrow {
    color: #4F46E5;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}

#card {
    background: #FFFFFF;
    border: 1px solid #E8EBF2;
    border-radius: 17px;
}

#softCard {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
}

#quickCard {
    background: #4F46E5;
    border-radius: 17px;
}

#quickTitle {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 800;
}

#quickSubtitle {
    color: #E0E7FF;
    font-size: 12px;
}

/* ==========================================================
   STAT CARDS
   ========================================================== */

#statCard {
    background: #FFFFFF;
    border: 1px solid #E8EBF2;
    border-radius: 15px;
}

#statTitle {
    color: #64748B;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

#statValue {
    color: #111827;
    font-size: 26px;
    font-weight: 800;
}

#statSubtitle {
    color: #94A3B8;
    font-size: 10px;
}

#statAccent {
    background: #EEF2FF;
    border-radius: 9px;
}

#statAccent QLabel {
    color: #4F46E5;
    font-size: 16px;
    font-weight: 800;
}

/* ==========================================================
   TABLES
   ========================================================== */

QTableWidget {
    background: #FFFFFF;
    border: none;
    border-radius: 14px;
    gridline-color: #F1F5F9;
    color: #111827;
    font-size: 12px;
    selection-background-color: #EEF2FF;
    selection-color: #111827;
    outline: none;
}

QTableWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #F1F5F9;
}

QTableWidget::item:selected {
    background: #EEF2FF;
    color: #111827;
}

QHeaderView::section {
    background: #F8FAFC;
    color: #64748B;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    padding: 11px 10px;
    font-size: 10px;
    font-weight: 800;
}

QTableCornerButton::section {
    background: #F8FAFC;
    border: none;
}

/* ==========================================================
   LIST / DETAIL
   ========================================================== */

QListWidget {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 11px;
    color: #111827;
    padding: 5px;
    font-size: 12px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 8px;
}

QListWidget::item:hover {
    background: #F1F5F9;
}

QListWidget::item:selected {
    background: #EEF2FF;
    color: #4338CA;
}

/* ==========================================================
   STATUS BADGES
   ========================================================== */

#statusBadge {
    border-radius: 999px;
    padding: 5px 9px;
    min-width: 66px;
    font-size: 10px;
    font-weight: 800;
}

#statusBadge[status="Pending"] {
    background: #FEF3C7;
    color: #92400E;
}

#statusBadge[status="In Progress"] {
    background: #DBEAFE;
    color: #1D4ED8;
}

#statusBadge[status="Resolved"] {
    background: #DCFCE7;
    color: #166534;
}

#priorityBadge {
    border-radius: 999px;
    padding: 5px 9px;
    font-size: 10px;
    font-weight: 800;
}

#priorityBadge[priority="High"] {
    background: #FEE2E2;
    color: #B91C1C;
}

#priorityBadge[priority="Normal"] {
    background: #EDE9FE;
    color: #6D28D9;
}

#priorityBadge[priority="Low"] {
    background: #E2E8F0;
    color: #475569;
}

/* ==========================================================
   MESSAGE BOX
   ========================================================== */

QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    background-color: #FFFFFF;
    color: #111827;
    font-size: 13px;
    padding: 6px;
}

QMessageBox QPushButton {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 23px;
    min-width: 76px;
    font-size: 12px;
    font-weight: 700;
}

QMessageBox QPushButton:hover {
    background-color: #4338CA;
}

QMessageBox QPushButton:pressed {
    background-color: #3730A3;
}

/* ==========================================================
   SCROLLBAR
   ========================================================== */

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 3px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 35px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
"""


# ============================================================
# Helpers
# ============================================================

def apply_shadow(widget, blur_radius=28, x_offset=0, y_offset=8):
    """Apply a subtle shadow that works well on light backgrounds."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(15, 23, 42, 28))
    widget.setGraphicsEffect(shadow)


def set_status_badge(label, status):
    """Apply the stylesheet status property and refresh the badge."""
    label.setObjectName("statusBadge")
    label.setProperty("status", status)
    from PySide6.QtCore import Qt
    label.setAlignment(Qt.AlignCenter)
    label.style().unpolish(label)
    label.style().polish(label)
    label.update()


def set_priority_badge(label, priority):
    """Apply the stylesheet priority property and refresh the badge."""
    label.setObjectName("priorityBadge")
    label.setProperty("priority", priority)
    label.style().unpolish(label)
    label.style().polish(label)
    label.update()


def show_message(parent, title, message, icon=QMessageBox.Information):
    """Show a consistent, readable message box in light theme."""
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(message)
    box.setIcon(icon)
    box.setStandardButtons(QMessageBox.Ok)
    box.setStyleSheet("""
        QMessageBox {
            background-color: #FFFFFF;
        }
        QMessageBox QLabel {
            background-color: #FFFFFF;
            color: #111827;
            font-size: 13px;
            padding: 6px;
        }
        QMessageBox QPushButton {
            background-color: #4F46E5;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 9px 23px;
            min-width: 76px;
            font-size: 12px;
            font-weight: 700;
        }
        QMessageBox QPushButton:hover {
            background-color: #4338CA;
        }
    """)
    return box.exec()
