from dataclasses import dataclass, field
import uuid
from datetime import datetime, timezone


@dataclass
class AuditEvent:

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0"
    product: str = ""
    event_type: str = ""
    organization_id: str | None = None
    actor_user_id: str | None = None
    reference_id: str = ""

    metadata: dict = field(default_factory=dict)
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )