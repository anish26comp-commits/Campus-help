import sqlite3
import os
import hashlib
import secrets
from datetime import datetime


# ============================================================
# Database Configuration
# ============================================================

DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "CampusHelp.db"
)


# ============================================================
# Database Connection
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# Password Hashing
# ============================================================

def hash_password(
    password,
    salt=None
):

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(
    password,
    stored_password
):

    try:

        salt, stored_hash = (
            stored_password.split("$")
        )

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()

        return secrets.compare_digest(
            password_hash,
            stored_hash
        )

    except ValueError:

        return False


# ============================================================
# Initialize Database
# ============================================================

def initialize_database():

    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
                CHECK(role IN ('student', 'admin'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS help_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (student_id)
                REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            updated_by INTEGER NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (request_id)
                REFERENCES help_requests(request_id),

            FOREIGN KEY (updated_by)
                REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,

            FOREIGN KEY (request_id)
                REFERENCES help_requests(request_id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")


# ============================================================
# Register Student
# ============================================================

def register_user(
    name,
    email,
    password
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        password_hash = hash_password(
            password
        )

        cursor.execute("""
            INSERT INTO users
                (name, email, password, role)
            VALUES
                (?, ?, ?, 'student')
        """, (
            name,
            email,
            password_hash
        ))

        connection.commit()

        return {
            "success": True,
            "message": "Registration successful.",
            "user_id": cursor.lastrowid
        }

    except sqlite3.IntegrityError:

        return {
            "success": False,
            "message": "Email already registered."
        }

    finally:

        connection.close()


# ============================================================
# Create Admin
# ============================================================

def create_admin_user(
    name,
    email,
    password
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        password_hash = hash_password(
            password
        )

        cursor.execute("""
            INSERT INTO users
                (name, email, password, role)
            VALUES
                (?, ?, ?, 'admin')
        """, (
            name,
            email,
            password_hash
        ))

        connection.commit()

        return {
            "success": True,
            "message": "Admin account created successfully.",
            "user_id": cursor.lastrowid
        }

    except sqlite3.IntegrityError:

        return {
            "success": False,
            "message": "Email already registered."
        }

    finally:

        connection.close()


# ============================================================
# Authenticate User
# ============================================================

def authenticate_user(
    email,
    password
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            password,
            role
        FROM users
        WHERE email = ?
    """, (
        email,
    ))

    user = cursor.fetchone()

    connection.close()

    if user is None:

        return {
            "success": False,
            "message": "User does not exist. Register first."
        }

    user_id, name, email, stored_password, role = user

    if not verify_password(
        password,
        stored_password
    ):

        return {
            "success": False,
            "message": "Invalid email or password."
        }

    return {
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role
        }
    }


# ============================================================
# Create Help Request
# ============================================================

def create_help_request(
    student_id,
    category,
    subject,
    description,
    priority
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO help_requests (
                student_id,
                category,
                subject,
                description,
                priority,
                status,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?,
                'Pending',
                ?, ?
            )
        """, (
            student_id,
            category,
            subject,
            description,
            priority,
            now,
            now
        ))

        connection.commit()

        return {
            "success": True,
            "message": "Help request submitted successfully.",
            "request_id": cursor.lastrowid
        }

    except Exception as error:

        connection.rollback()

        return {
            "success": False,
            "message": f"Unable to create request: {error}"
        }

    finally:

        connection.close()


# ============================================================
# Get Student Requests
# ============================================================

def get_student_requests(
    student_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            request_id,
            category,
            subject,
            description,
            priority,
            status,
            created_at,
            updated_at
        FROM help_requests
        WHERE student_id = ?
        ORDER BY request_id DESC
    """, (
        student_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    requests = []

    for row in rows:

        requests.append({
            "request_id": row[0],
            "category": row[1],
            "subject": row[2],
            "description": row[3],
            "priority": row[4],
            "status": row[5],
            "created_at": row[6],
            "updated_at": row[7]
        })

    return {
        "success": True,
        "requests": requests
    }


# ============================================================
# Get All Requests
# ============================================================

def get_all_requests():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            hr.request_id,
            u.name,
            u.email,
            hr.category,
            hr.subject,
            hr.description,
            hr.priority,
            hr.status,
            hr.created_at,
            hr.updated_at
        FROM help_requests hr
        INNER JOIN users u
            ON hr.student_id = u.id
        ORDER BY hr.request_id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    requests = []

    for row in rows:

        requests.append({
            "request_id": row[0],
            "student_name": row[1],
            "student_email": row[2],
            "category": row[3],
            "subject": row[4],
            "description": row[5],
            "priority": row[6],
            "status": row[7],
            "created_at": row[8],
            "updated_at": row[9]
        })

    return {
        "success": True,
        "requests": requests
    }


# ============================================================
# Get Request Attachments
# ============================================================

def get_request_attachments(
    request_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            attachment_id,
            filename,
            filepath,
            uploaded_at
        FROM attachments
        WHERE request_id = ?
        ORDER BY uploaded_at ASC
    """, (
        request_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    attachments = []

    for row in rows:

        attachments.append({
            "attachment_id": row[0],
            "filename": row[1],
            "filepath": row[2],
            "uploaded_at": row[3]
        })

    return attachments


# ============================================================
# Add Attachment
# ============================================================

def add_attachment(
    request_id,
    filename,
    filepath
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            SELECT request_id
            FROM help_requests
            WHERE request_id = ?
        """, (
            request_id,
        ))

        if cursor.fetchone() is None:

            return {
                "success": False,
                "message": "Request not found."
            }

        cursor.execute("""
            INSERT INTO attachments (
                request_id,
                filename,
                filepath,
                uploaded_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            filename,
            filepath,
            now
        ))

        connection.commit()

        return {
            "success": True,
            "message": "Attachment recorded successfully."
        }

    except Exception as error:

        connection.rollback()

        return {
            "success": False,
            "message": f"Unable to record attachment: {error}"
        }

    finally:

        connection.close()


# ============================================================
# Build Request Details
# ============================================================

def _request_details_from_row(
    cursor,
    row,
    request_id
):

    cursor.execute("""
        SELECT
            ru.message,
            u.name,
            ru.updated_at
        FROM request_updates ru
        INNER JOIN users u
            ON ru.updated_by = u.id
        WHERE ru.request_id = ?
        ORDER BY ru.updated_at ASC
    """, (
        request_id,
    ))

    update_rows = cursor.fetchall()

    updates = []

    for update in update_rows:

        updates.append({
            "message": update[0],
            "updated_by": update[1],
            "updated_at": update[2]
        })

    cursor.execute("""
        SELECT
            attachment_id,
            filename,
            filepath,
            uploaded_at
        FROM attachments
        WHERE request_id = ?
        ORDER BY uploaded_at ASC
    """, (
        request_id,
    ))

    attachment_rows = cursor.fetchall()

    attachments = []

    for attachment in attachment_rows:

        attachments.append({
            "attachment_id": attachment[0],
            "filename": attachment[1],
            "filepath": attachment[2],
            "uploaded_at": attachment[3]
        })

    return {
        "request_id": row[0],
        "student_id": row[1],
        "student_name": row[2],
        "student_email": row[3],
        "category": row[4],
        "subject": row[5],
        "description": row[6],
        "priority": row[7],
        "status": row[8],
        "created_at": row[9],
        "updated_at": row[10],
        "updates": updates,
        "attachments": attachments
    }


# ============================================================
# Get Request Details
# ============================================================

def get_request_details(
    request_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            hr.request_id,
            hr.student_id,
            u.name,
            u.email,
            hr.category,
            hr.subject,
            hr.description,
            hr.priority,
            hr.status,
            hr.created_at,
            hr.updated_at
        FROM help_requests hr
        INNER JOIN users u
            ON hr.student_id = u.id
        WHERE hr.request_id = ?
    """, (
        request_id,
    ))

    row = cursor.fetchone()

    if row is None:

        connection.close()

        return {
            "success": False,
            "message": "Request not found."
        }

    request = _request_details_from_row(
        cursor,
        row,
        request_id
    )

    connection.close()

    return {
        "success": True,
        "request": request
    }


# ============================================================
# Get Student-Specific Request Details
# ============================================================

def get_student_request_details(
    student_id,
    request_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            hr.request_id,
            hr.student_id,
            u.name,
            u.email,
            hr.category,
            hr.subject,
            hr.description,
            hr.priority,
            hr.status,
            hr.created_at,
            hr.updated_at
        FROM help_requests hr
        INNER JOIN users u
            ON hr.student_id = u.id
        WHERE hr.request_id = ?
          AND hr.student_id = ?
    """, (
        request_id,
        student_id
    ))

    row = cursor.fetchone()

    if row is None:

        connection.close()

        return {
            "success": False,
            "message": (
                "Request not found or access denied."
            )
        }

    request = _request_details_from_row(
        cursor,
        row,
        request_id
    )

    connection.close()

    return {
        "success": True,
        "request": request
    }


# ============================================================
# Update Request Status
# ============================================================

def update_request_status(
    request_id,
    status,
    admin_id
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            UPDATE help_requests
            SET
                status = ?,
                updated_at = ?
            WHERE request_id = ?
        """, (
            status,
            now,
            request_id
        ))

        if cursor.rowcount == 0:

            return {
                "success": False,
                "message": "Request not found."
            }

        cursor.execute("""
            INSERT INTO request_updates (
                request_id,
                message,
                updated_by,
                updated_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            f"Request status changed to {status}.",
            admin_id,
            now
        ))

        connection.commit()

        return {
            "success": True,
            "message": (
                "Request status updated successfully."
            )
        }

    except Exception as error:

        connection.rollback()

        return {
            "success": False,
            "message": (
                f"Unable to update request: {error}"
            )
        }

    finally:

        connection.close()


# ============================================================
# Add Request Update
# ============================================================

def add_request_update(
    request_id,
    message,
    admin_id
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            SELECT request_id
            FROM help_requests
            WHERE request_id = ?
        """, (
            request_id,
        ))

        if cursor.fetchone() is None:

            return {
                "success": False,
                "message": "Request not found."
            }

        cursor.execute("""
            INSERT INTO request_updates (
                request_id,
                message,
                updated_by,
                updated_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            message,
            admin_id,
            now
        ))

        cursor.execute("""
            UPDATE help_requests
            SET updated_at = ?
            WHERE request_id = ?
        """, (
            now,
            request_id
        ))

        connection.commit()

        return {
            "success": True,
            "message": "Response added successfully."
        }

    except Exception as error:

        connection.rollback()

        return {
            "success": False,
            "message": (
                f"Unable to add response: {error}"
            )
        }

    finally:

        connection.close()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    initialize_database()