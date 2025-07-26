"""базовая миграция

Revision ID: cacce4fb47ec
Revises:
Create Date: 2025-07-26 19:24:14.045307

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cacce4fb47ec"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "Book_reasons",
        sa.Column("reason_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("reason_id"),
        sa.UniqueConstraint("title"),
    )
    op.create_table(
        "Books",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("date_publicated", sa.Date(), nullable=False),
        sa.Column("age_limit", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "language",
            sa.Enum(
                "ENGLISH",
                "RUSSIAN",
                "SPANISH",
                "FRENCH",
                "GERMAN",
                "CHINESE",
                "JAPANESE",
                "KOREAN",
                "PORTUGUESE",
                "ITALIAN",
                "ARABIC",
                "HINDI",
                "TURKISH",
                "POLISH",
                "UKRAINIAN",
                name="language_enum",
            ),
            nullable=False,
        ),
        sa.Column("is_rendered", sa.Boolean(), nullable=False),
        sa.Column("cover_link", sa.String(), nullable=True),
        sa.Column(
            "render_status",
            sa.Enum(
                "UPLOADED",
                "RENDERING",
                "READY",
                "FAILED",
                name="render_status",
            ),
            nullable=True,
        ),
        sa.Column("is_publicated", sa.Boolean(), nullable=False),
        sa.Column("total_pages", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("book_id"),
    )
    op.create_table(
        "Genres",
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("genre_id"),
        sa.UniqueConstraint("title"),
    )
    op.create_table(
        "Users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "USER",
                "AUTHOR",
                "ADMIN",
                "GENERAL_ADMIN",
                name="user_role_enum",
            ),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("surname", sa.String(), nullable=False),
        sa.Column("nickname", sa.String(length=30), nullable=False),
        sa.Column(
            "last_activity", sa.TIMESTAMP(timezone=True), nullable=False
        ),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "registation_date", sa.TIMESTAMP(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("nickname"),
    )
    op.create_table(
        "Banned_Users",
        sa.Column("ban_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ban_until", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["Users.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("ban_id"),
    )
    op.create_table(
        "Book_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("reason_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("is_checked", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["reason_id"], ["Book_reasons.reason_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "Books_authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["Users.user_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "Books_genres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["genre_id"],
            ["Genres.genre_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "Books_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("title_tag", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "Pages",
        sa.Column("page_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("page_id"),
    )
    op.create_table(
        "Reviews",
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=150), nullable=False),
        sa.Column(
            "publication_date", sa.TIMESTAMP(timezone=True), nullable=False
        ),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "rating >= 1 AND rating <= 5", name="rating_range_check"
        ),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["Users.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("review_id"),
    )
    op.create_table(
        "User_books_read",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_seen_page", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"], ["Books.book_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["Users.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("User_books_read")
    op.drop_table("Reviews")
    op.drop_table("Pages")
    op.drop_table("Books_tags")
    op.drop_table("Books_genres")
    op.drop_table("Books_authors")
    op.drop_table("Book_reports")
    op.drop_table("Banned_Users")
    op.drop_table("Users")
    op.drop_table("Genres")
    op.drop_table("Books")
    op.drop_table("Book_reasons")
