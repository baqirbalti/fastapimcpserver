from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import asyncio
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

app = FastAPI(title="Todo List API", version="1.0.0")

# Pydantic models
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime

# In-memory storage (replace with database in production)
todos_db = []
next_id = 1

# Dummy data
dummy_todos = [
    {"title": "Learn FastAPI", "description": "Complete FastAPI tutorial", "completed": False},
    {"title": "Build MCP Server", "description": "Create MCP server for Gemini CLI", "completed": False},
    {"title": "Test Integration", "description": "Test FastAPI with MCP server", "completed": False},
    {"title": "Deploy Application", "description": "Deploy to production", "completed": True},
    {"title": "Write Documentation", "description": "Create API documentation", "completed": False}
]

# Initialize with dummy data
for todo_data in dummy_todos:
    todo = Todo(
        id=next_id,
        title=todo_data["title"],
        description=todo_data["description"],
        completed=todo_data["completed"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    todos_db.append(todo)
    next_id += 1

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Todo List API",
        "version": "1.0.0",
        "endpoints": {
            "GET /todos": "Get all todos",
            "GET /todos/{id}": "Get todo by ID",
            "POST /todos": "Create new todo",
            "PUT /todos/{id}": "Update todo",
            "DELETE /todos/{id}": "Delete todo",
            "GET /todos/stats": "Get todo statistics"
        }
    }

@app.get("/todos", response_model=List[Todo])
async def get_todos():
    """Get all todos"""
    return todos_db

@app.get("/todos/stats")
async def get_todo_stats():
    """Get todo statistics"""
    total_todos = len(todos_db)
    completed_todos = sum(1 for todo in todos_db if todo.completed)
    pending_todos = total_todos - completed_todos
    
    return {
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "pending_todos": pending_todos,
        "completion_percentage": round((completed_todos / total_todos * 100), 2) if total_todos > 0 else 0
    }

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    for todo in todos_db:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos", response_model=Todo)
async def create_todo(todo: TodoCreate):
    """Create a new todo"""
    global next_id
    new_todo = Todo(
        id=next_id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    todos_db.append(new_todo)
    next_id += 1
    return new_todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update an existing todo"""
    for i, todo in enumerate(todos_db):
        if todo.id == todo_id:
            update_data = todo_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(todo, field, value)
            todo.updated_at = datetime.now()
            todos_db[i] = todo
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo"""
    for i, todo in enumerate(todos_db):
        if todo.id == todo_id:
            deleted_todo = todos_db.pop(i)
            return {"message": f"Todo '{deleted_todo.title}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")

# MCP Server Class
class TodoMCPServer:
    def __init__(self):
        self.server = Server("todo-mcp-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools for todo management"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_todos",
                        description="Get all todos from the FastAPI application",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="get_todo_stats",
                        description="Get statistics about todos (total, completed, pending)",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="create_todo",
                        description="Create a new todo item",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Title of the todo"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Description of the todo (optional)"
                                },
                                "completed": {
                                    "type": "boolean",
                                    "description": "Whether the todo is completed (default: false)"
                                }
                            },
                            "required": ["title"]
                        }
                    ),
                    Tool(
                        name="update_todo",
                        description="Update an existing todo",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "ID of the todo to update"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "New title (optional)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New description (optional)"
                                },
                                "completed": {
                                    "type": "boolean",
                                    "description": "New completion status (optional)"
                                }
                            },
                            "required": ["id"]
                        }
                    ),
                    Tool(
                        name="delete_todo",
                        description="Delete a todo by ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "ID of the todo to delete"
                                }
                            },
                            "required": ["id"]
                        }
                    ),
                    Tool(
                        name="get_todo_by_id",
                        description="Get a specific todo by ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "ID of the todo to retrieve"
                                }
                            },
                            "required": ["id"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "get_todos":
                    return await self._get_todos()
                elif name == "get_todo_stats":
                    return await self._get_todo_stats()
                elif name == "create_todo":
                    return await self._create_todo(arguments)
                elif name == "update_todo":
                    return await self._update_todo(arguments)
                elif name == "delete_todo":
                    return await self._delete_todo(arguments)
                elif name == "get_todo_by_id":
                    return await self._get_todo_by_id(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to FastAPI server"""
        url = f"http://localhost:8001{endpoint}"
        
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
    
    async def _get_todos(self) -> CallToolResult:
        """Get all todos"""
        todos = await self._make_request("GET", "/todos")
        todos_text = "\n".join([
            f"ID: {todo['id']} | {todo['title']} | {'✅' if todo['completed'] else '⏳'} | {todo.get('description', 'No description')}"
            for todo in todos
        ])
        
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=f"All Todos:\n{todos_text}"
            )]
        )
    
    async def _get_todo_stats(self) -> CallToolResult:
        """Get todo statistics"""
        stats = await self._make_request("GET", "/todos/stats")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Todo Statistics:\n"
                     f"Total Todos: {stats['total_todos']}\n"
                     f"Completed: {stats['completed_todos']}\n"
                     f"Pending: {stats['pending_todos']}\n"
                     f"Completion Rate: {stats['completion_percentage']}%"
            )]
        )
    
    async def _create_todo(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Create a new todo"""
        todo_data = {
            "title": arguments["title"],
            "description": arguments.get("description"),
            "completed": arguments.get("completed", False)
        }
        
        result = await self._make_request("POST", "/todos", todo_data)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Created todo: {result['title']} (ID: {result['id']})"
            )]
        )
    
    async def _update_todo(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Update an existing todo"""
        todo_id = arguments["id"]
        update_data = {k: v for k, v in arguments.items() if k != "id" and v is not None}
        
        result = await self._make_request("PUT", f"/todos/{todo_id}", update_data)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Updated todo: {result['title']} (ID: {result['id']})"
            )]
        )
    
    async def _delete_todo(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Delete a todo"""
        todo_id = arguments["id"]
        result = await self._make_request("DELETE", f"/todos/{todo_id}")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=result["message"]
            )]
        )
    
    async def _get_todo_by_id(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get a specific todo by ID"""
        todo_id = arguments["id"]
        todo = await self._make_request("GET", f"/todos/{todo_id}")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Todo Details:\n"
                     f"ID: {todo['id']}\n"
                     f"Title: {todo['title']}\n"
                     f"Description: {todo.get('description', 'No description')}\n"
                     f"Status: {'✅ Completed' if todo['completed'] else '⏳ Pending'}\n"
                     f"Created: {todo['created_at']}\n"
                     f"Updated: {todo['updated_at']}"
            )]
        )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="todo-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def run_mcp_server():
    """Run MCP server"""
    server = TodoMCPServer()
    await server.run()

def start_fastapi():
    """Start FastAPI server"""
    print("Starting FastAPI Todo Application...")
    print("📝 API Documentation available at: http://localhost:8001/docs")
    print("🔗 API Base URL: http://localhost:8001")
    print("📊 Todo Stats endpoint: http://localhost:8001/todos/stats")
    print("\n" + "="*50)
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        print("🔌 Starting MCP Server for Todo Integration...")
        print("📡 Server will connect to FastAPI at: http://localhost:8001")
        print("🤖 Ready for Gemini CLI integration")
        print("\n" + "="*50)
        asyncio.run(run_mcp_server())
    else:
        start_fastapi()