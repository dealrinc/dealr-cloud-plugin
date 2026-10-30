# Dealr.cloud

<img src="assets/logo.svg" width="128" height="128" alt="Dealr.cloud logo on a dark teal background">

**Look up dealership records.** Connect Cursor and compatible plugin hosts to your Dealr.cloud account through the hosted Model Context Protocol (MCP) server.

Dealr.cloud is the dealership management system independent auto dealers use to run inventory, sales, service, and accounting.

## What you can ask

- “Show vehicles in stock more than 90 days.”
- “Which repair orders are open?”
- “Find the deal for this stock number.”
- “What is our AR aging as of today?”
- “Show profit and loss for last month.”

Search inventory, customers, deals, leads, communications, repair orders, part orders, and parts inventory. Find customers and vehicles by supported identifiers, view record details, and read financial statements, journal entries, control balances, and AR/AP aging when your permissions allow it.

## Connect

1. Install the Dealr.cloud plugin from **Customize** once it is approved. For local testing, copy this repository's contents into `~/.cursor/plugins/local/dealr-cloud/`, then restart Cursor or run **Developer: Reload Window**. Confirm the plugin appears in **Customize**. Enterprise admins may need to allow local plugin imports.
2. Connect the `dealr` MCP server and complete the OAuth sign-in using your existing Dealr.cloud account. Review the requested access before approving it.
3. Ask a question about your dealership. The assistant discovers your permitted rooftops and available data before querying records.

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

## Access and privacy

Results include only the rooftops and records your Dealr.cloud user has permission to view. Contact-field sharing and record permissions are enforced by Dealr.cloud. Missing permissions are not an invitation to switch accounts or bypass access controls.

The record lookup and accounting tools described here read data; they do not edit dealership records, send messages, or post journal entries. Loan and title records are not included in the record lookup catalog. Server capabilities can evolve independently of this package; use the live tool descriptions and request-specific authorization for any additional capabilities a host exposes.

This repository contains plugin metadata, instructions, and brand assets. It contains no dealership records, authentication tokens, or backend implementation. Your AI host processes information returned by the connection under that host's own policies. You can revoke the connection from Dealr.cloud's connected-app settings.

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

## Publishing and updates

Submit this public repository at [Cursor's publisher page](https://cursor.com/marketplace/publish). The manifest is `.cursor-plugin/plugin.json`; MCP configuration is `mcp.json`. The square logo includes an opaque background and is committed at `assets/logo.svg`.

A 512 × 512 PNG copy is available at `assets/logo.png` for submission forms that require a direct image URL.

For package updates, edit the files, increment the manifest's semantic version, validate the package, and follow the marketplace's current review/update process. Do not assume pushing a commit immediately updates an approved listing.

## Links

- [Dealr.cloud](https://dealr.cloud)
- [Help center](https://dealr.cloud/docs)
- [Contact Dealr](https://dealr.cloud/contact)
- [Privacy policy](https://dealr.com/policies/privacy-policy/standalone/)
- [Terms of use](https://dealr.com/policies/website-terms-of-use/standalone/)

© 2026 Dealr, Inc. Dealr.cloud branding remains the property of Dealr, Inc. Access to the hosted service is subject to its terms and your account permissions.
