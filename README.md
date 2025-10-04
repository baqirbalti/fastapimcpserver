# Todo List MCP Server

A Model Context Protocol (MCP) server implementation for a Todo List application, integrating FastAPI backend with MCP tools for seamless AI assistant integration.

## 📺 Demo Video

Watch the demo video here: [Todo MCP Server Demo](https://drive.google.com/file/d/1Yb7pFDumEAROewnsaa6BqQ8nDBlNlObc/view?usp=drive_link)

## 🚀 Features

- **FastAPI Backend**: RESTful API for todo management with automatic API documentation
- **MCP Server Integration**: Two implementations (FastMCP and native MCP) for AI assistant tools
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality for todos
- **Statistics**: Real-time todo statistics (total, completed, pending, completion rate)
- **In-Memory Storage**: Quick setup with pre-loaded dummy data
- **Cursor IDE Integration**: Configured MCP server ready to use in Cursor

## 📋 Available MCP Tools

The MCP server exposes the following tools:

1. **get_todos** - Retrieve all todos with their status
2. **get_todo_stats** - Get statistics (total, completed, pending, completion percentage)
3. **create_todo** - Create a new todo item
4. **update_todo** - Update an existing todo (title, description, or status)
5. **delete_todo** - Delete a todo by ID
6. **get_todo_by_id** - Get detailed information about a specific todo

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone or download this repository:
```bash
cd D:\Projects_Model\mcp_03
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.3
python-dotenv==1.0.0
httpx==0.26.0
fastmcp==0.1.0
```

## 🚦 Usage

### 1. Start the FastAPI Backend

```bash
python main.py
```

This starts the FastAPI server on `http://localhost:8001` with:
- API Documentation: http://localhost:8001/docs
- Interactive API: http://localhost:8001/redoc
- Todo Stats: http://localhost:8001/todos/stats

### 2. Start the MCP Server (for Gemini CLI or other MCP clients)

```bash
python main.py mcp
```

Or use the FastMCP version:

```bash
python mcpserver.py
```

### 3. Use with Cursor IDE

The MCP server is already configured in Cursor's `mcp.json`:

```json
{
  "mcpServers": {
    "todo-mcp-server": {
      "command": "python",
      "args": ["..\\mcpserver.py"],
      "cwd": "D:\\Projects_Model\\mcp_03"
    }
  }
}
```

Simply restart Cursor, and the MCP tools will be available in your AI assistant conversations!

### 4. Run Tests

Test all MCP endpoints:

```bash
python test_mcp.py
```

## 📚 API Endpoints

### Todo Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/todos` | Get all todos |
| GET | `/todos/{id}` | Get a specific todo |
| POST | `/todos` | Create a new todo |
| PUT | `/todos/{id}` | Update a todo |
| DELETE | `/todos/{id}` | Delete a todo |
| GET | `/todos/stats` | Get todo statistics |

### Example Requests

**Create a Todo:**
```bash
curl -X POST http://localhost:8001/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn MCP", "description": "Study Model Context Protocol", "completed": false}'
```

**Get All Todos:**
```bash
curl http://localhost:8001/todos
```

**Get Statistics:**
```bash
curl http://localhost:8001/todos/stats
```

## 🏗️ Project Structure

```
mcp_03/
├── main.py              # FastAPI app + Native MCP server
├── mcpserver.py         # FastMCP implementation
├── test_mcp.py          # Test script for MCP endpoints
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 💡 How It Works

1. **FastAPI Backend** (`main.py`):
   - Runs on port 8001
   - Provides REST API for todo operations
   - Includes in-memory storage with dummy data
   - Auto-generates OpenAPI documentation

2. **MCP Server** (`mcpserver.py`):
   - Connects to FastAPI backend via HTTP
   - Exposes todo operations as MCP tools
   - Integrates with AI assistants (Cursor, Gemini CLI, etc.)
   - Provides natural language interface to todo operations

3. **Integration Flow**:
   ```
   AI Assistant (Cursor)
         ↓
   MCP Server (mcpserver.py)
         ↓
   FastAPI Backend (main.py)
         ↓
   In-Memory Database
   ```

## 🔧 Configuration

### Change Port

Edit `main.py` to change the FastAPI port:

```python
uvicorn.run(
    "main:app", 
    host="0.0.0.0", 
    port=8001,  # Change this
    reload=True,
    log_level="info"
)
```

Don't forget to update `mcpserver.py` and `test_mcp.py` accordingly:

```python
FASTAPI_URL = "http://localhost:8001"  # Update this
```

### MCP Configuration for Cursor

Edit `~/.cursor/mcp.json` (or `C:\Users\{username}\.cursor\mcp.json` on Windows):

```json
{
  "mcpServers": {
    "todo-mcp-server": {
      "command": "python",
      "args": ["path\\to\\mcpserver.py"],
      "cwd": "path\\to\\mcp_03"
    }
  }
}
```

## 📊 Sample Data

The application comes pre-loaded with 5 sample todos:

1. Learn FastAPI
2. Build MCP Server
3. Test Integration
4. Deploy Application (Completed)
5. Write Documentation

## 🤝 Using with AI Assistants

### In Cursor

Once configured, you can use natural language commands:

- "Show me all my todos"
- "Create a todo to finish the project report"
- "Mark todo #3 as completed"
- "What's my todo completion rate?"
- "Delete the completed todos"

### With Gemini CLI

```bash
# Start the MCP server
python main.py mcp

# Use Gemini CLI with MCP integration
gemini --mcp todo-mcp-server "What todos do I have?"
```

## 🐛 Troubleshooting

### Port Already in Use

If port 8001 is already in use:
1. Change the port in `main.py`
2. Update `FASTAPI_URL` in `mcpserver.py` and `test_mcp.py`

### MCP Server Connection Error

Ensure the FastAPI backend is running before starting the MCP server:
```bash
# Terminal 1
python main.py

# Terminal 2
python mcpserver.py
```

### Encoding Issues on Windows

The test script includes automatic UTF-8 encoding configuration for Windows. If you still see encoding errors, run:
```bash
chcp 65001
python test_mcp.py
```

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- MCP integration using [FastMCP](https://github.com/jlowin/fastmcp)
- Designed for [Cursor IDE](https://cursor.sh/) integration

## 📞 Support

For issues or questions, please refer to the demo video or check the FastAPI documentation at http://localhost:8001/docs when the server is running.

---

**Happy Todo Managing with AI! 🎉**

