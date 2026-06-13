# Current Event Architecture

## Discovery

TTL already contains a generic event registry through AuditEvent.

---

## Current Model

AuditEvent

Fields:

* event_type
* entity_type
* entity_id
* actor_id
* workspace_id
* old_state
* new_state
* metadata_json
* created_at

---

## Institutional Interpretation

AuditEvent is not merely auditing.

AuditEvent is an institutional event stream.

---

## Future Usage

Claim Events

* verified
* published
* locked

Evidence Events

* exported
* verified

Verification Events

* reviewed
* downloaded
* externally_verified

Integrity Events

* mismatch_detected
* mismatch_resolved

Broker Events

* sync_completed
* sync_failed

---

## Conclusion

Verification Timeline should be built on AuditEvent.

A separate VerificationEvent table is unnecessary.
