from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, EntityType
from app.models.audit_log import AuditLog


async def log_audit_event(
    session: AsyncSession,
    user_id: int,
    action: AuditAction,
    entity_type: EntityType,
    entity_id: int,
    details: dict | None = None,
) -> None:
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    session.add(audit_entry)