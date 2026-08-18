from typing import Literal
from pydantic import BaseModel


class CategorizeSuggestionRequest(BaseModel):
    description: str
    operation_code: Literal["credit", "debit"]


class CategorySuggestionResponse(BaseModel):
    category_code: str
    category_name: str