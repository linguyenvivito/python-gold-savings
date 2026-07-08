from fastapi import APIRouter, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio
import re
from playwright.async_api import async_playwright

URL = "https://update.giavang.doji.vn/system/doji_92411/92411"
CACHE_TTL_SECONDS = 3600

# 1. Create a global state container for Playwright
state = {}
state_lock = asyncio.Lock()
cache_lock = asyncio.Lock()


async def _ensure_browser_initialized():
    browser = state.get("browser")
    if browser:
        return browser

    async with state_lock:
        browser = state.get("browser")
        if browser:
            return browser

        state["playwright"] = await async_playwright().start()
        state["browser"] = await state["playwright"].chromium.launch(
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox"],
        )
        return state["browser"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup: Runs when the server starts
    await _ensure_browser_initialized()
    yield
    # Teardown: Runs when the server shuts down
    browser = state.get("browser")
    playwright = state.get("playwright")
    if browser:
        await browser.close()
        state["browser"] = None
    if playwright:
        await playwright.stop()
        state["playwright"] = None


router = APIRouter(prefix="/gold", tags=["gold"], lifespan=lifespan)


def _cache_is_valid(now: datetime) -> bool:
    expires_at = state.get("cache_expires_at")
    return isinstance(expires_at, datetime) and now < expires_at and bool(state.get("cache_payload"))


def _parse_prices_from_text(body_text: str, captured_at: str):
    prices = []
    for raw_line in body_text.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            continue

        # Expected line shape:
        # PRODUCT NAME ... <buy> <sell or ->
        match = re.match(r"^(.+?)\s+([0-9][0-9\.,]*)\s+([0-9][0-9\.,]*|-)$", line)
        if not match:
            continue

        product = match.group(1).strip()
        buy = match.group(2).strip()
        sell = match.group(3).strip()
        if not product:
            continue

        prices.append(
            {
                "brand": "DOJI",
                "product": product,
                "buy": buy,
                "sell": "" if sell == "-" else sell,
                "captured_at": captured_at,
                "source_url": URL,
            }
        )

    return prices

@router.get("/doji", status_code=status.HTTP_200_OK)
async def scrape_page():
    now = datetime.utcnow()
    if _cache_is_valid(now):
        cached_payload = dict(state["cache_payload"])
        cached_payload["cache_hit"] = True
        cached_payload["cache_expires_at"] = state["cache_expires_at"].isoformat()
        return cached_payload

    async with cache_lock:
        now = datetime.utcnow()
        if _cache_is_valid(now):
            cached_payload = dict(state["cache_payload"])
            cached_payload["cache_hit"] = True
            cached_payload["cache_expires_at"] = state["cache_expires_at"].isoformat()
            return cached_payload

    browser = await _ensure_browser_initialized()

    page = await browser.new_page()
    try:
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        captured_at = datetime.utcnow().isoformat()
        prices = []

        rows_locator = page.locator("table tbody tr")
        if await rows_locator.count() > 0:
            rows = await rows_locator.all()

            for row in rows:
                cols = await row.locator("td").all()
                if len(cols) < 3:
                    continue

                product = (await cols[0].inner_text()).strip()
                buy = (await cols[1].inner_text()).strip()
                sell = (await cols[2].inner_text()).strip()

                if not product:
                    continue

                prices.append(
                    {
                        "brand": "DOJI",
                        "product": product,
                        "buy": buy,
                        "sell": sell,
                        "captured_at": captured_at,
                        "source_url": URL,
                    }
                )
        else:
            # DOJI page often renders plain text blocks instead of table tags.
            body_text = await page.inner_text("body")
            prices = _parse_prices_from_text(body_text, captured_at)

        if not prices:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="DOJI prices not found on page",
            )

        response_payload = {
            "count": len(prices),
            "data": prices,
            "cache_hit": False,
            "cache_expires_at": (datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)).isoformat(),
        }

        state["cache_payload"] = {
            "count": response_payload["count"],
            "data": response_payload["data"],
        }
        state["cache_expires_at"] = datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)

        return response_payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch DOJI prices: {exc}",
        ) from exc
    finally:
        await page.close()