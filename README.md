# kni-audit-sdk

Small shared package for pushing audit/consent events to the shared Redis
stream. Used by eCAS, and later LAS and IP Platform.

It doesn't store anything. Your own database is still the source of truth —
this just sends a copy of the event to the shared log.

## Install

```
pip install git+https://github.com/KANDIWEALTHADVISORS/kni-audit-sdk.git@v1.0.0
```

Use the tag, not @main. Needs Python 3.10+.

## Usage

Make the client once, when your app starts:

```python
from kni_audit_sdk import AuditClient

audit = AuditClient(product="ecas", redis_url=settings.AUDIT_REDIS_URL)
```

Then log events where they happen:

```python
consent.save()

audit.log_event(
    event_type="consent.confirmed",
    reference_id=str(consent.id),
    organization_id=str(org.id),
    actor_user_id=str(request.user.id),
    metadata={"channel": "web"},
)
```

You don't pass `product` every time, it comes from the client.

`reference_id` is the id of the real row in your own database.

## Things to know

- `log_event()` doesn't return anything.
- It never raises. If Redis is down it logs a warning and moves on, so your
  actual code doesn't break.
- No retry. If an event doesn't make it, it's gone. That's intentional, the
  real record is in your own database.

Events go into the stream `kni:audit:events`.

## Event types

Format is `<domain>.<past-tense-verb>` — lowercase, dots, past tense.

- `consent.confirmed` — eCAS, customer confirmed consent

This list is incomplete. Only `consent.confirmed` is confirmed so far (it's
the one in the ticket). Add your event types here before wiring your product
in, otherwise we end up with two names for the same thing.

## metadata

Don't put personal data in it — no PAN, phone, email, bank details. Other
products read this stream, so send an id instead and keep the real record in
your own DB.

Values need to be JSON serializable, so no datetime objects. Use
`.isoformat()`.

## Running tests

```
pip install -e ".[dev]"
pytest
```

The test suite uses fakeredis, so it needs no running Redis. To check
against a real one:

```
docker run -d --name kni-redis -p 6379:6379 redis:7-alpine
```

To see what's in the stream:

```
docker exec kni-redis redis-cli XRANGE kni:audit:events - +
```
