from datetime import date as date_type
from pydantic import BaseModel


class SummaryResponseSchema(BaseModel):
    summary: str
    date_from: date_type
    date_to: date_type
    currency: str