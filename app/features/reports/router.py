from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.features.reports import service
from app.features.reports.schemas import ReportGenerateRequest

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate")
async def generate_report_endpoint(
    request: ReportGenerateRequest,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    buffer = await service.generate_report(session, current_user.id, request)

    filename = f"report_{request.date_from}_{request.date_to}.docx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )