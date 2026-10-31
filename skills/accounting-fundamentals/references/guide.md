# Accounting fundamentals

Use this when the dealer asks what a debit, credit, account type, or
journal entry is — or when they're confused by accounting terminology in
the system. This is the "what does this mean?" skill, not the "how do I
fix this?" skill.

Do not guess at exact menu paths, field labels, or button text — call
`search_docs` for those. This skill covers the concepts; the docs cover
the screens.

**This skill teaches mechanics, not decisions.** Explain how double-entry
works, what each account type does, and what debits and credits mean in
plain language. Do not advise which account to use or how to structure the
chart of accounts — those are decisions for the dealer's CPA.

Unlike workflow skills that must not improvise procedures, accounting
fundamentals are universal. The explanations below are safe to teach
directly because they describe how bookkeeping works, not how a specific
screen behaves. Use `search_docs` for anything about the system's UI.

## Double-entry bookkeeping

Every transaction that posts to the GL creates a journal entry with at
least two lines. A transaction dated before the dealer's accounting start
date skips journal generation, unless it's an opening balance. Total
debits always equal total credits — that's the fundamental rule. If a
dealer sees "out of balance," the two sides don't add up.

Think of it as: every dollar comes from somewhere and goes somewhere.
Posting a sale debits the customer receivable and credits income — it
doesn't move cash by itself. Cash moves later, in the separate payment
journal, which debits cash (or Undeposited Funds) and credits the
receivable. A bill records what's owed (credit AP) and the expense (debit
expense). The two sides always balance.

## The six account types

Every GL account is one of six types. The type determines which financial
statement the account appears on and whether its normal balance is a debit
or a credit.

**Balance sheet accounts** (what the business owns and owes right now):

- **Assets** — what the business owns or is owed. Cash, inventory,
  accounts receivable, vehicles. Normal balance: debit. A debit increases
  an asset; a credit decreases it.
- **Liabilities** — what the business owes. Loans payable, accounts
  payable, tax collected but not yet remitted. Normal balance: credit.
  A credit increases a liability; a debit decreases it.
- **Equity** — the owner's stake. Retained earnings, owner draws,
  contributed capital. Normal balance: credit.

**Income statement accounts** (activity over a period):

- **Income** (Revenue) — money earned. Vehicle sales, service revenue,
  finance income. Normal balance: credit. A credit increases income.
- **Cost of Goods Sold (COGS)** — the direct cost of what was sold.
  Vehicle cost of sale, RO parts cost. Normal balance: debit. Dealr
  tracks COGS as its own account type, reported separately from
  Expense on the P&L.
- **Expenses** — money spent to operate. Advertising, rent, utilities.
  Normal balance: debit. A debit increases an expense.

The plain-language version: assets, COGS, and expenses go up with debits.
Liabilities, equity, and income go up with credits. A debit to one side
always pairs with a credit to the other.

## Debits and credits in plain language

"Debit" and "credit" don't mean good or bad — they mean left and right in
the journal entry. Whether a debit is an increase or decrease depends on
the account type:

| Account type | Debit does | Credit does |
|---|---|---|
| Asset | Increases (more cash, more inventory) | Decreases |
| Liability | Decreases (pay down a loan) | Increases (take on debt) |
| Equity | Decreases (owner draw) | Increases (contribution) |
| Income | Decreases (return or adjustment) | Increases (a sale) |
| COGS | Increases (cost of sale) | Decreases (a cost reversal) |
| Expense | Increases (spend money) | Decreases (a refund) |

When a dealer says a number is "negative" on a report, it usually means
the account has a balance opposite its normal side — a credit balance in
an asset account, or a debit balance in a liability account.

## Journal entries

A journal entry is the system's record of a transaction. Every entry has:

- A date
- Two or more lines, each with an account and a debit or credit amount
- Total debits equal total credits

Some entries are created manually. Most are system-generated — created
automatically when the dealer posts a deal, records a payment, receives
inventory, or completes a repair order. The system builds the entry from
its accounting mapping configuration.

For entry corrections or mapping questions, use `search_docs` for documented workflows and involve the person responsible for the books. The lookup tools cannot change entries or mappings.

## Not every payment is an expense

A payment leaving the bank is not automatically an expense — it depends
on what the payment changes:

- **Loan payment** — splits between principal (reduces the loan
  liability) and interest expense. Only interest hits the P&L.
- **Owner draw** — reduces equity, not an expense.
- **Asset purchase** — buying equipment or a company vehicle creates a
  fixed asset. The cost spreads over time as depreciation, not as a lump expense.
- **Inventory** — buying a vehicle for resale creates inventory.
  The cost moves to Cost of Goods Sold when the vehicle sells.
- **Tax remittance** — paying collected sales tax reduces a liability, not an expense. Use `search_docs` for tax category workflows.
- **Transfer** — moving money between bank accounts is neither income
  nor expense. Both sides reference the same transfer account.

A P&L that looks expense-heavy may include balance-sheet payments
miscategorized as expenses. Use `search_docs` to investigate documented correction workflows.

## Common questions explained

### "Why did this payment create two lines?"
Double-entry requires a debit and a credit. A customer payment debits
cash (asset goes up) and credits accounts receivable (what they owe goes
down). Two lines, one transaction.

### "Why does my expense show as a debit?"
Expenses have a debit normal balance. A debit to an expense means
spending went up — that's correct and expected.

### "Why is my bank account showing a credit?"
A credit to the bank (an asset) means money went out. This is how the
system records a payment, withdrawal, or transfer out.

### "What's the difference between AP and an expense?"
Accounts Payable (AP) is a liability — it records what you owe but
haven't paid yet. An expense records the cost itself. When you receive a
bill: debit expense, credit AP. When you pay that bill: debit AP
(reducing what you owe), credit cash (money leaves the bank).

### "What does 'posted' mean?"
A posted transaction has been written to the general ledger as a journal
entry. Before posting, a deal or repair order is a working record;
after posting, it affects the books. System-generated entries post
automatically based on the module's workflow triggers.

## Always

- Use everyday language. Say "money in" and "money out" alongside the
  technical terms. The dealer is learning, not taking an exam.
- Relate concepts back to the system: "In your chart of accounts, each
  account has a type — that type tells the system whether a debit means
  more or less."
- Do not pick accounts, design chart structures, or advise on accounting
  treatment — route those to the dealer's CPA.
- For entry corrections, mapping, or bank categorization decisions, use `search_docs` for documented procedures and involve the person responsible for the books. Do not imply those workflows can be executed through the read-only tools.
- Use `search_docs` for how the system displays these concepts — the
  chart of accounts screen, the journal entry view, the GL detail report.
