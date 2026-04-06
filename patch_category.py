import sys

content = open("tests/test_coupons.py").read()
content = content.replace(
'''    c1 = Coupon(
        platform=platform,
        discount_type="percentage",
        value=10.0,
        min_spend=0.0,
        max_cap=5.0, # max saving 5
        expiry=datetime.date(2030, 1, 1),
        is_active=True
    )
    c2 = Coupon(
        platform=platform,
        discount_type="fixed",
        value=20.0, # saving 20
        min_spend=10.0,
        max_cap=None,
        expiry=datetime.date(2030, 1, 1),
        is_active=True
    )''',
'''    c1 = Coupon(
        platform=platform,
        discount_type="percentage",
        value=10.0,
        min_spend=0.0,
        max_cap=5.0, # max saving 5
        expiry=datetime.date(2030, 1, 1),
        category="E-commerce",
        is_active=True
    )
    c2 = Coupon(
        platform=platform,
        discount_type="fixed",
        value=20.0, # saving 20
        min_spend=10.0,
        max_cap=None,
        expiry=datetime.date(2030, 1, 1),
        category="E-commerce",
        is_active=True
    )'''
)
open("tests/test_coupons.py", "w").write(content)
