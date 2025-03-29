#!/usr/bin/env python3
"""
MCP GitHub Discussions HTTP Client

This client connects to the MCP GitHub Discussions Server using HTTP.
It provides a terminal interface for interacting with GitHub Discussions
and other GitHub operations.
"""
import sys
import requests
import json
import socket
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.markdown import Markdown
import time
import os

# Server address
SERVER_HOST = "127.0.0.1"  # Use IP address instead of hostname
SERVER_PORT = 8004  # Match the port in the server
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

console = Console()

def call_tool(tool_name, params=None):
    """
    Calls a tool on the MCP server using HTTP.
    
    Args:
        tool_name: The name of the tool to call
        params: A dictionary of parameters to pass to the tool
    
    Returns:
        The response from the server, or None on error
    """
    try:
        if params is None:
            params = {}
        
        url = f"{BASE_URL}/tools/{tool_name}"
        response = requests.post(url, json=params, timeout=10)
        
        if response.status_code == 200:
            if not response.text:
                console.print("[bold red]Error: Server returned empty response[/bold red]")
                return None
            try:
                return response.json()
            except json.JSONDecodeError:
                console.print(f"[bold red]Error: Invalid JSON response: {response.text}[/bold red]")
                return None
        else:
            console.print(f"[bold red]Error: Server returned status code {response.status_code}[/bold red]")
            console.print(f"Response: {response.text}")
            return None
    except requests.RequestException as e:
        console.print(f"[bold red]Request error: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        return None

def list_tools():
    """Lists all available tools on the server"""
    try:
        # First verify the server is running with a simple request
        if not check_server_running():
            console.print("[bold red]Server is not responding to basic requests[/bold red]")
            return None
            
        url = f"{BASE_URL}/tools"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold red]Error: Server returned status code {response.status_code}[/bold red]")
            return None
    except requests.RequestException as e:
        console.print(f"[bold red]Request error: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        return None

def check_server_running():
    """Check if the server is running and responding to requests"""
    try:
        response = requests.get(f"{BASE_URL}/tools", timeout=2)
        return response.status_code == 200
    except:
        return False

def find_top_repositories(language=None, min_stars=1000, limit=10):
    """
    Find top public repositories on GitHub
    
    Args:
        language: Filter by programming language (optional)
        min_stars: Minimum number of stars (default: 1000)
        limit: Maximum number of repositories to return (default: 10)
    """
    try:
        # Call the server's tool for finding top repositories
        params = {
            "language": language,
            "min_stars": min_stars,
            "limit": limit
        }
        return call_tool("find_top_repositories", params)
    except Exception as e:
        console.print(f"[bold red]Error finding top repositories: {e}[/bold red]")
        return None

def display_repository_list(repositories):
    """Display a list of repositories in a table format"""
    if not repositories:
        console.print("[yellow]No repositories found.[/yellow]")
        return
    
    table = Table(title="Top GitHub Repositories")
    table.add_column("#", style="dim")
    table.add_column("Repository", style="green")
    table.add_column("Stars", justify="right")
    table.add_column("Language", style="blue")
    table.add_column("Description")
    
    for i, repo in enumerate(repositories, 1):
        table.add_row(
            str(i),
            f"{repo.get('owner', '')}/{repo.get('name', '')}",
            f"{repo.get('stars', 0):,}",
            repo.get('language', 'Unknown'),
            repo.get('description', '')[:80] + ('...' if len(repo.get('description', '')) > 80 else '')
        )
    
    console.print(table)

def main():
    """Main function to run the client"""
    console.print(Panel(
        "[bold]MCP GitHub Discussions Explorer[/bold]\nA terminal UI for interacting with GitHub Discussions",
        title="GitHub Discussions Explorer",
        border_style="green"
    ))
    
    console.print("Connecting to server...")
    
    # Check if server is running
    if not check_server_running():
        console.print("[bold red]Error: Could not connect to the server.[/bold red]")
        console.print(f"Make sure the server is running at {BASE_URL}")
        return 1
    
    # Get available tools
    tools = list_tools()
    if tools:
        console.print(f"Connected to server. {len(tools)} tools available.")
    else:
        console.print("[bold red]Error: Could not retrieve tools from server.[/bold red]")
        return 1
    
    # Main menu loop
    debug_mode = False
    while True:
        console.print("\nAvailable Actions:")
        console.print("1. Browse Top Repositories")
        console.print("2. List Discussions (by repo)")
        console.print("3. Get Discussion Details")
        console.print("4. Check Server Status")
        console.print("5. Exit")
        console.print("6. Toggle Debug Mode")
        
        choices = ["1", "2", "3", "4", "5", "6"]
        choice = Prompt.ask("Enter the number of the action you want to perform", choices=choices, default="1")

        if choice == "1":
            console.print("\nBrowse Top Repositories:")
            console.print("1. Top Repos by Recent Activity")
            console.print("2. Top Repos by Star Count")
            console.print("3. Top Python Repos")
            console.print("4. Top JavaScript Repos")
            console.print("5. Top AI/LLM Repos")
            console.print("6. Back to Main Menu")
            
            repo_choices = ["1", "2", "3", "4", "5", "6"]
            repo_choice = Prompt.ask("Select repository category", choices=repo_choices, default="1")
            
            if repo_choice == "6":
                continue
                
            limit = IntPrompt.ask("Number of repositories to show", default=10)
            
            if repo_choice == "1":
                console.print("[yellow]Finding top repositories by recent activity...[/yellow]")
                response = call_tool("get_top_repos_by_activity", {"limit": limit})
            elif repo_choice == "2":
                console.print("[yellow]Finding top repositories by star count...[/yellow]")
                response = call_tool("get_top_repos_by_stars", {"limit": limit})
            elif repo_choice == "3":
                console.print("[yellow]Finding top Python repositories...[/yellow]")
                response = call_tool("get_top_language_repos", {"language": "python", "limit": limit})
            elif repo_choice == "4":
                console.print("[yellow]Finding top JavaScript repositories...[/yellow]")
                response = call_tool("get_top_language_repos", {"language": "javascript", "limit": limit})
            elif repo_choice == "5":
                console.print("[yellow]Finding top AI/LLM repositories...[/yellow]")
                response = call_tool("get_top_ai_llm_repos", {"limit": limit})
            
            if response:
                if debug_mode:
                    console.print("[bold]JSON Response:[/bold]")
                    console.print_json(json.dumps(response, indent=2))
                
                if response.get("status") == "success":
                    repositories = response.get("repositories", [])
                    
                    if repositories:
                        table = Table(title=f"Top Repositories ({len(repositories)})")
                        table.add_column("#", style="cyan")
                        table.add_column("Repository", style="green")
                        table.add_column("Stars", style="yellow")
                        table.add_column("Language", style="magenta")
                        table.add_column("Has Discussions", style="blue")
                        
                        for i, repo in enumerate(repositories, 1):
                            table.add_row(
                                str(i),
                                repo.get("full_name", "Unknown"),
                                str(repo.get("stars", 0)),
                                repo.get("language", "Unknown"),
                                "✓" if repo.get("has_discussions") else "✗"
                            )
                        
                        console.print(table)
                        
                        # Filter repositories with discussions enabled
                        repos_with_discussions = [r for r in repositories if r.get("has_discussions")]
                        
                        if repos_with_discussions:
                            view_discussions = Prompt.ask(
                                "[yellow]View discussions for a repository?[/yellow]", 
                                choices=["y", "n"], 
                                default="y"
                            )
                            
                            if view_discussions.lower() == "y":
                                repo_index = IntPrompt.ask(
                                    "[yellow]Enter repository number (1-" + str(len(repositories)) + ")[/yellow]",
                                    default=1
                                )
                                
                                if 1 <= repo_index <= len(repositories):
                                    selected_repo = repositories[repo_index - 1]
                                    
                                    if not selected_repo.get("has_discussions"):
                                        console.print("[yellow]This repository does not have discussions enabled.[/yellow]")
                                        continue
                                    
                                    owner = selected_repo.get("owner")
                                    repo = selected_repo.get("name")
                                    
                                    console.print(f"[yellow]Listing discussions for {owner}/{repo}...[/yellow]")
                                    
                                    discussions_response = call_tool("list_discussions", {
                                        "owner": owner,
                                        "repo": repo
                                    })
                                    
                                    if discussions_response and discussions_response.get("status") == "success":
                                        discussions = discussions_response.get("discussions", [])
                                        
                                        if discussions:
                                            table = Table(title=f"Discussions in {owner}/{repo}")
                                            table.add_column("ID", style="cyan")
                                            table.add_column("Title", style="green")
                                            table.add_column("URL", style="blue")
                                            
                                            for d in discussions:
                                                table.add_row(
                                                    d.get("id", "Unknown"),
                                                    d.get("title", "Untitled"),
                                                    d.get("url", "No URL")
                                                )
                                            
                                            console.print(table)
                                            
                                            # Allow user to select a discussion to view details
                                            view_details = Prompt.ask(
                                                "[yellow]View discussion details?[/yellow]", 
                                                choices=["y", "n"], 
                                                default="y"
                                            )
                                            
                                            if view_details.lower() == "y":
                                                discussion_id = Prompt.ask("[yellow]Enter discussion ID[/yellow]")
                                                
                                                console.print(f"[yellow]Getting details for discussion ID: {discussion_id}[/yellow]")
                                                
                                                details_response = call_tool("get_discussion", {
                                                    "owner": owner,
                                                    "repo": repo,
                                                    "discussion_id": discussion_id
                                                })
                                                
                                                if details_response and details_response.get("status") == "success":
                                                    discussion_details = details_response.get("discussion", {})
                                                    
                                                    # Display discussion details with markdown rendering
                                                    console.print(Panel(
                                                        Markdown(f"# {discussion_details.get('title', 'Untitled')}\n\n"
                                                        f"{discussion_details.get('body', 'No content')}\n\n"
                                                        f"*By {discussion_details.get('author', 'Unknown')} on "
                                                        f"{discussion_details.get('created_at', 'Unknown date')}*"),
                                                        title=f"Discussion #{discussion_details.get('number', 'Unknown')}",
                                                        border_style="green"
                                                    ))
                                                    
                                                    comments = discussion_details.get("comments", [])
                                                    if comments:
                                                        console.print("\n[bold]Comments:[/bold]")
                                                        for i, comment in enumerate(comments, 1):
                                                            console.print(Panel(
                                                                Markdown(f"{comment.get('body', 'No content')}\n\n"
                                                                f"*By {comment.get('author', 'Unknown')}*"),
                                                                title=f"Comment #{i}",
                                                                border_style="blue"
                                                            ))
                                                    else:
                                                        console.print("[yellow]No comments on this discussion.[/yellow]")
                                                else:
                                                    console.print("[bold red]Failed to get discussion details.[/bold red]")
                                        else:
                                            console.print("[yellow]No discussions found in this repository.[/yellow]")
                                    else:
                                        console.print("[bold red]Failed to list discussions.[/bold red]")
                        else:
                            console.print("[yellow]None of the repositories have discussions enabled.[/yellow]")
                    else:
                        console.print("[yellow]No repositories found matching the criteria.[/yellow]")
                else:
                    console.print(f"[bold red]Error: {response.get('message', 'Unknown error')}[/bold red]")
            else:
                console.print("[yellow]Failed to find repositories.[/yellow]")

        elif choice == "2":
            owner = Prompt.ask("[yellow]Enter repository owner[/yellow]")
            repo = Prompt.ask("[yellow]Enter repository name[/yellow]")
            
            console.print(f"[yellow]Listing discussions for {owner}/{repo}...[/yellow]")
            response = call_tool("list_discussions", {
                "owner": owner,
                "repo": repo
            })
            
            if response:
                if debug_mode:
                    console.print("[bold]JSON Response:[/bold]")
                    console.print_json(json.dumps(response, indent=2))
                
                if response.get("status") == "success":
                    discussions = response.get("discussions", [])
                    
                    if discussions:
                        table = Table(title=f"Discussions in {owner}/{repo}")
                        table.add_column("ID", style="cyan")
                        table.add_column("Title", style="green")
                        table.add_column("URL", style="blue")
                        
                        for d in discussions:
                            table.add_row(
                                d.get("id", "Unknown"),
                                d.get("title", "Untitled"),
                                d.get("url", "No URL")
                            )
                        
                        console.print(table)
                        
                        # Allow user to select a discussion to view details
                        view_details = Prompt.ask(
                            "[yellow]View discussion details?[/yellow]", 
                            choices=["y", "n"], 
                            default="y"
                        )
                        
                        if view_details.lower() == "y":
                            discussion_id = Prompt.ask("[yellow]Enter discussion ID[/yellow]")
                            
                            console.print(f"[yellow]Getting details for discussion ID: {discussion_id}[/yellow]")
                            
                            details_response = call_tool("get_discussion", {
                                "owner": owner,
                                "repo": repo,
                                "discussion_id": discussion_id
                            })
                            
                            if details_response and details_response.get("status") == "success":
                                discussion_details = details_response.get("discussion", {})
                                
                                # Display discussion details with markdown rendering
                                console.print(Panel(
                                    Markdown(f"# {discussion_details.get('title', 'Untitled')}\n\n"
                                    f"{discussion_details.get('body', 'No content')}\n\n"
                                    f"*By {discussion_details.get('author', 'Unknown')} on "
                                    f"{discussion_details.get('created_at', 'Unknown date')}*"),
                                    title=f"Discussion #{discussion_details.get('number', 'Unknown')}",
                                    border_style="green"
                                ))
                                
                                comments = discussion_details.get("comments", [])
                                if comments:
                                    console.print("\n[bold]Comments:[/bold]")
                                    for i, comment in enumerate(comments, 1):
                                        console.print(Panel(
                                            Markdown(f"{comment.get('body', 'No content')}\n\n"
                                            f"*By {comment.get('author', 'Unknown')}*"),
                                            title=f"Comment #{i}",
                                            border_style="blue"
                                        ))
                                else:
                                    console.print("[yellow]No comments on this discussion.[/yellow]")
                            else:
                                console.print("[bold red]Failed to get discussion details.[/bold red]")
                    else:
                        console.print("[yellow]No discussions found in this repository.[/yellow]")
                else:
                    console.print(f"[bold red]Error: {response.get('message', 'Unknown error')}[/bold red]")
            else:
                console.print("[yellow]Failed to list discussions.[/yellow]")

        elif choice == "3":
            owner = Prompt.ask("[yellow]Enter repository owner[/yellow]")
            repo = Prompt.ask("[yellow]Enter repository name[/yellow]")
            discussion_id = Prompt.ask("[yellow]Enter discussion ID[/yellow]")
            
            console.print(f"[yellow]Getting details for discussion {discussion_id} in {owner}/{repo}...[/yellow]")
            response = call_tool("get_discussion", {
                "owner": owner,
                "repo": repo,
                "discussion_id": discussion_id
            })
            
            if response:
                if debug_mode:
                    console.print("[bold]JSON Response:[/bold]")
                    console.print_json(json.dumps(response, indent=2))
                
                if response.get("status") == "success":
                    discussion = response.get("discussion", {})
                    
                    # Display discussion details with markdown rendering
                    console.print(Panel(
                        Markdown(f"# {discussion.get('title', 'Untitled')}\n\n"
                        f"{discussion.get('body', 'No content')}\n\n"
                        f"*By {discussion.get('author', 'Unknown')} on "
                        f"{discussion.get('created_at', 'Unknown date')}*"),
                        title=f"Discussion #{discussion.get('number', 'Unknown')}",
                        border_style="green"
                    ))
                    
                    comments = discussion.get("comments", [])
                    if comments:
                        console.print("\n[bold]Comments:[/bold]")
                        for i, comment in enumerate(comments, 1):
                            console.print(Panel(
                                Markdown(f"{comment.get('body', 'No content')}\n\n"
                                f"*By {comment.get('author', 'Unknown')}*"),
                                title=f"Comment #{i}",
                                border_style="blue"
                            ))
                    else:
                        console.print("[yellow]No comments on this discussion.[/yellow]")
                else:
                    console.print(f"[bold red]Error: {response.get('message', 'Unknown error')}[/bold red]")
            else:
                console.print("[yellow]Failed to get discussion details.[/yellow]")

        elif choice == "4":
            console.print("[yellow]Checking server status...[/yellow]")
            response = call_tool("check_server_status")
            
            if response:
                # Always show JSON for server status
                console.print("[bold]JSON Response:[/bold]")
                console.print_json(json.dumps(response, indent=2))
            else:
                console.print("[yellow]Could not retrieve server status.[/yellow]")
                
        elif choice == "5":
            console.print("[bold green]Exiting MCP GitHub Discussions Explorer. Goodbye![/bold green]")
            break

        elif choice == "6":
            debug_mode = not debug_mode
            console.print(f"[yellow]Debug mode {'enabled' if debug_mode else 'disabled'}[/yellow]")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

