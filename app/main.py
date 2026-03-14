import json
from contextlib import asynccontextmanager
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Depends
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, text
from .database import engine, Base, db_session
from .models import Category, Coupon
from .config import settings

# --- LIFESPAN: create tables on startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Lightweight migration for old DBs created before `category` existed.
        category_exists = await conn.scalar(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'coupons'
                      AND column_name = 'category'
                )
                """
            )
        )
        if not category_exists:
            await conn.execute(
                text(
                    "ALTER TABLE coupons ADD COLUMN category VARCHAR NOT NULL DEFAULT 'Others'"
                )
            )
    yield

# Initialize FastAPI
app = FastAPI(title="Smart Coupon Saver V1.0", lifespan=lifespan)

# --- CONFIGURATION ---
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# --- LOGIC ---

async def pick_best_deal(platform: str, amount: float, session: AsyncSession):
    """Queries the DB for eligible coupons, then returns the one with the highest value."""
    today = date.today()

    result = await session.execute(
        select(Coupon).where(
            Coupon.platform.ilike(platform),
            Coupon.expiry >= today,
            or_(Coupon.min_spend == None, Coupon.min_spend <= amount),
        )
    )
    eligible = result.scalars().all()

    if not eligible:
        return None

    return max(eligible, key=lambda c: c.value)

# --- ENDPOINTS ---

@app.post("/add-coupon")
async def add_coupon(user_text: str, session: AsyncSession = Depends(db_session)):
    """Uses Gemini to turn natural language into a structured coupon object."""
    prompt = f"""
    Extract coupon details from this text: '{user_text}'. 
    Return ONLY a JSON object with these keys: 
    - platform (string)
    - value (number)
    - min_spend (number, use 0 if none)
    - expiry (YYYY-MM-DD)
    - category (string)
    
    CRITICAL RULE: For the 'category' key, you MUST choose exactly one of these exact words: [Food, Electronics, Fashion, Health, Travel, Others]. Categorize it logically based on the platform.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            }
        )
        data = json.loads(response.text)
        coupon = Coupon(
            platform=data["platform"],
            value=float(data["value"]),
            min_spend=float(data["min_spend"]) if data.get("min_spend") is not None else None,
            expiry=datetime.strptime(data["expiry"], "%Y-%m-%d").date(),
            category=Category(data["category"]),
        )
        session.add(coupon)
        await session.commit()
        await session.refresh(coupon)
        return {"status": "success", "saved_coupon": data}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend")
async def recommend(platform: str, amount: float, session: AsyncSession = Depends(db_session)):
    """Finds the best coupon for the user's current shopping cart."""
    best = await pick_best_deal(platform, float(amount), session)
    if not best:
        return {"message": f"No valid coupons found for {platform}. Try a public code like WELCOME50!"}
    return {
        "message": "Best deal found!",
        "coupon": {
            "id": best.id,
            "platform": best.platform,
            "value": best.value,
            "min_spend": best.min_spend,
            "expiry": str(best.expiry),
            "category": best.category,
        },
    }

@app.get("/coupons")
async def list_coupons(session: AsyncSession = Depends(db_session)):
    """Returns all coupons stored in the database."""
    result = await session.execute(select(Coupon))
    coupons = result.scalars().all()
    return {
        "coupons": [
            {
                "id": c.id,
                "platform": c.platform,
                "value": c.value,
                "min_spend": c.min_spend,
                "expiry": str(c.expiry),
                "category": c.category,
            }
            for c in coupons
        ]
    }


