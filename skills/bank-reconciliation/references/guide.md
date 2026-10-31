# Bank reconciliation

Use this when the user is reconciling a bank/GL account against a statement,
or a reconciliation shows a difference instead of zero.

Do not guess at exact menu paths, field labels, or button text — call
`search_docs` for those. This skill covers the diagnostic order of operations;
the docs cover the screens.

**Never propose an adjusting journal entry to force a reconciliation to
balance.** An adjusting entry posts real money to the ledger. If the actual
problem is a clearing status in the wrong period, the entry double-counts it
and the general ledger ends up overstated — permanently, once the period is
locked. Identify whether the discrepancy is a *status* problem or a genuinely
missing/duplicated *transaction* before anyone books anything, and route
anything touching a closed period to whoever owns the books.

## 1. Establish what "not balancing" means here

Ask, if not already clear from the conversation:

- Which account, and which statement period (the reconciliation's ending
  date)?
- Is this the account's first reconciliation, or was an earlier period already
  reconciled?
- Does the user mean the Difference figure is non-zero, or that specific
  transactions won't clear?

## 2. How the Difference figure is built

The reconciliation screen shows Beginning, Ending, and Change (Ending minus
Beginning) on one side, and Cleared on the other. Difference is Cleared minus
Change, and reads zero when the two agree.

Two things about those numbers surprise people:

- **Beginning is not typed in.** Dealr carries forward the Ending balance of
  the most recent *earlier-dated* reconciliation on that account, and uses
  zero when there is no earlier one.
- **Cleared counts only what is reconciled into this reconciliation** — not
  the cleared checkmarks on the account register. Those are different sets. If
  the user is comparing the register's cleared items to this figure, say so
  explicitly; the numbers are not supposed to match.

If the Cleared and Uncleared rows render blank rather than showing a number,
stop diagnosing the difference — that account's type is not one this screen
computes a cleared balance for, and the reconciliation can never be locked.
Escalate it.

## 3. If the Difference is non-zero

Work through these before anything else:

- **Sign, on a credit card or other liability account.** The sign convention
  flips: money owed reads as a positive balance and a payment *reduces* the
  cleared total. A statement balance entered with the sign a bank export uses
  produces a difference of roughly double the balance. Check the sign of the
  Ending balance first — this is the single most common false lead, and the
  default chart of accounts ships a reconcilable credit card account.
- **First reconciliation on the account.** Beginning is zero, so a
  pre-existing account balance has to be dealt with before the period can
  balance. Use `search_docs` for how a first reconciliation is meant to be
  set up.
- **Wrong ending date on the reconciliation.** Starting a reconciliation
  sweeps in *everything already cleared* on or before its ending date. If the
  date was entered wrong, that sweep is where wrong-period items came from —
  check the ending date before checking individual transactions. Note Dealr
  also refuses to create a reconciliation dated on or before an existing one,
  so an out-of-order period cannot simply be added after the fact.
- **Beginning-balance drift.** An earlier period was reconciled, then
  unlocked and changed. Dealr allows unlocking an earlier reconciliation even
  when later ones were built on it, which silently re-bases every later
  period's Beginning. Ask whether the previous period reconciled cleanly and
  whether anyone unlocked it since. A period the user believes was "finished"
  and is now off was either never locked or has been unlocked — a
  reconciliation cannot be locked until its Difference is exactly zero.

## 4. If a specific transaction won't clear or won't reconcile

Dealr refuses the change for specific, checkable reasons. Most likely first:

- **The account isn't set up to be reconciled.** Clearing is blocked outright
  on accounts not marked reconcilable, and the default chart of accounts marks
  only two. Check this before anything else.
- **The amount doesn't match.** The amount being cleared has to equal that
  transaction's net effect on that one account. A transaction hitting the
  account on several lines nets to a single figure; clearing a different
  figure is rejected.
- **The transaction doesn't touch the account,** or is voided. Voided
  transactions are excluded from reconciliation entirely.
- **The account clears line by line.** Accounts can be configured to track
  individual journal lines, in which case a specific line has to be named
  rather than the whole transaction.
- **Bank feed match.** A manual clear/unclear can be refused on a transaction
  still matched to a bank-feed entry until that match is removed. This affects
  clearing, not reconciling inside an open reconciliation.
- **Locked period.** A locked reconciliation refuses edits, re-reconciling,
  and deletion. Do not tell the user a locked period is immutable in every
  respect — if a locked period's numbers have visibly shifted, treat that as a
  support escalation rather than explaining it away.

## 5. If clearing status looks doubled up on one transaction

A straightforward double-clear is blocked, so a literal duplicate is unlikely.
What does happen: turning the account's individual-journal-lines setting on or
off after transactions were already cleared leaves whole-transaction and
per-line markers mixed together. Dealr detects this and offers to clean up the
stale markers as part of the action the user is taking — continuing removes
them rather than adding a duplicate.

The case that dead-ends: if any stale marker belongs to a *locked*
reconciliation, the cleanup is refused outright and that period has to be
unlocked first.

Ask whether that account setting was changed recently — it explains the
symptom better than anything in the transactions themselves.

## 6. If the user can't reach reconciliation at all

Check configuration before permissions:

- The reconciliation area only appears for accounts marked reconcilable, and
  never for control accounts. Since very few accounts are reconcilable by
  default, this is the more likely cause.
- If that checks out, it is a permissions question. Reconciliation maps to its
  own permission on granular permission setups but is bundled into general
  accounting edit access on simpler ones — do not assert which the dealer has.
  Have them confirm with an admin, and use `search_docs` for where it lives.

Either way, note that unlocking a past period is not a further-restricted
action: whoever can reconcile can also unlock.

## 7. Always

- Confirm the account and period before proposing a fix; the same symptom
  ("doesn't balance") has different fixes depending on whether the problem is
  in this period, an earlier one, or the account's configuration.
- Use `search_docs` for the actual UI steps (where cleared vs. reconciled
  status is shown, how to start, lock, or unlock a reconciliation, how bank
  feed matches are removed) — this skill only orders the questions to ask.
