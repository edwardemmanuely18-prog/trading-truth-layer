# EvidenceRecord V1

## Objective

Create an immutable evidence layer between ImportBatch and Trade.

---

## Institutional Flow

ImportPreviewSession
↓
ImportBatch
↓
EvidenceRecord
↓
Trade
↓
Claim
↓
PublicRecord

---

## Purpose

Trade records are operational.

Evidence records are forensic.

Trade answers:

"What happened?"

EvidenceRecord answers:

"How do we prove it happened?"

---

## Proposed Fields

id

workspace_id

import_batch_id

source_type

adapter_name

verification_state

trade_fingerprint

evidence_hash

raw_payload_json

normalized_payload_json

created_at

---

## Verification States

pending

validated

verified

rejected

---

## Design Rules

Evidence records are immutable.

Evidence records never replace trades.

Trades remain the canonical ledger.

Evidence records provide provenance.

---

## Future Benefits

Broker Verification

Audit Trails

Integrity Monitoring

Evidence Registry

Verification Timeline

Trust Intelligence
