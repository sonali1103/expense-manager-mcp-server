from __future__ import annotations

import sqlite3
from pathlib import Path

from fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"
CATEGORIES_PATH = BASE_DIR / "categories.json"

mcp = FastMCP("ExpenseTracker")


def get_connection() -> sqlite3.Connection:
    """Create a connection to the local SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the expenses table if it does not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
            """
        )


init_db()


@mcp.tool
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
) -> dict:
    """Add a new expense entry."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses (
                date, amount, category, subcategory, note
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note),
        )

        return {
            "status": "ok",
            "id": cursor.lastrowid,
        }


@mcp.tool
def list_expenses(
    start_date: str,
    end_date: str,
) -> list[dict]:
    """List expenses within an inclusive date range."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC, id ASC
            """,
            (start_date, end_date),
        ).fetchall()

        return [dict(row) for row in rows]


@mcp.tool
def summarize(
    start_date: str,
    end_date: str,
    category: str | None = None,
) -> list[dict]:
    """Summarize expenses by category within an inclusive date range."""

    query = """
        SELECT
            category,
            SUM(amount) AS total_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """

    params: list[str] = [start_date, end_date]

    if category is not None:
        query += " AND category = ?"
        params.append(category)

    query += """
        GROUP BY category
        ORDER BY category ASC
    """

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

        return [dict(row) for row in rows]


@mcp.tool
def update_expense(
    id: int,
    date: str | None = None,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    note: str | None = None,
) -> dict:
    """Update only the provided fields of an existing expense."""

    fields: list[str] = []
    values: list[object] = []

    updates = {
        "date": date,
        "amount": amount,
        "category": category,
        "subcategory": subcategory,
        "note": note,
    }

    for column, value in updates.items():
        if value is not None:
            fields.append(f"{column} = ?")
            values.append(value)

    if not fields:
        return {
            "status": "error",
            "message": "No fields provided to update",
        }

    values.append(id)

    query = f"""
        UPDATE expenses
        SET {", ".join(fields)}
        WHERE id = ?
    """

    with get_connection() as connection:
        cursor = connection.execute(query, values)

        if cursor.rowcount == 0:
            return {
                "status": "error",
                "message": f"No expense with id {id}",
            }

        return {
            "status": "ok",
            "updated_id": id,
        }


@mcp.tool
def delete_expense(id: int) -> dict:
    """Delete an expense entry by ID."""

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (id,),
        )

        if cursor.rowcount == 0:
            return {
                "status": "error",
                "message": f"No expense with id {id}",
            }

        return {
            "status": "ok",
            "deleted_id": id,
        }


@mcp.tool
def search_expenses(
    query: str,
    limit: int = 50,
) -> list[dict]:
    """Search expenses by category, subcategory, or note."""

    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")

    like = f"%{query}%"

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            WHERE category LIKE ?
               OR subcategory LIKE ?
               OR note LIKE ?
            ORDER BY date DESC, id DESC
            LIMIT ?
            """,
            (like, like, like, limit),
        ).fetchall()

        return [dict(row) for row in rows]


@mcp.resource("expense://categories")
def categories() -> str:
    """Return available expense categories as JSON."""

    with CATEGORIES_PATH.open("r", encoding="utf-8") as file:
        return file.read()


if __name__ == "__main__":
    mcp.run()
