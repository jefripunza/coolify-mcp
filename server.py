#!/usr/bin/env python3
"""Coolify MCP Server - Manage Coolify via Model Context Protocol."""
import os
import json
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Load config from file or environment
CONFIG_FILE = Path.home() / ".cloudflared" / "coolify.env"

def load_config():
    """Load config from env file."""
    config = {}
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    return config

config = load_config()
COOLIFY_URL = config.get("COOLIFY_URL") or os.environ.get("COOLIFY_URL", "https://coolify.jefripunza.com")
COOLIFY_TOKEN = config.get("COOLIFY_TOKEN") or os.environ.get("COOLIFY_TOKEN", "")

mcp = FastMCP("coolify")


def coolify_api(method, path, data=None):
    """Make API request to Coolify using curl (bypasses Cloudflare)."""
    url = f"{COOLIFY_URL}/api/v1{path}"
    cmd = [
        "curl", "-s", "-X", method,
        "-H", f"Authorization: Bearer {COOLIFY_TOKEN}",
        "-H", "Content-Type: application/json",
    ]
    if data:
        cmd.extend(["-d", json.dumps(data)])
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return {"error": result.stderr}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": result.stdout[:500]}


# ==================== PROJECTS ====================

@mcp.tool()
def list_projects():
    """List all Coolify projects."""
    result = coolify_api("GET", "/projects")
    if isinstance(result, list):
        projects = []
        for p in result:
            projects.append({
                "uuid": p.get("uuid"),
                "name": p.get("name"),
                "description": p.get("description") or "-"
            })
        return json.dumps(projects, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_project(uuid: str):
    """Get project details by UUID."""
    result = coolify_api("GET", f"/projects/{uuid}")
    return json.dumps(result, indent=2)


@mcp.tool()
def create_project(name: str, description: str = ""):
    """Create a new Coolify project."""
    result = coolify_api("POST", "/projects", {"name": name, "description": description})
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_project(uuid: str):
    """Delete a Coolify project by UUID."""
    result = coolify_api("DELETE", f"/projects/{uuid}")
    return json.dumps(result, indent=2)


# ==================== SERVERS ====================

@mcp.tool()
def list_servers():
    """List all Coolify servers."""
    result = coolify_api("GET", "/servers")
    if isinstance(result, list):
        servers = []
        for s in result:
            servers.append({
                "uuid": s.get("uuid"),
                "name": s.get("name"),
                "ip": s.get("ip"),
                "status": s.get("status"),
                "proxy_type": s.get("proxy_type")
            })
        return json.dumps(servers, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_server(uuid: str):
    """Get server details by UUID."""
    result = coolify_api("GET", f"/servers/{uuid}")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_server_resources(uuid: str):
    """Get all resources on a server."""
    result = coolify_api("GET", f"/servers/{uuid}/resources")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_server_domains(uuid: str):
    """Get all domains configured on a server."""
    result = coolify_api("GET", f"/servers/{uuid}/domains")
    return json.dumps(result, indent=2)


# ==================== APPLICATIONS ====================

@mcp.tool()
def list_applications(tag: str = None):
    """List all applications. Optionally filter by tag."""
    path = "/applications"
    if tag:
        path += f"?tag={tag}"
    result = coolify_api("GET", path)
    if isinstance(result, list):
        apps = []
        for a in result:
            apps.append({
                "uuid": a.get("uuid"),
                "name": a.get("name"),
                "git_repository": a.get("git_repository"),
                "status": a.get("status"),
                "domains": a.get("domains"),
                "fqdn": a.get("fqdn")
            })
        return json.dumps(apps, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_application(uuid: str):
    """Get application details by UUID."""
    result = coolify_api("GET", f"/applications/{uuid}")
    return json.dumps(result, indent=2)


# ==================== DATABASES ====================

@mcp.tool()
def list_databases():
    """List all databases."""
    result = coolify_api("GET", "/databases")
    if isinstance(result, list):
        dbs = []
        for d in result:
            dbs.append({
                "uuid": d.get("uuid"),
                "name": d.get("name"),
                "type": d.get("database_type") or d.get("type"),
                "status": d.get("status")
            })
        return json.dumps(dbs, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_database(uuid: str):
    """Get database details by UUID."""
    result = coolify_api("GET", f"/databases/{uuid}")
    return json.dumps(result, indent=2)


# ==================== SERVICES ====================

@mcp.tool()
def list_services():
    """List all services."""
    result = coolify_api("GET", "/services")
    if isinstance(result, list):
        services = []
        for s in result:
            services.append({
                "uuid": s.get("uuid"),
                "name": s.get("name"),
                "type": s.get("type"),
                "status": s.get("status")
            })
        return json.dumps(services, indent=2)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_service(uuid: str):
    """Get service details by UUID."""
    result = coolify_api("GET", f"/services/{uuid}")
    return json.dumps(result, indent=2)


# ==================== DEPLOYMENTS ====================

@mcp.tool()
def list_deployments(application_uuid: str = None, limit: int = 10):
    """List deployments. Optionally filter by application UUID."""
    path = "/deployments"
    params = []
    if application_uuid:
        params.append(f"application_uuid={application_uuid}")
    if limit:
        params.append(f"limit={limit}")
    if params:
        path += "?" + "&".join(params)
    result = coolify_api("GET", path)
    return json.dumps(result, indent=2)


@mcp.tool()
def deploy_application(uuid: str):
    """Trigger deployment for an application."""
    result = coolify_api("POST", "/deploy", {"application_uuid": uuid})
    return json.dumps(result, indent=2)


# ==================== RESOURCES ====================

@mcp.tool()
def list_resources():
    """List all resources across all servers."""
    result = coolify_api("GET", "/resources")
    if isinstance(result, list):
        resources = []
        for r in result:
            resources.append({
                "uuid": r.get("uuid"),
                "name": r.get("name"),
                "type": r.get("type"),
                "status": r.get("status"),
                "server_name": r.get("server", {}).get("name") if r.get("server") else None
            })
        return json.dumps(resources, indent=2)
    return json.dumps(result, indent=2)


# ==================== TEAMS ====================

@mcp.tool()
def list_teams():
    """List all teams."""
    result = coolify_api("GET", "/teams")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_current_team():
    """Get current team info."""
    result = coolify_api("GET", "/teams/current")
    return json.dumps(result, indent=2)


# ==================== HEALTH ====================

@mcp.tool()
def coolify_health():
    """Check Coolify instance health."""
    result = coolify_api("GET", "/health")
    return json.dumps(result, indent=2)


@mcp.tool()
def coolify_version():
    """Get Coolify version."""
    result = coolify_api("GET", "/version")
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    if not COOLIFY_TOKEN:
        print("ERROR: COOLIFY_TOKEN not set in ~/.cloudflared/coolify.env or environment")
        exit(1)
    print(f"Coolify MCP Server starting...")
    print(f"URL: {COOLIFY_URL}")
    mcp.run()
