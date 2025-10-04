#!/usr/bin/env python3
"""
MCP Server for Todo List using FastMCP (2025)
"""

import asyncio
import httpx
from fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("TodoListMCPServer")

# FastAPI server URL
FASTAPI_URL = "http://localhost:8001"

async def make_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make HTTP request to FastAPI server"""
    url = f"{FASTAPI_URL}{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise Exception("Cannot connect to FastAPI server. Make sure it's running on http://localhost:8001")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")

@mcp.tool()
async def get_todos() -> str:
    """Get all todos from the FastAPI application"""
    todos = await make_request("GET", "/todos")
    todos_text = "\n".join([
        f"ID: {todo['id']} | {todo['title']} | {'✅' if todo['completed'] else '⏳'} | {todo.get('description', 'No description')}"
        for todo in todos
    ])
    return f"All Todos:\n{todos_text}"

@mcp.tool()
async def get_todo_stats() -> str:
    """Get statistics about todos (total, completed, pending)"""
    stats = await make_request("GET", "/todos/stats")
    return f"Todo Statistics:\nTotal Todos: {stats['total_todos']}\nCompleted: {stats['completed_todos']}\nPending: {stats['pending_todos']}\nCompletion Rate: {stats['completion_percentage']}%"

@mcp.tool()
async def create_todo(title: str, description: str = None, completed: bool = False) -> str:
    """Create a new todo item"""
    todo_data = {
        "title": title,
        "description": description,
        "completed": completed
    }
    result = await make_request("POST", "/todos", todo_data)
    return f"Created todo: {result['title']} (ID: {result['id']})"

@mcp.tool()
async def update_todo(todo_id: int, title: str = None, description: str = None, completed: bool = None) -> str:
    """Update an existing todo"""
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if completed is not None:
        update_data["completed"] = completed
    
    result = await make_request("PUT", f"/todos/{todo_id}", update_data)
    return f"Updated todo: {result['title']} (ID: {result['id']})"

@mcp.tool()
async def delete_todo(todo_id: int) -> str:
    """Delete a todo by ID"""
    result = await make_request("DELETE", f"/todos/{todo_id}")
    return result["message"]

@mcp.tool()
async def get_todo_by_id(todo_id: int) -> str:
    """Get a specific todo by ID"""
    todo = await make_request("GET", f"/todos/{todo_id}")
    return f"Todo Details:\nID: {todo['id']}\nTitle: {todo['title']}\nDescription: {todo.get('description', 'No description')}\nStatus: {'✅ Completed' if todo['completed'] else '⏳ Pending'}\nCreated: {todo['created_at']}\nUpdated: {todo['updated_at']}"

if __name__ == "__main__":
    print("🔌 Starting Todo MCP Server with FastMCP...")
    print("📡 Connecting to FastAPI at: http://localhost:8001")
    print("🤖 Ready for Gemini CLI integration")
    print("="*50)
    
    # Run the MCP server
    mcp.run()