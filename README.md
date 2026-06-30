# bus-api

Israel public transport API — stops, routes and real-time (SIRI) arrivals.

## MCP interface

The same operations are exposed over the [Model Context Protocol](https://modelcontextprotocol.io)
via a streamable-HTTP server mounted on the FastAPI app at **`/mcp`** (so the full
URL is `<root_path>/mcp`). It shares the app's database connection and lifespan, so
nothing extra needs to be started — running the API serves the MCP endpoint too.

### Tools

| Tool | Description |
| --- | --- |
| `find_stop_by_code` | Find a stop by its public stop code (e.g. 5200). |
| `find_stop_by_id` | Find a stop by its internal GTFS stop id (e.g. 10846). |
| `search_stops_by_name` | Search stops by (partial) name — natural-language entry point. |
| `find_stops_by_parent_id` | List child stops / platforms of a parent station id. |
| `find_nearest_stops` | Find stops within a radius (meters) of a lat/lng point. |
| `find_route_by_id` | Get a route by its GTFS route id. |
| `search_routes` | Search lines by number (short name) or origin/destination city. |
| `get_available_routes_for_stop` | List routes that serve a stop code. |
| `get_arrivals_for_stop` | Real-time incoming routes/ETAs for a stop code. |
| `get_arrivals_for_stop_by_id` | Real-time incoming routes/ETAs for a GTFS stop id. |
| `get_vehicle_location` | Current GPS location of a specific inbound vehicle. |

### Connecting a client

This is a **streamable-HTTP** server, so point clients at the `/mcp` URL —
`https://api.ginzburg.io/il_transport/mcp` for the hosted instance (or `http://localhost:8000/mcp`
when running locally). Below are configs for the most popular MCP clients.

#### Claude Code

```sh
claude mcp add --transport http israel-transport https://api.ginzburg.io/il_transport/mcp
```

#### Claude Desktop

Easiest via the UI: **Settings → Connectors → Add custom connector**, then enter a name
and the `/mcp` URL.

For older versions whose `claude_desktop_config.json` only speaks stdio, bridge with
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote) (requires Node.js):

```json
{
  "mcpServers": {
    "israel-transport": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.ginzburg.io/il_transport/mcp"]
    }
  }
}
```

#### ChatGPT Desktop

ChatGPT connects to remote MCP servers as **custom connectors** (available on paid
plans). Enable **Settings → Connectors → Advanced → Developer mode**, then **Add custom
connector** and paste the server URL `https://api.ginzburg.io/il_transport/mcp`. ChatGPT cannot
run local stdio servers and requires a public **HTTPS** endpoint (note the `https://` — a
plain-`http` URL or `localhost` will not be accepted).

#### Codex

In `~/.codex/config.toml` (HTTP transport requires the rmcp client feature):

```toml
[features]
experimental_use_rmcp_client = true

[mcp_servers.israel-transport]
url = "https://api.ginzburg.io/il_transport/mcp"
```

#### VS Code (GitHub Copilot agent mode)

In `.vscode/mcp.json`:

```json
{
  "servers": {
    "israel-transport": {
      "type": "http",
      "url": "https://api.ginzburg.io/il_transport/mcp"
    }
  }
}
```

#### Any other streamable-HTTP client

```json
{
  "mcpServers": {
    "israel-transport": {
      "type": "http",
      "url": "https://api.ginzburg.io/il_transport/mcp"
    }
  }
}
```

### Security

DNS-rebinding protection (Host-header validation) is **off by default**, which suits
running behind a reverse proxy. To enable it, set `MCP_ALLOWED_HOSTS` (and optionally
`MCP_ALLOWED_ORIGINS`) as JSON arrays — `"host:*"` port wildcards are supported:

```
MCP_ALLOWED_HOSTS='["api.ginzburg.io", "localhost:*"]'
```
