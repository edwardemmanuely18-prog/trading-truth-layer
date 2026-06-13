# Future Evidence Registry Architecture

## Objective

Introduce a provenance-driven evidence architecture without breaking existing TTL workflows.

---

## Future Canonical Flow

Broker
↓
Adapter
↓
Import Batch
↓
Evidence Record
↓
Trade Ledger
↓
Claim
↓
Public Record

---

## Design Principles

### Verification First

Evidence precedes trust.

### Immutable Evidence

Evidence records are never edited.

### Traceable Origin

Every trade must identify:

* Source
* Adapter
* Import Batch
* Evidence Record

### Auditability

Every trade must be traceable back to original imported evidence.

---

## Registry Components

### Trade Ledger

Current canonical trade storage.

### Evidence Record

Immutable normalized evidence.

### Import Batch

Collection of evidence records from one ingestion event.

### Integrity Registry

Future integrity monitoring surface.

### Audit Timeline

Future verification history surface.

---

## Compatibility Requirement

Existing imports:

* CSV
* MT5
* IBKR
* Manual Entry

must continue functioning throughout migration.

No existing claim workflows may be broken.
