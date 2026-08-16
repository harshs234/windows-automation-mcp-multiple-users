# Windows Endpoint Automation API (MCP endpoint copy)

This is the endpoint-side FastAPI application used by the Windows Automation MCP multi-user POC.

Run natively on Windows. It executes only the allowlisted PowerShell automation routes.

Endpoints:
- GET /health
- GET /disk/status (X-API-KEY required)
- POST /disk/cleanup (X-API-KEY required)
- POST /browser/bookmarks (X-API-KEY required)

Configure `API_KEY` in `.env` per physical laptop.
