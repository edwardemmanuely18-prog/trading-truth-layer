# VerificationEvent Model Proposal

## Objective

Track institutional verification activity without modifying the existing claim lifecycle.

---

## Existing Claim Lifecycle

Draft
↓
Verified
↓
Published
↓
Locked

This lifecycle remains unchanged.

---

## VerificationEvent Purpose

Record activities performed against a claim after creation.

---

## Proposed Event Types

reviewed

downloaded

externally_verified

verification_note_added

allocator_reviewed

auditor_reviewed

evidence_exported

report_generated

public_record_viewed

---

## Future Structure

Claim
↓
VerificationEvent

One claim may have many verification events.

---

## Proposed Fields

id

workspace_id

claim_id

event_type

actor_type

actor_identifier

metadata_json

created_at

---

## Benefits

Verification Timeline

External Reviews

Audit History

Due Diligence Reports

Verification Network

Trust Intelligence
