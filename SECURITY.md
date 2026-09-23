# Security Policy

## Supported version
The latest release on `main` is supported.

## Security model
MCP Directory Local stores configuration metadata only. It never starts MCP servers, executes stored commands, connects to stored URLs, or resolves credentials. Registry files may reveal command names, arguments, URLs, and local topology; protect them accordingly. Do not store API keys, tokens, passwords, or authorization headers in registry entries.

## Reporting
Please report security concerns privately through GitHub's security reporting facilities when available. Do not publish credentials or sensitive local configuration in an issue.
