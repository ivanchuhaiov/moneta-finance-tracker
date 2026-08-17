from app.models import CreditType, DebitType


CATEGORIZE_SYSTEM_PROMPT = (
    "You are a transaction categorization assistant inside the Moneta app. "
    "You must choose exactly one category from the provided list that best matches "
    "the transaction description. Always pick the closest match, even if the fit "
    "is not perfect. Never invent a category that is not in the list."
)


def build_categorize_prompt(description: str, categories: list[CreditType] | list[DebitType]) -> str:
    lines = []
    lines.append(f"Transaction description: {description}")
    lines.append("")
    lines.append("Available categories:")

    for category_item in categories:
        category_line = f"- {category_item.code}: {category_item.name}"
        lines.append(category_line)

    prompt = "\n".join(lines)
    return prompt