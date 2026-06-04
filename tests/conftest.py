from collections.abc import Generator
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


def reset_postgres_database(db: Session) -> None:
    db.execute(
        text(
            "TRUNCATE TABLE application_status_history, job_applications "
            "RESTART IDENTITY CASCADE"
        )
    )
    db.commit()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    test_database_url = os.getenv("TEST_DATABASE_URL")
    if test_database_url is None:
        engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
    else:
        engine = create_engine(test_database_url)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    db = TestingSessionLocal()
    if test_database_url is not None:
        reset_postgres_database(db)

    try:
        yield db
    finally:
        if test_database_url is None:
            db.close()
            Base.metadata.drop_all(bind=engine)
        else:
            reset_postgres_database(db)
            db.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
