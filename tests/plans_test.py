"""Unit tests for plans.py.
"""
from datetime import datetime
import unittest


from src.reading_plan.plans import ReadingPlan

class TestReadingPlan(unittest.TestCase):
    """Test class for ReadingPlan."""

    def test_pages(self) -> None:
        """Test for the pages attribute."""
        start_page = 1
        end_page = 80
        plan = ReadingPlan(start_page=start_page, end_page=end_page)

        expected_result = range(start_page, end_page + 1)
        self.assertEqual(plan.pages, expected_result)

    def test_formatted_date_range_same_month(self) -> None:
        """Test for the formatted_date_range attribute."""
        start_date = datetime.strptime('2000-01-01', '%Y-%m-%d') # Saturday
        end_date = datetime.strptime('2000-01-31', '%Y-%m-%d') # Monday
        start_page = 1
        end_page = 80
        num_times_to_read = 10
        name = 'Test Reading Plan'
        plan = ReadingPlan(start_date=start_date,
                           end_date=end_date,
                           start_page=start_page,
                           end_page=end_page,
                           num_times_to_read=num_times_to_read,
                           name=name)

        expected_result = 'Jan 1 - 31'
        self.assertEqual(plan.formatted_date_range, expected_result)

    def test_formatted_date_range_different_months(self) -> None:
        """Test for the formatted_date_range attribute."""
        start_date = datetime.strptime('2000-01-01', '%Y-%m-%d') # Saturday
        end_date = datetime.strptime('2000-02-10', '%Y-%m-%d') # Monday
        start_page = 1
        end_page = 80
        num_times_to_read = 10
        name = 'Test Reading Plan'
        plan = ReadingPlan(start_date=start_date,
                           end_date=end_date,
                           start_page=start_page,
                           end_page=end_page,
                           num_times_to_read=num_times_to_read,
                           name=name)

        expected_result = 'Jan 1 - Feb 10'
        self.assertEqual(plan.formatted_date_range, expected_result)


if __name__ == '__main__':
    unittest.main()
