# Create a Coupons table with SQLAlchemy ORM and use the mapped_column function to define the columns. This will be used to store the coupons in the database.

import enum
from datetime import date
from typing import List

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# Define the strict category list as an Enum
class Category(str, enum.Enum):
    FOOD = "Food"
    ELECTRONICS = "Electronics"
    FASHION = "Fashion"
    HEALTH = "Health"
    TRAVEL = "Travel"
    OTHERS = "Others"


class DiscountType(str, enum.Enum):
    AMOUNT = "amount"
    PERCENTAGE = "percentage"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    coupons: Mapped[List["Coupon"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    discount_type: Mapped[str] = mapped_column(String, nullable=False, default=DiscountType.AMOUNT.value)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    min_spend: Mapped[float | None] = mapped_column(Float, nullable=True)  # Optional
    max_cap: Mapped[float | None] = mapped_column(Float, nullable=True)  # Optional cap for percentage discounts
    expiry: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)  # Required
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    owner: Mapped[User] = relationship(back_populates="coupons")
    
    def __repr__(self):
        return f"<Coupon(platform={self.platform}, value={self.value}, min_spend={self.min_spend}, max_cap={self.max_cap}, expiry={self.expiry})>"