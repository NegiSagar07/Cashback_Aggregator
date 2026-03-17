import json
from datetime import datetime

from google import genai

from ..config import settings
from ..models import Category, Coupon

client = genai.Client(api_key=settings.GEMINI_API_KEY)


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
