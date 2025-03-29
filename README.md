# GitHub MCP Server

A versatile and powerful server implementation of the Model Context Protocol (MCP), designed to seamlessly interact with GitHub repositories, issues, discussions, and beyond. This server enables efficient management, automation, and enhanced collaboration by providing a structured interface to query, update, and analyze GitHub data. With support for integrating custom workflows, handling repository metadata, and facilitating real-time interactions with issues and discussions, the MCP server empowers developers and teams to streamline their GitHub experience. Whether you're building tools, automating tasks, or exploring new ways to engage with GitHub's ecosystem, this server offers a robust foundation for your projects.


## Overview

This MCP server provides a bridge between AI assistants and the GitHub API, allowing AI models to perform actions like:

- Searching repositories
- Viewing discussions
- Analyzing repository activity
- Fetching repository statistics

## Features

- **Repository Management**: Search, analyze, and interact with GitHub repositories
- **Discussion Integration**: Analyze GitHub Discussions
- **Activity Analysis**: Get insights on repository activity and contributions
- **Search Capabilities**: Advanced search for repositories, code, and discussions

## Installation

### Prerequisites

- Python 3.8+
- GitHub Personal Access Token with appropriate permissions

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jasona7/mcp_github_discussions.git
   cd mcp_github_discussions
   ```

2. Install dependencies:
   ```bash
   pip install requests
   ```

3. Set up your GitHub token in the environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_personal_access_token
   ```

## Usage

### Starting the Server

Run the server with:

```bash
python scripts/mcp/github/mcp_github_server.py
```

The server will start on `localhost:8004` by default.

### Available Tools

The server provides the following tools:

- `search_repositories`: Search for repositories based on various criteria
- `get_repository_details`: Get detailed information about a repository
- `get_repository_issues`: Fetch issues from a repository
- `get_repository_discussions`: Fetch discussions from a repository
- `get_top_repos_by_activity`: Get trending repositories by activity

## Configuration

The server can be configured using environment variables:

- `GITHUB_TOKEN`: Your GitHub Personal Access Token
- `MCP_HOST`: Host to bind the server to (default: localhost)
- `MCP_PORT`: Port to bind the server to (default: 8004)


## Using the Client 

```
python scripts/mcp/github/mcp_github_client.py
╭──────────────────────────────── GitHub Discussions Explorer ────────────────────────────────╮
│ MCP GitHub Discussions Explorer                                                             │
│ A terminal UI for interacting with GitHub Discussions                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯
Connecting to server...
Connected to server. 5 tools available.

Available Actions:
1. Browse Top Repositories
2. List Discussions (by repo)
3. Get Discussion Details
4. Check Server Status
5. Exit
6. Toggle Debug Mode
Enter the number of the action you want to perform [1/2/3/4/5/6] (1): 1

Browse Top Repositories:
1. Top Repos by Recent Activity
2. Top Repos by Star Count
3. Top Python Repos
4. Top JavaScript Repos
5. Top AI/LLM Repos
6. Back to Main Menu
Select repository category [1/2/3/4/5/6] (1): 3
Number of repositories to show (10): 3
Finding top Python repositories...
                             Top Repositories (3)                             
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ # ┃ Repository                       ┃ Stars  ┃ Language ┃ Has Discussions ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 1 │ public-apis/public-apis          │ 334406 │ Python   │ ✗               │
│ 2 │ donnemartin/system-design-primer │ 294897 │ Python   │ ✗               │
│ 3 │ vinta/awesome-python             │ 238668 │ Python   │ ✗               │
└───┴──────────────────────────────────┴────────┴──────────┴─────────────────┘
None of the repositories have discussions enabled.

Available Actions:
1. Browse Top Repositories
2. List Discussions (by repo)
3. Get Discussion Details
4. Check Server Status
5. Exit
6. Toggle Debug Mode
Enter the number of the action you want to perform [1/2/3/4/5/6] (1): 
```

## Troubleshooting

- **Connection Refused**: Make sure the server is running and the port is not blocked by a firewall
- **Authentication Errors**: Verify your GitHub token has the necessary permissions
- **Rate Limiting**: GitHub API has rate limits; the server will handle these but may slow down during heavy usage

## License

MIT License - see the LICENSE file for details

