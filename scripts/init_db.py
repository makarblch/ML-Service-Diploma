from app.db.base import Base
from app.db.models import MlErrorLog, MlJobLog, MlJobState, ModelRegistry  # noqa: F401
from app.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database schema created successfully.")


if __name__ == "__main__":
    main()