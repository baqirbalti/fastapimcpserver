#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate MCP server functionality
This directly calls the FastAPI endpoints that the MCP server wraps
"""

import httpx
import asyncio
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

FASTAPI_URL = "http://localhost:8001"

async def test_mcp_endpoints():
    """Test all the endpoints that the MCP server exposes"""
    
    print("Testing Todo MCP Server Endpoints\n")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Get all todos
            print("\n[1] GET ALL TODOS")
            print("-" * 60)
            response = await client.get(f"{FASTAPI_URL}/todos")
            todos = response.json()
            for todo in todos:
                status = "[DONE]" if todo['completed'] else "[TODO]"
                print(f"  ID: {todo['id']} | {status} {todo['title']}")
                if todo.get('description'):
                    print(f"     -> {todo['description']}")
            
            # Test 2: Get statistics
            print("\n[2] GET TODO STATISTICS")
            print("-" * 60)
            response = await client.get(f"{FASTAPI_URL}/todos/stats")
            stats = response.json()
            print(f"  Total Todos: {stats['total_todos']}")
            print(f"  Completed: {stats['completed_todos']}")
            print(f"  Pending: {stats['pending_todos']}")
            print(f"  Completion Rate: {stats['completion_percentage']}%")
            
            # Test 3: Create a new todo
            print("\n[3] CREATE NEW TODO")
            print("-" * 60)
            new_todo = {
                "title": "Test MCP Integration",
                "description": "Testing the MCP server functionality",
                "completed": False
            }
            response = await client.post(f"{FASTAPI_URL}/todos", json=new_todo)
            created = response.json()
            print(f"  Created: {created['title']} (ID: {created['id']})")
            
            # Test 4: Get specific todo
            print("\n[4] GET TODO BY ID")
            print("-" * 60)
            todo_id = created['id']
            response = await client.get(f"{FASTAPI_URL}/todos/{todo_id}")
            todo = response.json()
            print(f"  ID: {todo['id']}")
            print(f"  Title: {todo['title']}")
            print(f"  Description: {todo.get('description', 'N/A')}")
            print(f"  Status: {'Completed' if todo['completed'] else 'Pending'}")
            
            # Test 5: Update the todo
            print("\n[5] UPDATE TODO")
            print("-" * 60)
            update_data = {"completed": True}
            response = await client.put(f"{FASTAPI_URL}/todos/{todo_id}", json=update_data)
            updated = response.json()
            print(f"  Updated: {updated['title']} -> Completed")
            
            # Test 6: Delete the todo
            print("\n[6] DELETE TODO")
            print("-" * 60)
            response = await client.delete(f"{FASTAPI_URL}/todos/{todo_id}")
            result = response.json()
            print(f"  {result['message']}")
            
            print("\n" + "=" * 60)
            print("SUCCESS: All MCP endpoint tests completed!")
            print("\nTIP: These same operations are available through the MCP")
            print("     server tools when using this with Cursor or other MCP clients.")
            
        except httpx.ConnectError:
            print("ERROR: Cannot connect to FastAPI server.")
            print("       Make sure the server is running: python main.py")
        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mcp_endpoints())

