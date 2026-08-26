import json
import logging
from datetime import datetime

import fakeredis

from kni_audit_sdk import AuditClient, AuditEvent

# Nothing is listening on this port, on purpose.
UNREACHABLE = "redis://localhost:9999/0"


def test_each_event_gets_its_own_id():
    assert AuditEvent().event_id != AuditEvent().event_id


def test_event_defaults():
    event = AuditEvent(
        product="ecas", event_type="consent.confirmed", reference_id="4567"
    )
    assert event.schema_version == "1.0"
    assert event.metadata == {}
    assert event.occurred_at.endswith("+00:00")


def test_event_reaches_the_stream():
    client = AuditClient(product="ecas", redis_url=UNREACHABLE)
    client.redis = fakeredis.FakeRedis(decode_responses=True)

    client.log_event(
        event_type="consent.confirmed",
        reference_id="4567",
        organization_id="ORG-88",
        metadata={"channel": "web"},
    )

    entries = client.redis.xrange("kni:audit:events", "-", "+")
    assert len(entries) == 1

    payload = json.loads(entries[0][1]["data"])
    assert payload["product"] == "ecas"
    assert payload["event_type"] == "consent.confirmed"
    assert payload["reference_id"] == "4567"
    assert payload["organization_id"] == "ORG-88"
    assert payload["metadata"] == {"channel": "web"}


def test_unreachable_redis_does_not_raise(caplog):
    client = AuditClient(product="ecas", redis_url=UNREACHABLE)
    with caplog.at_level(logging.WARNING, logger="kni_audit_sdk"):
        client.log_event(event_type="consent.confirmed", reference_id="4567")
    assert "Failed to push audit event" in caplog.text


def test_unserializable_metadata_does_not_raise(caplog):
    client = AuditClient(product="ecas", redis_url=UNREACHABLE)
    with caplog.at_level(logging.WARNING, logger="kni_audit_sdk"):
        client.log_event(
            event_type="consent.confirmed",
            reference_id="4567",
            metadata={"when": datetime.now()},
        )
    assert "Failed to build audit event" in caplog.text
