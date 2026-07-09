import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None


def _normalize_database_url(raw_url: str) -> str:
    # SQLAlchemy defaults postgresql:// to psycopg2; force psycopg v3 driver.
    if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+psycopg://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", "postgresql://postgres:postgresdb@my-postgres:5432/goldsavings")
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


@contextmanager
def get_connection():
    database_url = get_database_url()
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    if psycopg is None:
        raise RuntimeError("psycopg is not installed")

    connection = psycopg.connect(database_url)
    try:
        yield connection
    finally:
        connection.close()


def init_database() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    token_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMP NOT NULL,
                    revoked_at TIMESTAMP NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    usermame TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS stores (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    culture TEXT NOT NULL,
                    note TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scheduled_notifications (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    scheduled_for TIMESTAMPTZ NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    dispatched_at TIMESTAMPTZ NULL
                );
                CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_pending_time
                    ON scheduled_notifications (status, scheduled_for);

                CREATE TABLE IF NOT EXISTS notifications (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    scheduled_notification_id BIGINT NULL REFERENCES scheduled_notifications(id) ON DELETE SET NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    read_at TIMESTAMPTZ NULL
                );
                CREATE INDEX IF NOT EXISTS idx_notifications_user_created_at
                    ON notifications (user_id, created_at DESC);
                """
            )
            connection.commit()
        finally:
            cursor.close()

#id, name, address, phone, culture, note
