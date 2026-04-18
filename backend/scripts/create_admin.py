"""Script interativo para criar o primeiro usuário administrador."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import hash_password
from database import SessionLocal, engine
from models import Base, User


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("\n=== Criar Usuário Admin — Goiânia Cultural ===\n")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Senha (mínimo 8 caracteres): ").strip()

    if len(password) < 8:
        print("Erro: senha muito curta.")
        sys.exit(1)

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"Erro: usuário '{username}' já existe.")
        sys.exit(1)

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_admin=True,
    )
    db.add(user)
    db.commit()

    print(f"\n✅ Admin '{username}' criado com sucesso!")
    print("   Acesse /admin para fazer login.\n")
    db.close()


if __name__ == "__main__":
    main()
