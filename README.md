# SQLite Explorer

A beautiful terminal-based UI for exploring SQLite databases using the Model Context Protocol with rich formatting and navigation. The explorer provides an intuitive interface for MCP tools that inspect table schemas, run SQL queries, and analyze database structures without leaving the terminal environment. Built with a client-server architecture, it separates data access from presentation concerns, allowing for clean code organization and maintainable components. The rich text formatting capabilities enhance readability of complex database information, making it easier to understand relationships between tables and interpret query results at a glance.


## Features

- **Rich Terminal UI**: Beautiful tables, syntax highlighting, and formatted output
- **Database Discovery**: Automatically finds SQLite databases in your project
- **Table Exploration**: View table schemas, indexes, and statistics
- **SQL Queries**: Run custom SQL queries with syntax highlighting
- **Database Info**: Get detailed information about your database structure

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Install from GitHub

```bash
git clone https://github.com/jasona7/sqlite-mcp-explorer.git
cd sqlite-mcp-explorer
pip install -r requirements.txt
``` 

### Run the Server

```bash
python run_sqlite_explorer.py
``` 

## Usage

Once the explorer is running, you'll see a menu with the following options:

1. **List tables**: Shows all tables in the database
2. **Describe table**: View detailed schema information for a specific table
3. **Run query**: Execute a custom SQL query (SELECT only for safety)
4. **Database info**: View general information about the database
5. **Exit**: Close the explorer

## Architecture

SQLite Explorer is built as a wrapper python script for a Model Context Protocol (MCP) Appication with these key components:

1. **Server (`simple_sqlite_server.py`)**: A Flask-based HTTP server that provides an API to interact with the SQLite database. Exposes endpoints for database operations.

2. **Client (`rich_sqlite_client.py`)**: A rich terminal UI that communicates with the server and displays the results using the Rich library for style & formatting.

3. **Launcher (`run_sqlite_explorer.py`)**: Handles starting both components and managing their lifecycle. Provides database discovery and selection.

This architecture demonstrates:
- Clean separation of concerns between data access (server) and presentation (client)
- HTTP-based communication between components
- Coordinated lifecycle management

## Requirements

- flask
- rich
- requests

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
