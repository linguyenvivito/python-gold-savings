from fastapi import APIRouter, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio
from playwright.async_api import async_playwright

URL = "https://www.pnj.com.vn/site/gia-vang"
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

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/pnj", status_code=status.HTTP_200_OK)
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
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_selector("table tbody tr", timeout=15000)

        rows = await page.locator("table tbody tr").all()
        prices = []
        captured_at = datetime.utcnow().isoformat()

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
                    "brand": "PNJ",
                    "product": product,
                    "buy": buy,
                    "sell": sell,
                    "captured_at": captured_at,
                    "source_url": URL,
                }
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
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch PNJ prices: {exc}",
        ) from exc
    finally:
        await page.close()