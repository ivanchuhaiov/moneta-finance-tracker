import logging
from datetime import datetime
from decimal import Decimal
from typing import NamedTuple, TypeAlias

logger = logging.getLogger(__name__)


class RateEntry(NamedTuple):
    fetched_at: datetime
    rate: Decimal


RatesIndex: TypeAlias = dict[tuple[str, str], list[RateEntry]]


def find_rate_for_date(
    rates_index: RatesIndex, base: str, target: str, target_date: datetime
) -> Decimal | None:
    entries = rates_index.get((base, target))
    if not entries:
        return None

    matching_rate = None
    for entry in entries:
        if entry.fetched_at <= target_date:
            matching_rate = entry.rate
            continue

        if matching_rate is None:
            logger.info(
                "No historical rate before %s for %s->%s, using nearest future rate from %s",
                target_date, base, target, entry.fetched_at,
            )
            matching_rate = entry.rate

        break

    return matching_rate


def convert_amount(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    rate: Decimal | None,
    transaction_date: datetime | None = None,
) -> Decimal | None:
    if from_currency == to_currency:
        return amount

    if rate is None:
        logger.warning(
            "No exchange rate found for %s->%s (transaction_date=%s)",
            from_currency, to_currency, transaction_date,
        )
        return None

    return amount * rate


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"))