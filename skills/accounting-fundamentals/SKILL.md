---
name: accounting-fundamentals
description: Explain Dealr.cloud financial statements, journal entries, debits, credits, and account balances using read-only accounting tools. Use for accounting questions and report interpretation.
---

# Explain dealership accounting

For a dealer learning bookkeeping concepts, read [the accounting guide](references/guide.md). It covers the six account types, payment-versus-expense distinctions, and common questions. Use `search_docs` for current Dealr UI procedures and configured account mappings.

Call `get_context` before accounting tools. Establish the report date or period and the intended rooftop's books. Several rooftops may share books; a location filter and a books selection are not interchangeable. Follow each live tool's schema and permission notices.

Choose the read tool that answers the question:

- `get_financial_statement`: balance sheet, profit and loss, or trial balance.
- `search_journal_entries`: posted journal lines behind a balance or transaction.
- `get_aging_report`: receivables or payables by age as of a date.
- `get_control_balance`: balances and open items linked to a resolved record.

Resolve record IDs before using them. Preserve returned units and decimal precision; do not assume dollar values are integer cents or rescale them without schema evidence. Check pagination before totaling journal lines. Distinguish the report's total from the subtotal of a returned page.

Explain debits and credits in plain language:

| Account type | Debit | Credit |
| --- | --- | --- |
| Assets, cost of goods sold, expenses | Increase | Decrease |
| Liabilities, equity, income | Decrease | Increase |

An entry's total debits equal total credits. A payment leaving the bank is not automatically an expense: it may reduce a liability, purchase an asset, or transfer funds. A sale and its later customer payment are separate events.

Tie explanations of the dealership's actual numbers to retrieved records and the selected report scope. If records or permissions are unavailable, explain the limitation rather than inventing a balance. Separate observed facts from possible explanations. Use available Dealr documentation tools for exact UI procedures instead of guessing menu paths.

These tools read accounting data. Do not post entries or propose a journal entry merely to force two reports to agree. Account selection, tax treatment, and changes to closed periods require the person responsible for the books or their accountant.
