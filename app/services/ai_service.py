import json
from datetime import datetime

from google import genai
from google.genai import types

from ..config import settings
from ..models import Category, Coupon
from ..schemas import CouponCreate

client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def extract_coupon_from_image(image_bytes: bytes) -> CouponCreate:
	prompt = """
	Analyze this image and extract coupon details. 
	Return ONLY a JSON object exactly matching the following rules:
	- platform (string)
	- discount_type (string: 'amount' or 'percentage')
	- value (number)
	- min_spend (number, use 0 if none)
	- max_cap (number or null)
	- expiry (YYYY-MM-DD format)
	- category (string)
    
	Rules for category: Must be exactly one of: [Food, Electronics, Fashion, Health, Travel, Others].
	"""

	try:
		response = await client.aio.models.generate_content(
			model="gemini-2.5-flash",
			contents=[
				types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
				prompt
			],
			config={"response_mime_type": "application/json"}
		)
	except AttributeError:
		# Fallback if the user's version of genai doesn't support .aio
		response = client.models.generate_content(
			model="gemini-2.5-flash",
			contents=[
				types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
				prompt
			],
			config={"response_mime_type": "application/json"}
		)

	data = json.loads(response.text)
	return CouponCreate(**data)


def parse_coupon_from_text(user_text: str) -> Coupon:
	prompt = f"""
	Extract coupon details from this text: '{user_text}'.
	Return ONLY a JSON object with these keys:
	- platform (string)
	- discount_type (string: amount or percentage)
	- value (number)
	- min_spend (number, use 0 if none)
	- max_cap (number or null)
	- expiry (YYYY-MM-DD)
	- category (string)

	"max_cap (number or null): Look for phrases like "up to ₹X" or "maximum discount of X". If there is a cap, put that number here. If it is a flat discount or has no limit, use null."

	CRITICAL RULES:
	1) For 'discount_type', choose exactly one: [amount, percentage].
	2) For 'category', choose exactly one of these exact words: [Food, Electronics, Fashion, Health, Travel, Others].
	"""

	response = client.models.generate_content(
		model="gemini-2.5-flash",
		contents=prompt,
		config={"response_mime_type": "application/json"},
	)
	data = json.loads(response.text)

	discount_type = str(data.get("discount_type", "amount")).strip().lower()
	if discount_type not in {"amount", "percentage"}:
		discount_type = "amount"

	return Coupon(
		platform=str(data["platform"]).strip(),
		discount_type=discount_type,
		value=float(data["value"]),
		min_spend=(
			float(data["min_spend"]) if data.get("min_spend") is not None else None
		),
		max_cap=(
			float(data["max_cap"]) if data.get("max_cap") is not None else None
		),
		expiry=datetime.strptime(data["expiry"], "%Y-%m-%d").date(),
		category=Category(data["category"]).value,
	)
