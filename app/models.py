# Create a Coupons table with SQLAlchemy ORM and use the mapped_column function to define the columns. This will be used to store the coupons in the database.

from sqlalchemy import String, Float, Date, Integer
from sqlalchemy.orm import mapped_column
from .database import Base  
import enum

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

class Coupon(Base):
    __tablename__ = "coupons"

    id = mapped_column(Integer, primary_key=True, index=True)
    platform = mapped_column(String, nullable=False)
    discount_type = mapped_column(String, nullable=False, default=DiscountType.AMOUNT.value)
    value = mapped_column(Float, nullable=False)
    min_spend = mapped_column(Float, nullable=True)  # Optional
    expiry = mapped_column(Date, nullable=False)
    category = mapped_column(String, nullable=False)  # Required
    
    def __repr__(self):
        return f"<Coupon(platform={self.platform}, value={self.value}, min_spend={self.min_spend}, expiry={self.expiry})>"