from getpass import getpass

from database import (
    initialize_database,
    get_connection,
    hash_password
)


def main():

    initialize_database()

    print("=" * 50)
    print("Campus Help - Reset Admin Password")
    print("=" * 50)

    email = input(
        "Admin email: "
    ).strip()

    if not email:
        print("\nEmail cannot be empty.")
        return

    new_password = getpass(
        "New password: "
    )

    confirm_password = getpass(
        "Confirm new password: "
    )

    if not new_password:
        print("\nPassword cannot be empty.")
        return

    if new_password != confirm_password:
        print("\nPasswords do not match.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM users
        WHERE email = ?
          AND role = 'admin'
    """, (email,))

    admin = cursor.fetchone()

    if admin is None:

        connection.close()

        print(
            "\nNo administrator account was found "
            "with that email."
        )

        return

    password_hash = hash_password(
        new_password
    )

    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE id = ?
          AND role = 'admin'
    """, (
        password_hash,
        admin[0]
    ))

    connection.commit()
    connection.close()

    print(
        f"\nPassword reset successfully for "
        f"administrator: {admin[1]}"
    )


if __name__ == "__main__":
    main()