from app.analytics.schemas import CategoryBreakdownSchema, PeriodComparisonSchema, SavingsRateSchema


SUMMARY_SYSTEM_PROMPT = (
    "You are a financial assistant inside the Moneta app. "
    "Analyze only the data provided to you in the message. "
    "Never invent numbers that are not present in the data. "
    "Respond in 3 to 5 sentences, be direct and practical, avoid filler phrases."
)


def build_summary_prompt(
    period_comparison: PeriodComparisonSchema,
    category_breakdown: list[CategoryBreakdownSchema],
    savings_rate: SavingsRateSchema,
) -> str:
    lines = []

    lines.append(f"Income: {period_comparison.current_income:.2f} {period_comparison.currency}")
    lines.append(f"Previous period income: {period_comparison.previous_income:.2f} {period_comparison.currency}")
    lines.append(f"Income change: {period_comparison.income_change_percentage:.1f}%")
    lines.append(f"Expense: {period_comparison.current_expense:.2f} {period_comparison.currency}")
    lines.append(f"Previous period expense: {period_comparison.previous_expense:.2f} {period_comparison.currency}")
    lines.append(f"Expense change: {period_comparison.expense_change_percentage:.1f}%")
    lines.append(f"Savings rate: {savings_rate.savings_rate_percentage:.1f}%")
    lines.append("")
    lines.append("Expenses by category:")

    for category_item in category_breakdown:
        category_line = f"- {category_item.category}: {category_item.total:.2f} {period_comparison.currency} ({category_item.percentage:.1f}%)"
        lines.append(category_line)

    lines.append("")
    lines.append(
        "Give a short analysis: how the situation changed compared to the previous period, "
        "what took up most of the spending, and anything worth paying attention to."
    )

    prompt = "\n".join(lines)
    return prompt