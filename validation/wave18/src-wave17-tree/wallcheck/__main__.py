"""Dispatcher: `python -m wallcheck mcp` runs the MCP server;
anything else goes to the CLI (e.g. `python -m wallcheck probe <url>`)."""

import sys

from .cli import main as cli_main
from .server import main as server_main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        server_main()
    else:
        sys.exit(cli_main())
