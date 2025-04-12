import secrets
from app import db, create_app
from sqlalchemy.sql import text


def generate_professor_keys(num_keys=10):
    keys = []
    app = create_app()

    with app.app_context():
        for _ in range(num_keys):
            key = secrets.token_hex(16)
            keys.append(key)

            db.session.execute(
                text("INSERT INTO professor_keys (key_value) VALUES (:key)"), {"key": key}
            )

        db.session.commit()
        print("Chei generate cu succes:")
        for key in keys:
            print(f"- {key}")



if __name__ == "__main__":
    generate_professor_keys(num_keys=5)
