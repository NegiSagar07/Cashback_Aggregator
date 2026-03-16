from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional
from app.models import Category, DiscountType  # Import enums defined in models.py


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")


class UserCreate(UserBase):
    password: str = Field(..., min_length=1, description="Plain text password")


class UserRead(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class CouponBase(BaseModel):
    # Use Field constraints to ensure data quality
    platform: str = Field(..., min_length=1, description="The platform name (e.g., Swiggy)")
    value: float = Field(..., gt=0, description="The discount value")
    discount_type: DiscountType = Field(
        default=DiscountType.AMOUNT,
        description="Type of discount: 'amount' or 'percentage'",
    )
    
    # default=0.0 is better for math logic later
    min_spend: Optional[float] = Field(default=0.0, ge=0, description="Min spend required")
    
    expiry: date = Field(..., description="The expiry date of the coupon")
    
    # This is the "Senior" way: Use the Enum class as the type!
    # Pydantic will automatically validate that the input is one of your allowed categories.
    category: Category = Field(default=Category.OTHERS, description="Strict category type")

class CouponCreate(CouponBase):
    """Schema for creating a coupon (Request Body)"""
    pass

class CouponRead(CouponBase):
    """Schema for returning a coupon (Response Body)"""
    id: int
    user_id: int

    # In Pydantic V2, we use model_config instead of class Config
    model_config = ConfigDict(from_attributes=True)