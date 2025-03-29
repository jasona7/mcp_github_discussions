# GitHub MCP Server

A versatile and powerful server implementation of the Model Context Protocol (MCP), designed to seamlessly interact with GitHub repositories, issues, discussions, and beyond. This server enables efficient management, automation, and enhanced collaboration by providing a structured interface to query, update, and analyze GitHub data. With support for integrating custom workflows, handling repository metadata, and facilitating real-time interactions with issues and discussions, the MCP server empowers developers and teams to streamline their GitHub experience. Whether you're building tools, automating tasks, or exploring new ways to engage with GitHub's ecosystem, this server offers a robust foundation for your projects.


## Overview

This MCP server provides a bridge between AI assistants and the GitHub API, allowing AI models to perform actions like:

- Searching repositories
- Creating and managing issues
- Participating in discussions
- Analyzing repository activity
- Fetching repository statistics

## Features

- **Repository Management**: Search, analyze, and interact with GitHub repositories
- **Issue Tracking**: Create, update, and search issues
- **Discussion Integration**: Participate in GitHub Discussions
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
- `get_repo_id`: Get the GitHub repository ID (helper function)

## Configuration

The server can be configured using environment variables:

- `GITHUB_TOKEN`: Your GitHub Personal Access Token
- `MCP_HOST`: Host to bind the server to (default: localhost)
- `MCP_PORT`: Port to bind the server to (default: 8004)


## Integration with Next.js

In your Next.js application, you can call the MCP server like this:

```javascript
const response = await fetch('http://localhost:8004/mcp', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tool: 'search_repositories',
    args: { query: 'react' }
  })
});
```

## Troubleshooting

- **Connection Refused**: Make sure the server is running and the port is not blocked by a firewall
- **Authentication Errors**: Verify your GitHub token has the necessary permissions
- **Rate Limiting**: GitHub API has rate limits; the server will handle these but may slow down during heavy usage

## License

MIT License - see the LICENSE file for details

