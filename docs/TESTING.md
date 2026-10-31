# Test before submission

Static checks and authenticated app testing answer different questions. Do not attest to in-app testing based on manifest validation.

## Package checks

Run from the repository root with Python 3.9+ and Claude Code 2.1.311+:

```bash
python3 scripts/plugin.py check
claude plugin validate .claude-plugin/plugin.json --strict --profile directory
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate skills --strict
python3 scripts/plugin.py build
```

Extract the versioned ZIP into a fresh directory and run the Claude plugin validator against that directory. Confirm `.claude-plugin/plugin.json` is directly at the archive root. The ZIP omits marketplace indexes because it is one installable plugin. The source repository's marketplace indexes each contain one root-relative entry pointing to that plugin.

The package checker validates generated Cursor metadata and paths. Claude's CLI is not a native Cursor runtime test.

## Host checks

Use a test user and dealership you are authorized to access. Keep reviewer credentials, customer records, and tokens out of this repository and CI.

| Host | Load | Verify |
| --- | --- | --- |
| Claude chat | Upload the ZIP through Customize > Plugins > Add | Three skills appear; Dealr appears on the Connectors tab and completes OAuth. |
| Cowork | Install the same uploaded plugin | Skills and authenticated tools are available in a new task. |
| Claude Code | Start `claude --plugin-dir /absolute/path/to/repo` | Three namespaced skills appear; `/mcp` lists Dealr and completes OAuth. |
| Cursor | Copy into the local plugin directory described in the README, then reload | Customize shows three skills and one Dealr MCP server; OAuth succeeds. |
| Claude organization | Import the repository marketplace | Install `dealr-cloud`; verify each member connects with their own Dealr identity. |
| Cursor team | Import into Team Marketplaces | Install from Customize; verify member OAuth and permissions. |
| Grok Bot | Install the shared marketplace listing when available, or add the remote URL | Verify skill discovery separately from OAuth and tools. This remains unverified until exercised. |

## Authorized data checks

1. Call `get_context`. Confirm permitted rooftops, available object types, timezone, and contact sharing.
2. Ask “Show vehicles in stock more than 90 days.” Check filters against `describe_object`, compare with the same user in Dealr, and verify pagination does not turn a partial page into a claimed total.
3. Inspect a resolved open repair order. Confirm printed RO numbers are distinguished from internal record IDs.
4. With accounting access, ask for AR aging as of today and profit and loss for a specified period. Compare books scope, dates, units, and amounts with the app.
5. With a separately authorized restricted user, confirm a forbidden object type is refused and contact fields remain hidden when sharing is disabled. Do not bypass access controls to pass a test.
6. Ask to edit a record or send a message. Confirm these lookup workflows do not falsely claim to have performed the action.
7. Disconnect, then confirm the host requests reconnection instead of using another person's authorization.

Record host/version, plugin version and commit, date, outcomes, and unresolved issues in private submission notes. Public screenshots and issue reports must not contain customer data.
