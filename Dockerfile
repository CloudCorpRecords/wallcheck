# wallcheck as a container image (GHCR).
# Python standard library only — no pip installs at build or run time.
# Default command runs the stdio MCP server; pass `probe <url>` for the CLI.
FROM python:3.12-alpine
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
ENV PYTHONPATH=/app/src
USER nobody
ENTRYPOINT ["python3", "-m", "wallcheck"]
CMD ["mcp"]
LABEL org.opencontainers.image.source="https://github.com/CloudCorpRecords/wallcheck" \
      org.opencontainers.image.description="wallcheck: deterministic bot-wall transparency. Probe a URL, name the wall (Cloudflare, PerimeterX, DataDome, Akamai, Imperva, AWS WAF, Azure WAF, Kasada, CloudFront), get the evidence. CLI + stdio MCP server, Python stdlib only." \
      org.opencontainers.image.licenses="MIT" \
      io.modelcontextprotocol.server.name="io.github.CloudCorpRecords/wallcheck"
