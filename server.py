import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Windows Automation")

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
USERS_FILE = CONFIG_DIR / "users.json"
ENDPOINTS_FILE = CONFIG_DIR / "endpoints.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_users() -> list[dict]:
    return load_json(USERS_FILE).get("users", [])


def load_endpoints() -> dict[str, dict]:
    return {
        item["endpoint_id"]: item
        for item in load_json(ENDPOINTS_FILE).get("endpoints", [])
    }


def resolve_endpoint(user_id: str) -> dict:
    for user in load_users():
        if user["user_id"].lower() == user_id.lower() and user.get("enabled", False):
            return user
    raise ValueError(f"Enabled user '{user_id}' not found.")


def endpoint_config(user: dict) -> dict:
    endpoint_id = user["endpoint_id"]
    config = load_endpoints().get(endpoint_id)
    if not config:
        raise ValueError(f"Endpoint '{endpoint_id}' is not configured.")

    url = config.get("url")
    if not url or "REPLACE_WITH" in url:
        raise ValueError(f"Endpoint '{endpoint_id}' is not connected.")

    api_key_env = config.get("api_key_env")

    print("DEBUG endpoint:", endpoint_id)
    print("DEBUG api_key_env:", repr(api_key_env))
    print(
        "DEBUG env_exists:",
        bool(os.getenv(api_key_env)) if api_key_env else False
    )

    api_key = os.getenv(api_key_env) if api_key_env else None

    return {
        "url": url.rstrip("/"),
        "api_key": api_key,
    }


def call_endpoint(
    user: dict,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    config = endpoint_config(user)

    try:
        response = requests.request(
            method=method,
            url=f"{config['url']}{path}",
            headers={"X-API-KEY": config["api_key"]},
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if getattr(exc, "response", None) is not None:
            detail = f" | {exc.response.text}"
        raise RuntimeError(
            f"Endpoint '{user['endpoint_id']}' request failed: "
            f"{exc}{detail}"
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Endpoint '{user['endpoint_id']}' returned invalid JSON."
        ) from exc


def user_context(user: dict) -> dict:
    return {
        "user_id": user["user_id"],
        "endpoint_id": user["endpoint_id"],
        "computer_name": user["computer_name"],
    }


@mcp.tool
def list_test_users() -> list[dict]:
    """List enabled test users and their assigned endpoints."""
    return [
        {
            "user_id": user["user_id"],
            "endpoint_id": user["endpoint_id"],
            "computer_name": user["computer_name"],
            "enabled": True,
        }
        for user in load_users()
        if user.get("enabled", False)
    ]


@mcp.tool
def resolve_user_endpoint(user_id: str) -> dict:
    """Resolve a user to their assigned endpoint."""
    return {
        **user_context(resolve_endpoint(user_id)),
        "status": "resolved",
    }


@mcp.tool
def get_test_user(user_id: str) -> dict:
    """Get the endpoint assigned to a specific user."""
    return {
        **user_context(resolve_endpoint(user_id)),
        "enabled": True,
    }


@mcp.tool
def get_disk_status(user_id: str) -> dict:
    """Get disk usage for the Windows endpoint assigned to a user."""
    user = resolve_endpoint(user_id)
    result = call_endpoint(user, "GET", "/disk/status")
    return {"user": user_context(user), "endpoint_result": result}


@mcp.tool
def preview_cleanup(user_id: str) -> dict:
    """Preview Windows cleanup without deleting files."""
    user = resolve_endpoint(user_id)
    result = call_endpoint(
        user,
        "POST",
        "/disk/cleanup",
        {"cleanup_level": "safe", "dry_run": True},
    )
    return {"user": user_context(user), "endpoint_result": result}


@mcp.tool
def execute_cleanup(user_id: str, confirm: bool = False) -> dict:
    """Execute Windows cleanup. Requires confirm=true."""
    user = resolve_endpoint(user_id)

    if not confirm:
        return {
            "status": "confirmation_required",
            "message": "Cleanup was not executed. Set confirm=true to proceed.",
            "user": user_context(user),
        }

    result = call_endpoint(
        user,
        "POST",
        "/disk/cleanup",
        {"cleanup_level": "safe", "dry_run": False},
    )
    return {"user": user_context(user), "endpoint_result": result}


@mcp.tool
def add_browser_bookmarks(
    user_id: str,
    browser: str = "Both",
    close_browser: bool = True,
) -> dict:
    """Add configured bookmarks to Chrome, Edge, or both browsers.
    Existing bookmark URLs are skipped by the PowerShell script.
    """
    if browser not in {"Chrome", "Edge", "Both"}:
        raise ValueError("browser must be Chrome, Edge, or Both.")

    user = resolve_endpoint(user_id)
    result = call_endpoint(
        user,
        "POST",
        "/browser/bookmarks",
        {
            "browser": browser,
            "close_browser": close_browser,
            "dry_run": False,
        },
    )
    return {"user": user_context(user), "endpoint_result": result}


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
