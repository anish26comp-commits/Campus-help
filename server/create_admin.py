from getpass import getpass

from database import (
    initialize_database,
    create_admin_user
)


def main():

    initialize_database()

    print("=" * 50)
    print("Campus Help - Admin Account Setup")
    print("=" * 50)

    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip()

    password = getpass(
        "Admin password: "
    )

    confirm = getpass(
        "Confirm password: "
    )

    if not name or not email or not password:

        print("\nAll fields are required.")
        return

    if password != confirm:

        print("\nPasswords do not match.")
        return

    result = create_admin_user(
        name,
        email,
        password
    )

    print(
        "\n" + result["message"]
    )


if __name__ == "__main__":
    main()