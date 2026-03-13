# Copilot Instructions for FusionMCP

## Project Overview

FusionMCP is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that lets AI assistants (Claude, Copilot, etc.) control Autodesk Fusion 360 via natural language. It has two components:

1. **MCP Server** (`mcp_server/fusion_server.py`) — A Python process that runs locally and exposes CAD tools to the AI over stdio using the `mcp` SDK.
2. **Fusion 360 Add-in** (`FusionMCP.py` + `FusionMCP.manifest`) — A Python add-in that runs inside Fusion 360, hosts an HTTP server on `http://127.0.0.1:7432`, receives commands from the MCP server, and executes them on Fusion's main thread using the Fusion 360 Python API.

```
AI Assistant  ──stdio──▶  MCP Server (Python)  ──HTTP──▶  Fusion 360 Add-in
                           fusion_server.py                 FusionMCP.py
                           (your machine)                   (inside Fusion 360)
```

## Repository Structure

```
fusion-mcp/
├── FusionMCP.py            # Fusion 360 add-in (runs inside Fusion 360)
├── FusionMCP.manifest      # Fusion 360 add-in manifest (required by Fusion)
├── mcp_server/
│   ├── fusion_server.py    # MCP server exposing tools to the AI assistant
│   ├── requirements.txt    # Python dependencies (mcp, requests)
│   └── keyboard/           # Keyboard-related utilities
└── README.md
```

## Architecture & Key Concepts

- **All dimensions use centimeters** (Fusion 360's internal unit). Angles use degrees in tool parameters (converted to radians internally).
- **Commands flow one-way**: AI → MCP server (via stdio) → Fusion add-in (via HTTP POST to `/command`) → Fusion 360 API.
- **Add-in thread model**: The Fusion 360 add-in runs commands on the main thread via a custom event handler to comply with Fusion's threading model.
- **MCP tools** in `fusion_server.py` are decorated with `@mcp.tool()` using [FastMCP](https://github.com/jlowin/fastmcp). Each tool calls `_call(command, params)` which POSTs to the Fusion add-in.
- **Add-in command handler** in `FusionMCP.py` dispatches incoming `command` strings to handler functions that use the `adsk.fusion` and `adsk.core` APIs.

## Coding Conventions

### MCP Server (`fusion_server.py`)
- Every public tool is a top-level function decorated with `@mcp.tool()`.
- Each tool has a clear docstring describing its purpose and all parameters.
- Tools call `_call(command_name, params_dict)` — never call the Fusion HTTP endpoint directly.
- Return values are always strings (JSON-formatted on success, plain error messages on failure).
- Parameter names in tool signatures must match the keys expected by the Fusion add-in handler.

### Fusion 360 Add-in (`FusionMCP.py`)
- Uses `adsk.fusion`, `adsk.core`, and `adsk.cam` Fusion 360 Python API namespaces.
- Handler functions are named `handle_<command_name>` and receive a `params` dict.
- All geometry values (lengths, radii, etc.) are in centimeters.
- Angles passed to API calls use radians (convert with `math.radians(degrees)`).
- The HTTP server is a simple `http.server.BaseHTTPRequestHandler` subclass; keep it single-threaded.

### General
- Python 3.10+ syntax is acceptable.
- No type annotations are required but are welcome for clarity.
- Keep functions focused and single-purpose.
- Error messages returned to the AI should be human-readable and actionable.

## Development Setup

```bash
# Install MCP server dependencies
pip install -r mcp_server/requirements.txt
```

To test the MCP server without Fusion 360, you can run `fusion_server.py` directly and send MCP messages over stdio, or use the MCP Inspector.

The Fusion 360 add-in (`FusionMCP.py`) must be installed in Fusion 360's add-ins directory and run from within Fusion 360. See `README.md` for the exact paths.

## Adding a New Tool

1. **Add a handler in `FusionMCP.py`**: Create a `handle_<your_command>(params)` function that uses the Fusion 360 API, then register it in the command dispatch dictionary.
2. **Expose it in `fusion_server.py`**: Add a `@mcp.tool()` decorated function with a clear docstring, and call `_call("<your_command>", {...})`.
3. Update `README.md` to document the new capability under the appropriate feature section.

## Testing

There is no automated test suite — manual testing against a live Fusion 360 instance is the primary verification method. When making changes:
- Test the MCP server in isolation by verifying it starts without errors: `python mcp_server/fusion_server.py`.
- Test add-in changes by reloading the add-in inside Fusion 360 (Utilities > Add-Ins > Reload).
- Use `get_design_info`, `get_face_info`, and `get_edge_info` tools to verify state before and after operations.
