import os
import sys
import socket
import threading
import time
import json
import requests
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler

# GitHub GraphQL API configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "your-github-token")
GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Initialize FastMCP server
mcp = FastMCP("GitHub Discussions", log_level="DEBUG")

# Server configuration
HOST = "0.0.0.0"
PORT = 8004

# Helper function to execute GraphQL queries/mutations
def execute_graphql(query: str, variables: dict = None) -> dict:
    payload = {"query": query, "variables": variables or {}}
    response = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL Error: {data['errors']}")
    return data["data"]

# Add this function after initializing the mcp object
def get_registered_tools():
    """Get a list of registered tool names"""
    # This is a workaround since FastMCP doesn't expose tools directly
    tools = []
    
    # Debug output to help diagnose the issue
    print("\n=== TOOL DISCOVERY ===")
    print("Looking for registered tools...")
    
    # First try to find tools by examining function attributes
    for name, func in globals().items():
        if callable(func):
            print(f"Checking function: {name}")
            
            # Check if this is a tool function
            is_tool = False
            tool_attrs = []
            
            # Check for various MCP-related attributes
            for attr_name in dir(func):
                if attr_name.startswith('__mcp') or 'mcp' in attr_name.lower():
                    tool_attrs.append(attr_name)
                    is_tool = True
            
            if tool_attrs:
                print(f"  Found MCP-related attributes: {', '.join(tool_attrs)}")
            
            # Also check for known tool names
            known_tools = [
                'list_discussions', 'get_discussion', 'create_discussion', 
                'add_discussion_comment', 'check_server_status'
            ]
            
            if name in known_tools:
                print(f"  Recognized as known tool by name")
                is_tool = True
            
            if is_tool:
                tools.append(name)
                print(f"  ✓ Added tool: {name}")
    
    # If we still don't find any tools, use hardcoded list
    if not tools:
        print("No tools found via function inspection, using hardcoded list")
        tools = [
            'list_discussions', 'get_discussion', 'create_discussion', 
            'add_discussion_comment', 'check_server_status'
        ]
        for tool in tools:
            print(f"  ✓ Added hardcoded tool: {tool}")
    
    print(f"Total tools discovered: {len(tools)}")
    return tools

# Add this method to the FastMCP class
mcp.get_registered_tools = get_registered_tools

@mcp.tool()
def list_discussions(owner, repo):
    """
    List discussions in a repository
    
    Args:
        owner: Repository owner (e.g., username or org)
        repo: Repository name
    """
    print(f"Tool call: list_discussions for {owner}/{repo}")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        discussions(first: 10) {
          nodes {
            id
            title
            number
            url
          }
        }
      }
    }
    """
        variables = {"owner": owner, "repo": repo}
    data = execute_graphql(query, variables)
    discussions = data["repository"]["discussions"]["nodes"]
        
    if not discussions:
            return {
                "status": "success",
                "message": "No discussions found.",
                "discussions": []
            }
        
        formatted_discussions = []
        for d in discussions:
            formatted_discussions.append({
                "id": d["id"],
                "title": d["title"],
                "number": d["number"],
                "url": d["url"]
            })
        
        return {
            "status": "success",
            "discussions": formatted_discussions
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def get_discussion(owner, repo, discussion_id):
    """
    Get details of a specific discussion
    
    Args:
        owner: Repository owner (e.g., username or org)
        repo: Repository name
        discussion_id: Discussion ID (e.g., D_kwDOG7Pz9s4APjm1)
    """
    print(f"Tool call: get_discussion for {owner}/{repo} discussion {discussion_id}")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # First, we need to get the discussion number from the ID
        # The GitHub GraphQL API requires the discussion number, not the ID
        query_for_number = """
    query($owner: String!, $repo: String!, $discussionId: ID!) {
      repository(owner: $owner, name: $repo) {
            discussion(number: $discussionId) {
              number
            }
          }
        }
        """
        
        # Extract the discussion number from the ID
        # Discussion IDs are in the format D_kwDOIPDwls4AfBPd
        # We need to extract the number from the URL or use a different approach
        
        # Let's try to get the discussion directly using the ID
        query = """
        query($owner: String!, $repo: String!, $discussionNumber: Int!) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $discussionNumber) {
          title
          number
          body
          url
          author { login }
          createdAt
          comments(first: 5) {
            nodes {
              body
              author { login }
            }
          }
        }
      }
    }
    """
        
        # Extract the discussion number from the URL
        # If the discussion_id is a full URL, extract the number
        if discussion_id.startswith("http"):
            discussion_number = int(discussion_id.split("/")[-1])
        else:
            # Try to extract from the discussion ID format
            # For now, let's use the list_discussions tool to find the number
            list_response = list_discussions(owner, repo)
            if list_response.get("status") != "success":
                return {
                    "status": "error",
                    "message": "Failed to find discussion number from ID"
                }
                
            discussions = list_response.get("discussions", [])
            discussion_number = None
            for disc in discussions:
                if disc.get("id") == discussion_id:
                    # Extract number from URL
                    url = disc.get("url", "")
                    if url:
                        discussion_number = int(url.split("/")[-1])
                    break
                    
            if not discussion_number:
                return {
                    "status": "error",
                    "message": f"Could not find discussion with ID: {discussion_id}"
                }
        
        variables = {"owner": owner, "repo": repo, "discussionNumber": discussion_number}
    data = execute_graphql(query, variables)
    discussion = data["repository"]["discussion"]
        
    if not discussion:
            return {
                "status": "error",
                "message": "Discussion not found."
            }
        
        comments = []
        for c in discussion["comments"]["nodes"]:
            comments.append({
                "author": c["author"]["login"] if c["author"] else "Anonymous",
                "body": c["body"]
            })
        
        return {
            "status": "success",
            "discussion": {
                "title": discussion["title"],
                "number": discussion["number"],
                "body": discussion["body"],
                "url": discussion["url"],
                "author": discussion["author"]["login"] if discussion["author"] else "Anonymous",
                "created_at": discussion["createdAt"],
                "comments": comments
            }
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def create_discussion(owner, repo, title, body, category_id):
    """
    Create a new discussion
    
    Args:
        owner: Repository owner (e.g., username or org)
        repo: Repository name
        title: Title of the new discussion
        body: Body text of the discussion
        category_id: ID of the discussion category
    """
    print(f"Tool call: create_discussion in {owner}/{repo}")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # First get the repository ID
        repo_id = get_repo_id(owner, repo)
        
    mutation = """
    mutation($input: CreateDiscussionInput!) {
      createDiscussion(input: $input) {
        discussion {
          id
          title
          url
        }
      }
    }
    """
    variables = {
        "input": {
                "repositoryId": repo_id,
                "title": title,
                "body": body,
                "categoryId": category_id
        }
    }
    data = execute_graphql(mutation, variables)
    discussion = data["createDiscussion"]["discussion"]
        
        return {
            "status": "success",
            "discussion": {
                "id": discussion["id"],
                "title": discussion["title"],
                "url": discussion["url"]
            },
            "message": f"Discussion created: {discussion['title']}"
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def add_discussion_comment(owner, repo, discussion_id, body):
    """
    Add a comment to a discussion
    
    Args:
        owner: Repository owner (e.g., username or org)
        repo: Repository name
        discussion_id: Discussion ID
        body: Body text of the comment
    """
    print(f"Tool call: add_discussion_comment to {owner}/{repo} discussion {discussion_id}")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
    mutation = """
    mutation($input: AddDiscussionCommentInput!) {
      addDiscussionComment(input: $input) {
        comment {
          id
          body
          author { login }
        }
      }
    }
    """
    variables = {
        "input": {
                "discussionId": discussion_id,
                "body": body
        }
    }
    data = execute_graphql(mutation, variables)
    comment = data["addDiscussionComment"]["comment"]
        
        return {
            "status": "success",
            "comment": {
                "id": comment["id"],
                "body": comment["body"],
                "author": comment["author"]["login"]
            },
            "message": f"Comment added by {comment['author']['login']}"
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def check_server_status():
    """Check the status of the GitHub MCP server"""
    print(f"Tool call: check_server_status at {datetime.datetime.now()}")
    
    # Check GitHub token
    token_configured = bool(GITHUB_TOKEN and GITHUB_TOKEN != "your-github-token")
    
    return {
        "status": "online",
        "server_name": "GitHub Discussions MCP Server",
        "version": "1.0.0",
        "github_token_configured": token_configured,
        "pid": os.getpid(),
        "timestamp": datetime.datetime.now().isoformat()
    }

@mcp.tool()
def find_top_repositories(language=None, min_stars=1000, limit=10):
    """
    Find top public repositories on GitHub
    
    Args:
        language: Filter by programming language (optional)
        min_stars: Minimum number of stars (default: 1000)
        limit: Maximum number of repositories to return (default: 10)
    """
    print(f"Tool call: find_top_repositories (language={language}, min_stars={min_stars}, limit={limit})")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # Construct the GraphQL query
        query = """
        query($queryString: String!, $limit: Int!) {
          search(query: $queryString, type: REPOSITORY, first: $limit) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  name
                  owner { login }
                  stargazerCount
                  description
                  primaryLanguage {
                    name
                  }
                  url
                  id
                  hasDiscussionsEnabled
                }
              }
            }
          }
        }
        """
        
        # Build the query string
        query_parts = ["is:public"]
        if language:
            query_parts.append(f"language:{language}")
        query_parts.append(f"stars:>={min_stars}")
        query_string = " ".join(query_parts)
        
        variables = {
            "queryString": query_string,
            "limit": limit
        }
        
        data = execute_graphql(query, variables)
        search_results = data["search"]["edges"]
        
        if not search_results:
            return {
                "status": "success",
                "message": "No repositories found matching the criteria.",
                "repositories": []
            }
        
        formatted_repos = []
        for edge in search_results:
            repo = edge["node"]
            formatted_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "full_name": repo["nameWithOwner"],
                "stars": repo["stargazerCount"],
                "description": repo["description"] or "",
                "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "url": repo["url"],
                "has_discussions": repo["hasDiscussionsEnabled"]
            })
        
        return {
            "status": "success",
            "repositories": formatted_repos,
            "total_count": data["search"]["repositoryCount"]
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def get_top_repos_by_stars(limit=10):
    """
    Get top repositories by star count
    
    Args:
        limit: Maximum number of repositories to return (default: 10)
    """
    print(f"Tool call: get_top_repos_by_stars (limit={limit})")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # Construct the GraphQL query
        query = """
        query($queryString: String!, $limit: Int!) {
          search(query: $queryString, type: REPOSITORY, first: $limit) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  name
                  owner { login }
                  stargazerCount
                  description
                  primaryLanguage {
                    name
                  }
                  url
                  id
                  hasDiscussionsEnabled
                }
              }
            }
          }
        }
        """
        
        # Build the query string for most starred repos
        query_string = "is:public sort:stars-desc"
        
        variables = {
            "queryString": query_string,
            "limit": limit
        }
        
        data = execute_graphql(query, variables)
        search_results = data["search"]["edges"]
        
        if not search_results:
            return {
                "status": "success",
                "message": "No repositories found matching the criteria.",
                "repositories": []
            }
        
        formatted_repos = []
        for edge in search_results:
            repo = edge["node"]
            formatted_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "full_name": repo["nameWithOwner"],
                "stars": repo["stargazerCount"],
                "description": repo["description"] or "",
                "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "url": repo["url"],
                "has_discussions": repo["hasDiscussionsEnabled"]
            })
        
        return {
            "status": "success",
            "repositories": formatted_repos,
            "total_count": data["search"]["repositoryCount"]
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def get_top_repos_by_activity(limit=10):
    """
    Get top repositories by recent activity
    
    Args:
        limit: Maximum number of repositories to return (default: 10)
    """
    print(f"Tool call: get_top_repos_by_activity (limit={limit})")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # Construct the GraphQL query
        query = """
        query($queryString: String!, $limit: Int!) {
          search(query: $queryString, type: REPOSITORY, first: $limit) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  name
                  owner { login }
                  stargazerCount
                  description
                  primaryLanguage {
                    name
                  }
                  url
                  id
                  hasDiscussionsEnabled
                  updatedAt
                }
              }
            }
          }
        }
        """
        
        # Build the query string for recently active repos
        query_string = "is:public sort:updated-desc"
        
        variables = {
            "queryString": query_string,
            "limit": limit
        }
        
        data = execute_graphql(query, variables)
        search_results = data["search"]["edges"]
        
        if not search_results:
            return {
                "status": "success",
                "message": "No repositories found matching the criteria.",
                "repositories": []
            }
        
        formatted_repos = []
        for edge in search_results:
            repo = edge["node"]
            formatted_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "full_name": repo["nameWithOwner"],
                "stars": repo["stargazerCount"],
                "description": repo["description"] or "",
                "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "url": repo["url"],
                "has_discussions": repo["hasDiscussionsEnabled"],
                "updated_at": repo["updatedAt"]
            })
        
        return {
            "status": "success",
            "repositories": formatted_repos,
            "total_count": data["search"]["repositoryCount"]
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def get_top_language_repos(language, limit=10):
    """
    Get top repositories for a specific programming language
    
    Args:
        language: Programming language (e.g., Python, JavaScript)
        limit: Maximum number of repositories to return (default: 10)
    """
    print(f"Tool call: get_top_language_repos (language={language}, limit={limit})")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # Construct the GraphQL query
        query = """
        query($queryString: String!, $limit: Int!) {
          search(query: $queryString, type: REPOSITORY, first: $limit) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  name
                  owner { login }
                  stargazerCount
                  description
                  primaryLanguage {
                    name
                  }
                  url
                  id
                  hasDiscussionsEnabled
                }
              }
            }
          }
        }
        """
        
        # Build the query string for language-specific repos
        query_string = f"is:public language:{language} sort:stars-desc"
        
        variables = {
            "queryString": query_string,
            "limit": limit
        }
        
        data = execute_graphql(query, variables)
        search_results = data["search"]["edges"]
        
        if not search_results:
            return {
                "status": "success",
                "message": f"No {language} repositories found.",
                "repositories": []
            }
        
        formatted_repos = []
        for edge in search_results:
            repo = edge["node"]
            formatted_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "full_name": repo["nameWithOwner"],
                "stars": repo["stargazerCount"],
                "description": repo["description"] or "",
                "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "url": repo["url"],
                "has_discussions": repo["hasDiscussionsEnabled"]
            })
        
        return {
            "status": "success",
            "repositories": formatted_repos,
            "total_count": data["search"]["repositoryCount"]
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def get_top_ai_llm_repos(limit=10):
    """
    Get top AI/LLM repositories
    
    Args:
        limit: Maximum number of repositories to return (default: 10)
    """
    print(f"Tool call: get_top_ai_llm_repos (limit={limit})")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # Construct the GraphQL query
        query = """
        query($queryString: String!, $limit: Int!) {
          search(query: $queryString, type: REPOSITORY, first: $limit) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  name
                  owner { login }
                  stargazerCount
                  description
                  primaryLanguage {
                    name
                  }
                  url
                  id
                  hasDiscussionsEnabled
                }
              }
            }
          }
        }
        """
        
        # Build the query string for AI/LLM repos
        query_string = "is:public topic:ai topic:machine-learning topic:llm sort:stars-desc"
        
        variables = {
            "queryString": query_string,
            "limit": limit
        }
        
        data = execute_graphql(query, variables)
        search_results = data["search"]["edges"]
        
        if not search_results:
            return {
                "status": "success",
                "message": "No AI/LLM repositories found.",
                "repositories": []
            }
        
        formatted_repos = []
        for edge in search_results:
            repo = edge["node"]
            formatted_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "full_name": repo["nameWithOwner"],
                "stars": repo["stargazerCount"],
                "description": repo["description"] or "",
                "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "url": repo["url"],
                "has_discussions": repo["hasDiscussionsEnabled"]
            })
        
        return {
            "status": "success",
            "repositories": formatted_repos,
            "total_count": data["search"]["repositoryCount"]
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@mcp.tool()
def get_recently_active_repos(limit=10):
    """
    Get recently active repositories
    
    Args:
        limit: Maximum number of repositories to return (default: 10)
    """
    print(f"Tool call: get_recently_active_repos (limit={limit})")
    
    # Validate GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        return {
            "status": "error",
            "message": "GitHub token not configured. Please set the GITHUB_TOKEN environment variable."
        }
    
    try:
        # Construct the GraphQL query
        query = """
        query($queryString: String!, $limit: Int!) {
          search(query: $queryString, type: REPOSITORY, first: $limit) {
            repositoryCount
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  name
                  owner { login }
                  stargazerCount
                  description
                  primaryLanguage {
                    name
                  }
                  url
                  id
                  hasDiscussionsEnabled
                }
              }
            }
          }
        }
        """
        
        # Build the query string for recently active repos
        # Add minimum stars and filter for repos with discussions enabled
        query_string = "is:public stars:>1000 sort:updated-desc"
        
        variables = {
            "queryString": query_string,
            "limit": limit
        }
        
        data = execute_graphql(query, variables)
        search_results = data["search"]["edges"]
        
        if not search_results:
            return {
                "status": "success",
                "message": "No repositories found matching the criteria.",
                "repositories": []
            }
        
        formatted_repos = []
        for edge in search_results:
            repo = edge["node"]
            formatted_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "full_name": repo["nameWithOwner"],
                "stars": repo["stargazerCount"],
                "description": repo["description"] or "",
                "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "url": repo["url"],
                "has_discussions": repo["hasDiscussionsEnabled"]
            })
        
        return {
            "status": "success",
            "repositories": formatted_repos,
            "total_count": data["search"]["repositoryCount"]
        }
    except Exception as e:
        print(f"Error calling GitHub API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

# Helper function to get repository ID (required for creating discussions)
def get_repo_id(owner, repo):
    """Get the GitHub repository ID"""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        id
      }
    }
    """
    variables = {"owner": owner, "repo": repo}
    data = execute_graphql(query, variables)
    return data["repository"]["id"]

# Helper function to check if a port is in use
def check_port_in_use(host, port):
    """Check if a port is in use on the specified host"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

# Custom HTTP handler for MCP
class MCPHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/tools":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Get list of registered tools
            tools = get_registered_tools()
            tool_list = []
            
            for tool_name in tools:
                # Get the function object if possible
                tool_func = globals().get(tool_name)
                
                # Get the description from the docstring if available
                description = "No description available"
                if tool_func and tool_func.__doc__:
                    description = tool_func.__doc__.strip()
                
                tool_list.append({
                    "name": tool_name,
                    "description": description
                })
            
            self.wfile.write(json.dumps(tool_list).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not found")
    
    def do_POST(self):
        if self.path.startswith("/tools/"):
            tool_name = self.path.split("/tools/")[1]
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            
            try:
                params = json.loads(post_data) if post_data else {}
                
                # Get the tool function
                tool_func = globals().get(tool_name)
                if not tool_func or not callable(tool_func):
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Tool '{tool_name}' not found"}).encode())
                    return
                
                # Call the tool
                result = tool_func(**params)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Error calling tool: {str(e)}"}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not found")

def main():
    """Main function to start the MCP server"""
    print(f"Starting GitHub Discussions MCP Server v1.0.0...")
    print("This server implements the Model Context Protocol for GitHub Discussions.")
    print(f"Server PID: {os.getpid()}")
    
    # Check GitHub token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-github-token":
        print("\n⚠️ WARNING: GitHub token not configured!")
        print("Please set the GITHUB_TOKEN environment variable.")
        print("\nThe server will start, but API calls will fail until a token is configured.")
    else:
        print("\n✓ GitHub token configured.")
    
    # Check if port is already in use
    if check_port_in_use(HOST, PORT):
        print(f"WARNING: Port {PORT} is already in use. The server may not start correctly.")
        # Try to kill the process using the port
        try:
            print("Attempting to free the port...")
            if sys.platform.startswith('linux'):
                os.system(f"fuser -k {PORT}/tcp")
                print(f"Killed process using port {PORT}")
            else:
                print("Automatic port freeing only supported on Linux")
        except Exception as e:
            print(f"Error freeing port: {e}")
    
    print(f"Binding to {HOST}:{PORT}...")
    
    try:
        # Create and start HTTP server
        server = HTTPServer((HOST, PORT), MCPHTTPHandler)
        print(f"Server started at http://{HOST}:{PORT}")
        print("Press Ctrl+C to stop the server")
        
        # Start the server in a separate thread to avoid blocking
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Print a message every 10 seconds to show the server is still running
        try:
            while True:
                time.sleep(10)
                print(f"Server running at http://{HOST}:{PORT} (PID: {os.getpid()})")
        except KeyboardInterrupt:
            print("Server stopped by user")
            server.shutdown()
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    
    return 0

# Run the server
if __name__ == "__main__":
    sys.exit(main())