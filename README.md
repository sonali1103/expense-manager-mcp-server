# Expense Manager MCP Server

An **MCP server for managing personal expenses** using Python, FastMCP, and SQLite.

Connect it to **Claude Desktop** and manage your expenses using natural language.

## Features

* Add, update, and delete expenses
* Search expenses
* List expenses by date range
* Summarize spending by category
* Store data locally using SQLite
* Expose expense categories through an MCP resource

## Tech Stack

* Python 3.11+
* FastMCP
* Model Context Protocol (MCP)
* SQLite
* uv

## Setup

```bash
git clone https://github.com/sonali1103/expense-manager-mcp-server.git
cd expense-manager-mcp-server
uv sync
```

## Connect to Claude Desktop

### 1. Find your project path

From the project directory, run:

```bash
pwd
```

Copy the path returned. You'll need it in the Claude configuration.

### 2. Open Claude Desktop configuration

In **Claude Desktop**:

**Settings → Developer → Edit Config**

This opens `claude_desktop_config.json`.

On macOS, the file is located at:

```text
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 3. Add the MCP server

Add the following inside `mcpServers`:

```json
{
  "mcpServers": {
    "expense-manager": {
      "command": "uv",
      "args": [
        "--directory",
        "/YOUR/PATH/expense-manager-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

Replace:

```text
/YOUR/PATH/expense-manager-mcp-server
```

with the path you copied from `pwd`.

### 4. Restart Claude Desktop

Completely quit and reopen Claude Desktop.

Then click the **Connectors** icon near the chat box and verify that `expense-manager` is connected. Claude Desktop will show the MCP tools provided by the server.

## Try It

Once connected, ask Claude:

> "Add a $45 grocery expense for today."

> "Show me my expenses for this month."

> "How much did I spend on food this month?"

> "Find my travel expenses."

> "Delete expense 12."

## MCP Tools

| Tool              | Description                 |
| ----------------- | --------------------------- |
| `add_expense`     | Add an expense              |
| `list_expenses`   | List expenses by date range |
| `summarize`       | Summarize spending          |
| `update_expense`  | Update an expense           |
| `delete_expense`  | Delete an expense           |
| `search_expenses` | Search expenses             |

## Database

Expenses are stored locally in:

```text
expenses.db
```

The database and `expenses` table are created automatically when the server starts.

## Project Structure

```text
expense-manager-mcp-server/
├── main.py
├── categories.json
├── pyproject.toml
├── uv.lock
└── .gitignore
```

This project demonstrates how **Model Context Protocol connects an AI assistant to real application functionality and data through standardized tools**.

