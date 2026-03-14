# Create a Coupons table with SQLAlchemy ORM and use the mapped_column function to define the columns. This will be used to store the coupons in the database.

from sqlalchemy import String, Float, Date, Integer
from sqlalchemy.orm import mapped_column
from .database import Base  

class Coupon(Base):
    __tablename__ = "coupons"

    id = mapped_column(Integer, primary_key=True, index=True)
    platform = mapped_column(String, nullable=False)
    value = mapped_column(Float, nullable=False)
    min_spend = mapped_column(Float, nullable=True)  # Optional
    expiry = mapped_column(Date, nullable=False)

    def __repr__(self):
        return f"<Coupon(platform={self.platform}, value={self.value}, min_spend={self.min_spend}, expiry={self.expiry})>"