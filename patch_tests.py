import sys

content = open("tests/test_coupons.py").read()
content = content.replace('assert response.status_code == 200', 'assert response.status_code == 200, response.json()')
open("tests/test_coupons.py", "w").write(content)
