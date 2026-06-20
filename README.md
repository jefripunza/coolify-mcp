# Coolify MCP Server

MCP (Model Context Protocol) server for managing Coolify PaaS.

## Features

- **Projects**: List, create, delete projects
- **Servers**: List, get, validate servers
- **Applications**: List, get applications
- **Databases**: List, get databases
- **Services**: List, get services
- **Deployments**: List deployments, trigger deploy
- **Resources**: List all resources
- **Teams**: List teams, get current team
- **Health**: Check health, get version

## Configuration

Create `~/.cloudflared/coolify.env`:

```
COOLIFY_URL=https://your-coolify-instance.com
COOLIFY_TOKEN=your_api_token
```

## Usage

```bash
# Run directly
python server.py

# Or via uvx
uvx coolify-mcp
```

## Install in Hermes

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  coolify:
    command: python3
    args: [/home/p34c3-khyrein/workspace/coolify-mcp/server.py]
    env:
      COOLIFY_URL: https://coolify.jefripunza.com
```
