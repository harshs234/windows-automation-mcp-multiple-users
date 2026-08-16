# Windows Automation MCP — Multi-Endpoint POC

This project is the MCP gateway plus a copy of the Windows Endpoint Automation API.
The original `windows-disk-cleanup-api` used by Zia is not modified by this project.

## Architecture

Claude/Zia -> MCP server -> user_id -> endpoint_id -> authenticated Windows API -> PowerShell

The MCP server does routing. Each Windows laptop runs its own copy of `endpoint-api`.

## MCP tools

- `get_disk_status(user_id)`
- `preview_cleanup(user_id)`
- `execute_cleanup(user_id, confirm=true)`
- `add_browser_bookmarks(user_id, browser, close_browser)`
- `list_test_users()`
- `resolve_user_endpoint(user_id)`
- `get_test_user(user_id)`

Bookmark dry-run is intentionally not exposed through MCP. The PowerShell script already skips duplicate URLs.

## Main MCP laptop

1. Create a venv and install `requirements.txt`.
2. Copy `.env.example` to `.env` and set the endpoint API keys.
3. Edit `config/endpoints.json` with the real endpoint URLs.
4. Run `python server.py` (MCP on port 8000).

For the current two-laptop POC:
- endpoint-002 is configured as `http://127.0.0.1:8501` (main laptop endpoint API).
- endpoint-003 must be changed to the second laptop's reachable URL, normally `http://<LAN-IP>:8500`.

## Endpoint laptop

Copy only the `endpoint-api` directory to the Windows endpoint.

Inside that copy:
1. Create `.venv`.
2. Install `requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Set a unique `API_KEY`.
5. Run:
   `uvicorn app.main:app --host 0.0.0.0 --port 8500`

The endpoint API must run natively on Windows because the PowerShell scripts use Windows components.

## Security

- MCP sends `X-API-KEY` to the assigned endpoint.
- Each endpoint should have a unique API key.
- Do not commit `.env`.
- Restrict endpoint port 8500 with Windows Firewall to the MCP host/network.
- For remote/internet access, use a secure tunnel/VPN and do not expose the endpoint without authentication.

## Updating scripts

For this POC, the `endpoint-api/scripts` directory is the deployed version of the automation code.
Do not create an ad-hoc script downloader. For production, use the organization's endpoint/software deployment mechanism to version and update the endpoint package.

## Testing

From the MCP machine:
`fastmcp call http://localhost:8000/mcp get_disk_status user_id=test_user_01`

Then test the same tools with `test_user_02` after endpoint-003 is configured.
