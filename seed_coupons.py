import asyncio
from datetime import date, timedelta
from app.database import AsyncSessionLocal
from app.models import User, Coupon, Category, DiscountType
from app.auth import get_password_hash

async def seed():
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(
            username="sagarnegi@gmail.com",
            hashed_password=get_password_hash("12341234"),
            is_active=True
        )
        session.add(user)
        await session.flush()
        
        # Define 20 coupons
        today = date.today()
        coupons = [
            Coupon(platform="Swiggy", discount_type=DiscountType.PERCENTAGE.value, value=20, min_spend=50, max_cap=20, expiry=today + timedelta(days=7), category=Category.FOOD.value, user_id=user.id),
            Coupon(platform="Zomato", discount_type=DiscountType.AMOUNT.value, value=10, min_spend=30, max_cap=None, expiry=today + timedelta(days=14), category=Category.FOOD.value, user_id=user.id),
            Coupon(platform="KFC", discount_type=DiscountType.PERCENTAGE.value, value=15, min_spend=40, max_cap=10, expiry=today + timedelta(days=30), category=Category.FOOD.value, user_id=user.id),
            Coupon(platform="Domino's", discount_type=DiscountType.AMOUNT.value, value=5, min_spend=15, max_cap=None, expiry=today + timedelta(days=5), category=Category.FOOD.value, user_id=user.id),
            
            Coupon(platform="Amazon", discount_type=DiscountType.PERCENTAGE.value, value=10, min_spend=500, max_cap=100, expiry=today + timedelta(days=60), category=Category.ELECTRONICS.value, user_id=user.id),
            Coupon(platform="BestBuy", discount_type=DiscountType.AMOUNT.value, value=50, min_spend=1000, max_cap=None, expiry=today + timedelta(days=45), category=Category.ELECTRONICS.value, user_id=user.id),
            Coupon(platform="Samsung", discount_type=DiscountType.PERCENTAGE.value, value=5, min_spend=200, max_cap=50, expiry=today + timedelta(days=100), category=Category.ELECTRONICS.value, user_id=user.id),
            
            Coupon(platform="Myntra", discount_type=DiscountType.PERCENTAGE.value, value=30, min_spend=100, max_cap=30, expiry=today + timedelta(days=15), category=Category.FASHION.value, user_id=user.id),
            Coupon(platform="Nike", discount_type=DiscountType.AMOUNT.value, value=20, min_spend=80, max_cap=None, expiry=today + timedelta(days=40), category=Category.FASHION.value, user_id=user.id),
            Coupon(platform="Zara", discount_type=DiscountType.PERCENTAGE.value, value=15, min_spend=150, max_cap=25, expiry=today + timedelta(days=20), category=Category.FASHION.value, user_id=user.id),
            Coupon(platform="H&M", discount_type=DiscountType.AMOUNT.value, value=10, min_spend=50, max_cap=None, expiry=today + timedelta(days=10), category=Category.FASHION.value, user_id=user.id),
            
            Coupon(platform="1mg", discount_type=DiscountType.PERCENTAGE.value, value=12, min_spend=30, max_cap=15, expiry=today + timedelta(days=80), category=Category.HEALTH.value, user_id=user.id),
            Coupon(platform="Apollo", discount_type=DiscountType.AMOUNT.value, value=5, min_spend=25, max_cap=None, expiry=today + timedelta(days=120), category=Category.HEALTH.value, user_id=user.id),
            Coupon(platform="NetMeds", discount_type=DiscountType.PERCENTAGE.value, value=20, min_spend=50, max_cap=20, expiry=today + timedelta(days=60), category=Category.HEALTH.value, user_id=user.id),
            
            Coupon(platform="MakeMyTrip", discount_type=DiscountType.AMOUNT.value, value=100, min_spend=1000, max_cap=None, expiry=today + timedelta(days=50), category=Category.TRAVEL.value, user_id=user.id),
            Coupon(platform="Uber", discount_type=DiscountType.PERCENTAGE.value, value=10, min_spend=10, max_cap=5, expiry=today + timedelta(days=2), category=Category.TRAVEL.value, user_id=user.id),
            Coupon(platform="Airbnb", discount_type=DiscountType.AMOUNT.value, value=30, min_spend=200, max_cap=None, expiry=today + timedelta(days=35), category=Category.TRAVEL.value, user_id=user.id),
            Coupon(platform="Agoda", discount_type=DiscountType.PERCENTAGE.value, value=15, min_spend=150, max_cap=40, expiry=today + timedelta(days=90), category=Category.TRAVEL.value, user_id=user.id),
            
            Coupon(platform="BookMyShow", discount_type=DiscountType.AMOUNT.value, value=2, min_spend=10, max_cap=None, expiry=today + timedelta(days=30), category=Category.OTHERS.value, user_id=user.id),
            Coupon(platform="Udemy", discount_type=DiscountType.PERCENTAGE.value, value=50, min_spend=0, max_cap=100, expiry=today + timedelta(days=365), category=Category.OTHERS.value, user_id=user.id)
        ]
        
        session.add_all(coupons)
        await session.commit()
        print("Successfully added user and 20 coupons.")

if __name__ == "__main__":
    asyncio.run(seed())
