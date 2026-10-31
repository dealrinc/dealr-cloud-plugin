---
name: bank-reconciliation
description: Investigate a Dealr.cloud bank reconciliation difference using read-only accounting evidence. Use when a statement, account register, or reconciliation does not agree.
---

# Investigate a reconciliation difference

Read [the reconciliation guide](references/guide.md) when investigating a difference, clearing failure, prior-period change, or access problem. It preserves Dealr-specific diagnostic details; use `search_docs` for the current UI workflow.

Establish the account, statement ending date and balance, and whether this is the first reconciliation. Ask whether the problem is a nonzero difference or a particular transaction that will not clear. Do not request a full bank statement when a date, balance, and specific disputed transactions suffice.

Call `get_context` first, then use available accounting read tools to inspect the intended rooftop's books. Use `search_journal_entries` for posted transactions and `get_financial_statement` for relevant balances. Follow live schemas for date ranges, account identifiers, reconciled-status filters, units, and pagination.

Investigate in this order:

1. Compare the same account, books scope, dates, and statement balance sign. Credit card and other liability accounts may use a different sign convention from the statement.
2. Check opening balances and whether the previous statement reconciled. A first reconciliation needs an established starting point.
3. Look for timing differences, outstanding checks or deposits, duplicate or missing entries, and differing transaction amounts.
4. Separate posted ledger evidence from clearing and reconciliation status. A posted transaction's presence does not prove it belongs to this reconciliation. Identify any status or statement evidence the available tools cannot retrieve.
5. Ask whether a prior reconciliation was unlocked or changed if a previously balanced period now differs. Escalate changes involving closed periods to the person responsible for the books.

Never recommend an adjusting entry simply to make the difference zero. First distinguish a timing or status issue from a genuinely missing or duplicated transaction; an adjustment can otherwise double-count money.

Use available Dealr documentation tools for current clearing, matching, locking, or unlocking procedures. Do not invent controls or claim to clear, reconcile, unlock, or edit anything through these read-only workflows. Present verified transactions separately from hypotheses and the remaining checks the user must make in Dealr.cloud.
