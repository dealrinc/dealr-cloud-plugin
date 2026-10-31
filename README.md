# Dealr.cloud

![Dealr.cloud logo](assets/logo.png)

**Look up dealership records.** Connect Claude chat, Cowork, Claude Code, and Cursor to your Dealr.cloud account through the hosted Model Context Protocol (MCP) server.

Dealr.cloud is the dealership management system independent auto dealers use to run inventory, sales, service, and accounting.

## What you can ask

- “Show vehicles in stock more than 90 days.”
- “Which repair orders are open?”
- “Find the deal for this stock number.”
- “What is our AR aging as of today?”
- “Show profit and loss for last month.”

Search inventory, customers, deals, leads, communications, repair orders, part orders, and parts inventory. Find customers and vehicles by supported identifiers, view record details, and read financial statements, journal entries, control balances, and AR/AP aging when your permissions allow it.

## Install in Claude chat or Cowork

Until the public directory listing is approved, build the upload ZIP with `python3 scripts/plugin.py build`. Open **Customize > Plugins > Add > Upload plugin** and select the versioned ZIP in `dist/`. Alternatively, choose **Add marketplace**, enter https://github.com/dealrinc/dealr-cloud-plugin, and install `dealr-cloud`.

Open the plugin's **Connectors** tab, connect Dealr, and complete OAuth using your existing Dealr.cloud account. On Team and Enterprise, an Owner adds the connector for the organization before members connect their own accounts. Organization policies may restrict installation. Installing a plugin does not complete OAuth or grant additional Dealr permissions.

## Install in Claude Code

```text
/plugin marketplace add dealrinc/dealr-cloud-plugin
/plugin install dealr-cloud@dealr-cloud
```

Open `/mcp` to authenticate Dealr. The skills are available as `/dealr-cloud:get-started`, `/dealr-cloud:accounting-fundamentals`, and `/dealr-cloud:bank-reconciliation`.

For local development, start `claude --plugin-dir /absolute/path/to/dealr-cloud-plugin`.

## Install in Cursor

Once approved, install from **Customize**. For local testing, copy this repository into `~/.cursor/plugins/local/dealr-cloud/`, restart Cursor or run **Developer: Reload Window**, and confirm all three skills and Dealr's MCP server appear in Customize. Enterprise admins may need to allow local plugin imports. Symlinks pointing outside the local plugin folder are not supported.

Teams can import this repository from **Dashboard > Plugins & MCPs > Team Marketplaces > Add Marketplace > Import from Repo**. Each person must connect Dealr using their own OAuth account.

## Connection requirements

An active Dealr.cloud account and dealership access to AI tools are required. A dealership admin must enable **Integrations > Connect AI tools** for your user. Customer contact details appear only when the dealership enables them under **Settings > AI Tools**.

If your MCP client supports remote servers but not plugin installation, add this URL directly using OAuth:

```text
https://manage.dealr.cloud/mcp
```

No API key, shared password, local server, or package installation is required for the hosted connection. Each user authorizes their own account.

## Bundled skills

| Skill | Purpose |
| --- | --- |
| `get-started` | Discover account scope, find records, and interpret paginated results. |
| `accounting-fundamentals` | Explain financial statements, debits, credits, and balances using retrieved evidence. |
| `bank-reconciliation` | Investigate reconciliation differences using read-only accounting evidence. |

## Privacy Policy

Results include only the rooftops and records your Dealr.cloud user has permission to view. Contact-field sharing and record permissions are enforced by Dealr.cloud. Missing permissions are not an invitation to switch accounts or bypass access controls.

The record lookup and accounting tools described here read data; they do not edit dealership records, send messages, or post journal entries. Loan and title records are not included in the record lookup catalog. Server capabilities can evolve independently of this package; use the live tool descriptions and request-specific authorization for any additional capabilities a host exposes.

This repository contains plugin metadata, instructions, development tooling, and brand assets. The installed bundle declares no hooks, local processes, or telemetry collectors. It contains no dealership records, authentication tokens, or backend implementation. Your AI host processes information returned by the connection under that host's own policies. The hosted service's collection, retention, and sharing practices are covered by [Dealr's privacy policy](https://dealr.com/policies/privacy-policy/standalone/). You can revoke the connection from Dealr.cloud's connected-app settings.

## Verify the connection

Use a dealership and user you are authorized to test with:

1. Complete OAuth, then ask the assistant to call `get_context` and confirm the expected rooftops and available object types.
2. Ask “Show vehicles in stock more than 90 days.” Compare the returned scope and results with the same user's Dealr.cloud account.
3. If the user has accounting access, ask “What is our AR aging as of today?” Check the report date and books scope.
4. Confirm customer contact fields remain unavailable when sharing is disabled, and that unavailable object types return a permission refusal rather than data.

Never put reviewer credentials, real customer examples, or exported dealership data in this public repository. Arrange reviewer access separately.

## Troubleshooting

- **Sign-in or consent is unavailable:** confirm AI tools are enabled for your dealership and user, then reconnect through OAuth.
- **A record is missing:** check the selected rooftops, filters, pagination, and your account's permissions in Dealr.cloud.
- **Contact details are missing:** ask an admin to review the dealership's AI Tools contact-sharing setting.
- **A report differs from the app:** compare dates, timezone, and which rooftop's books were selected.

## Validate, package, and publish

Use Python 3.9+ for the dependency-free build tooling and Claude Code 2.1.311+ for native Claude validation:

```bash
python3 scripts/plugin.py check
claude plugin validate .claude-plugin/plugin.json --strict --profile directory
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate skills --strict
python3 scripts/plugin.py build
python3 scripts/plugin.py build --target chatgpt
```

The default build creates a versioned ZIP and `SHA256SUMS` in `dist/shared/`. The ZIP has both native manifests, both MCP configuration filenames, shared skills, branding, license, and documentation. It excludes Git history, development tooling, CI files, and root environment files. Rebuilding identical files with the same toolchain produces the same checksum.

The ChatGPT export is separate, in `dist/chatgpt/`. It uses the documented OpenAI/Codex compatibility manifest with listing metadata, onboarding, and a remote OAuth/DCR declaration. It reuses the skills and assets without changing Claude or Cursor metadata. Package checks do not prove OpenAI importer acceptance; see the [ChatGPT submission requirements](docs/PUBLISHING.md#chatgpt-and-codex).

Edit `plugin-source.json` for shared identity, version, listing links, and server endpoints, then run `python3 scripts/plugin.py sync` to regenerate both hosts' metadata. Shared skills and assets remain ordinary files. CI detects stale generated files and validates both the source plugin and the extracted upload ZIP.

See [Testing](docs/TESTING.md) for authenticated checks and [Publishing](docs/PUBLISHING.md) for Claude, Cursor, Grok, version updates, and adapting the bundle for a new app. Package validation does not establish marketplace approval or an authenticated connection. Grok Bot ingestion still needs its own in-app test.

## License

This package is proprietary; see [LICENSE](LICENSE). Dealr, Inc. retains the plugin and brand rights. A public repository does not grant an open-source license. Hosted service access remains governed by your existing Dealr agreement and terms of use.

## Links

- [Dealr.cloud](https://dealr.cloud)
- [Help center](https://dealr.cloud/docs)
- [Contact Dealr](https://dealr.cloud/contact)
- [Privacy policy](https://dealr.com/policies/privacy-policy/standalone/)
- [Terms of use](https://dealr.com/policies/website-terms-of-use/standalone/)

© 2026 Dealr, Inc. Dealr.cloud branding remains the property of Dealr, Inc. Access to the hosted service is subject to its terms and your account permissions.
