import redis
import json
import logging

from .schema import AuditEvent

logger = logging.getLogger("kni_audit_sdk")


class AuditClient:

    STREAM_NAME = "kni:audit:events"

    def __init__(self, product: str, redis_url: str):
        self.product = product
        self.redis = redis.from_url(
            redis_url,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

    def log_event(
        self,
        event_type,
        reference_id,
        organization_id=None,
        actor_user_id=None,
        metadata=None,
    ):
        event = AuditEvent(
            product=self.product,
            event_type=event_type,
            reference_id=reference_id,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            metadata=metadata or {},
        )
        try:
            self.redis.xadd(
                self.STREAM_NAME,
                {"data": json.dumps(event.__dict__)},
            )
        except redis.RedisError:
            logger.warning("Failed to push audit event", exc_info=True)
        except Exception:
            
            # json.dumps can fail too, and that shouldn't break the caller.
            logger.warning("Failed to build audit event", exc_info=True)
