import httpx

FRANKFURTER_URL = "https://api.frankfurter.dev/v2/rates"


async def fetch_rates(base: str, symbols: list[str]) -> list[dict] | None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                FRANKFURTER_URL,
                params={"base": base, "quotes": ",".join(symbols)},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()  # это list, а не dict
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError):
            return None