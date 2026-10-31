# Publish and maintain the bundle

## Source of truth

Edit `plugin-source.json` for identity, version, publisher, listing links, and server endpoints. Run:

```bash
python3 scripts/plugin.py sync
python3 scripts/plugin.py check
python3 scripts/plugin.py build
python3 scripts/plugin.py build --target chatgpt
```

Claude chat and Cowork discover `.mcp.json`; Cursor discovers `mcp.json`. Both are generated from the same HTTP endpoint definition. Skills and assets are shared regular files, not host-specific copies or symlinks.

| Consumer | Repository entry point |
| --- | --- |
| Claude plugin and public directory | `.claude-plugin/plugin.json` |
| Claude organization / Code marketplace | `.claude-plugin/marketplace.json` |
| Cursor plugin | `.cursor-plugin/plugin.json` |
| Cursor team marketplace | `.cursor-plugin/marketplace.json` |
| Claude remote server discovery | `.mcp.json` |
| Cursor remote server discovery | `mcp.json` |

The Claude/Cursor identity is `dealr-cloud`. The marketplace name is also `dealr-cloud`, so Claude Code installs `dealr-cloud@dealr-cloud`. ChatGPT retains its assigned package name from the existing export rather than replacing it with that marketplace identity.

## Claude public directory

1. Run local validation and [host tests](TESTING.md).
2. Open https://claude.ai/directory/manage in the Dealr organization. Connect a GitHub account that can push to the repository.
3. Choose **Submit new > Plugin bundle**, enter https://github.com/dealrinc/dealr-cloud-plugin, leave the plugin path empty for the root, and track `main` unless deliberately choosing another branch or tag.
4. Run portal **Validate**, resolve findings, and review listing and data-handling answers. Local CLI validation does not replace the portal's scan.
5. Separately submit https://manage.dealr.cloud/mcp as an **MCP connector**. If Dealr already owns a submission for this endpoint, continue it instead of duplicating it. Pair the plugin with the same endpoint.
6. Supply reviewer access privately. Confirm tool testing and accept terms only when authorized, then submit for review. Follow the portal's explicit publication state; a passing scan does not necessarily publish a version.

The Plugins API manages organization distribution; it is not a substitute for public directory submission. The ZIP also supports manual upload without a public listing.

## Cursor public marketplace

At https://cursor.com/marketplace/publish, submit the public repository under the Dealr organization. Include the publisher contact, description, website, and square logo with its opaque background. The direct image URL is:

https://raw.githubusercontent.com/dealrinc/dealr-cloud-plugin/main/assets/logo.png

Importing the repository into a team marketplace is useful for testing but is distinct from public marketplace approval.

## Grok and Grok Bot

The shared form at https://x.ai/bot/marketplace/submit-a-plugin accepts a public repository or MCP URL. Use the repository to have skills and assets reviewed with the connector. Select the intended destinations; do not assume selecting Cursor replaces an existing Cursor submission.

The package has native Claude and Cursor manifests. This does not prove Grok Bot's ingestion behavior. Verify skill discovery and authenticated tools in Grok Bot before checking its testing attestation.

## Release an update

1. Work on a branch and use the repository's pull-request review process.
2. Raise `version` in `plugin-source.json` for every public package update; run `sync` and commit generated changes with the authored files.
3. Run relevant local and host tests. Confirm CI passes on the pull request.
4. Build from the exact reviewed commit. CI retains the ZIP and checksum as an artifact.
5. Merge the reviewed update and follow each marketplace's version review process. Team refresh and public directory approval are separate operations. Do not promise an update is live merely because a commit was pushed.

## ChatGPT and Codex

Run `python3 scripts/plugin.py build --target chatgpt`. The ZIP in `dist/chatgpt/` is named `app-6ab344f9b2e48191ac932d73268eda65-<version>.zip`, matching the existing package identity. It contains `.codex-plugin/plugin.json`, `.mcp.json`, shared skills and references, the original ChatGPT icons, the proprietary license, and export-specific documentation. It does not carry Claude/Cursor manifests, marketplace indexes, app references, or hooks.

The `openai` section of `plugin-source.json` points to `exports/chatgpt/baseline.json`, the imported public metadata from the supplied 1.0.0 package, and the original PNG asset. That baseline is authoritative for the ChatGPT name, author, description, license label, interface fields, review materials, country targeting, onboarding, and MCP configuration. Shared metadata no longer overwrites approved ChatGPT listing fields. Edit the baseline deliberately for a listing change, and replace it with the latest published package metadata when preparing a subsequent update.

The baseline `.mcp.json` remains URL-only, with the capitalized `Dealr` server key. Authentication and client-registration behavior remain with the existing connector flow; the exporter does not add DCR declarations, scopes, or a new client registration. It rejects endpoint drift between the baseline and the shared server. Change authentication explicitly and validate it in the portal if needed.

Set the shared `version` higher than the baseline version and write `openai.updateNotes` for the current update. Only that version and publication note change automatically; review cases and the supplied video URL are retained without claiming they were rerun. Reviewer access must stay outside the baseline and archive.

The public Agent Plugins MCP schema currently rejects the per-server OAuth extension described in OpenAI's documentation. This target therefore uses OpenAI's documented Codex compatibility layout, without claiming portable-schema conformance. It does not add a portable root manifest that could change Cursor's format selection.

Before submission:

1. Import this export in OpenAI's plugin portal as an MCP-enabled package. For the published Dealr.cloud plugin, upload a new version to the existing identity instead of creating a duplicate. A skills-only submission is not appropriate for these connected workflows.
2. Verify imported metadata and the existing connector's saved OAuth settings and endpoint discovery. Confirm production support for OpenAI's current UserInfo and verified-email/workspace-domain requirements; a successful package build does not establish this.
3. Complete any domain challenge without overwriting an existing plugin's challenge token. Use a permitted parent origin or ask support if there is a conflict.
4. Rerun the five positive and three negative cases retained from the baseline with the reviewer account, and confirm the existing video is still accessible and representative. Update the cases or recording deliberately if behavior changed. Do not invent current test results.
5. Enter reviewer credentials privately in the portal. Complete policy attestations and submit only when authorized. An upload, scan, review approval, and publication are distinct steps.

Native OpenAI importer validation and authenticated runtime testing remain outstanding. This tooling produces a format-ready export, not a guarantee of public approval.

References: https://developers.openai.com/plugins/build/plugins and https://developers.openai.com/plugins/deploy/submission

## Adapt for a new app

1. Create a separate repository. Replace source metadata, publisher, repository, docs/support/privacy/terms links, and MCP endpoints. The generator rejects missing or unknown source keys.
2. Choose a permanent unique name and start at `1.0.0`. Use HTTPS and explicit HTTP transport for a hosted OAuth server. Keep credentials out of configuration.
3. Replace branding and both image variants with the app's own square, opaque assets. Update the README and license to reflect its actual ownership and terms.
   For ChatGPT, replace the baseline manifest, server key, icons, publisher fields, review materials, and targeting as well. Do not reuse Dealr's assigned app identity or demo URL for a different app.
4. Rewrite skills against the real server schemas. Remove Dealr-specific prerequisites, examples, and concepts. This package's skills are not generic templates.
5. Run `sync`, validators, archive build, and authenticated tests in each target host. Inspect the extracted archive.
6. Submit under the app publisher's organization with accurate data handling and private reviewer access. The build does not provision OAuth clients, deploy a server, accept terms, or submit listings.

## Authoritative references

- https://claude.com/docs/plugins/build
- https://claude.com/docs/plugins/pre-submission-checklist
- https://claude.com/docs/plugins/submit
- https://code.claude.com/docs/en/plugins-reference
- https://cursor.com/docs/reference/plugins
- https://cursor.com/docs/plugins
