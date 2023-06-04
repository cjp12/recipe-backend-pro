"""this holds sample tests"""

from django.test import SimpleTestCase
from app import calc


class CalcTest(SimpleTestCase):
    """test the calc module"""

    def test_add(self):
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract(self):
        """test the subtract numbers method"""
        res = calc.subtract(10, 15)

        self.assertEqual(res, -5)
