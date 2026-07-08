from fastapi import APIRouter, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio
from playwright.async_api import async_playwright

URL = "https://sjc.com.vn/gia-vang-online"
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


async def _find_rows_locator(page):
    selectors = [
        "table tbody tr",
        "table tr",
    ]

    for _ in range(6):
        # Check main page first
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() > 0:
                return locator

        # Then check iframes where some sites render dynamic price tables
        for frame in page.frames:
            if frame == page.main_frame:
                continue
            for selector in selectors:
                locator = frame.locator(selector)
                if await locator.count() > 0:
                    return locator

        await page.wait_for_timeout(1000)

    return None


async def _is_anti_bot_page(page):
    title = (await page.title()).lower()
    content = (await page.content()).lower()
    markers = [
        "just a moment",
        "cloudflare",
        "enable javascript and cookies",
        "attention required",
    ]
    return any(marker in title or marker in content for marker in markers)

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

@router.get("/sjc", status_code=status.HTTP_200_OK)
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

        rows_locator = await _find_rows_locator(page)
        if rows_locator is None:
            if await _is_anti_bot_page(page):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "SJC website blocked automated access (anti-bot challenge). "
                        "Please retry later or run this endpoint from an environment "
                        "that can pass the site challenge."
                    ),
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="SJC prices table not found on page",
            )

        rows = await rows_locator.all()
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
                    "brand": "SJC",
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
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch SJC prices: {exc}",
        ) from exc
    finally:
        await page.close()