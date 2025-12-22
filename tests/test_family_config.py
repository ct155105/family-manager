"""
Tests for family_config.py - Dynamic Children Age Calculation

Following TDD approach:
1. Write tests FIRST
2. Run tests and watch them FAIL
3. Implement minimal code to pass
4. Run tests again and watch them PASS
5. Refactor
"""

import pytest
from datetime import datetime
from unittest.mock import patch, Mock


class TestChildrenData:
    """Test that CHILDREN constant is properly defined"""

    def test_children_constant_exists(self):
        """Test that CHILDREN constant is defined"""
        from family_config import CHILDREN
        assert CHILDREN is not None

    def test_children_is_list(self):
        """Test that CHILDREN is a list"""
        from family_config import CHILDREN
        assert isinstance(CHILDREN, list)

    def test_children_has_three_entries(self):
        """Test that family has 3 children"""
        from family_config import CHILDREN
        assert len(CHILDREN) == 3

    def test_children_have_required_fields(self):
        """Test that each child has name and birthdate fields"""
        from family_config import CHILDREN

        for child in CHILDREN:
            assert "name" in child, "Child missing 'name' field"
            assert "birthdate" in child, "Child missing 'birthdate' field"

    def test_children_birthdates_are_correct(self):
        """Test that birthdates match expected values"""
        from family_config import CHILDREN

        expected_birthdates = [
            "2018-04-27",  # Grayson, age 7
            "2019-12-03",  # Child 2, age 6
            "2022-02-22",  # Child 3, age 3
        ]

        actual_birthdates = [child["birthdate"] for child in CHILDREN]
        assert actual_birthdates == expected_birthdates


class TestGetChildrenAges:
    """Test dynamic age calculation function"""

    def test_get_children_ages_function_exists(self):
        """Test that get_children_ages function exists"""
        from family_config import get_children_ages
        assert callable(get_children_ages)

    def test_get_children_ages_returns_list(self):
        """Test that function returns a list"""
        from family_config import get_children_ages
        ages = get_children_ages()
        assert isinstance(ages, list)

    def test_get_children_ages_returns_three_ages(self):
        """Test that function returns 3 ages"""
        from family_config import get_children_ages
        ages = get_children_ages()
        assert len(ages) == 3

    def test_get_children_ages_returns_integers(self):
        """Test that ages are integers"""
        from family_config import get_children_ages
        ages = get_children_ages()
        for age in ages:
            assert isinstance(age, int), f"Age {age} is not an integer"

    @patch('family_config.datetime')
    def test_get_children_ages_calculates_correctly(self, mock_datetime):
        """Test age calculation with a fixed date"""
        # Mock today's date as 2025-12-21
        mock_datetime.now.return_value = datetime(2025, 12, 21)
        # Keep strptime working normally
        mock_datetime.strptime = datetime.strptime

        from family_config import get_children_ages
        ages = get_children_ages()

        # Expected ages on 2025-12-21:
        # Child 1: 2018-04-27 -> 7 years old
        # Child 2: 2019-12-03 -> 6 years old
        # Child 3: 2022-02-22 -> 3 years old
        expected_ages = [7, 6, 3]
        assert ages == expected_ages

    @patch('family_config.datetime')
    def test_get_children_ages_handles_birthday_not_yet_occurred(self, mock_datetime):
        """Test that age calculation handles birthdays that haven't occurred yet this year"""
        # Mock date before Child 2's birthday (Dec 3)
        mock_datetime.now.return_value = datetime(2025, 11, 1)
        # Keep strptime working normally
        mock_datetime.strptime = datetime.strptime

        from family_config import get_children_ages
        ages = get_children_ages()

        # Expected ages on 2025-11-01:
        # Child 1: 2018-04-27 -> 7 years old (birthday passed)
        # Child 2: 2019-12-03 -> 5 years old (birthday NOT passed yet)
        # Child 3: 2022-02-22 -> 3 years old (birthday passed)
        expected_ages = [7, 5, 3]
        assert ages == expected_ages


class TestGetChildrenAgeString:
    """Test helper function to format ages as string for system prompt"""

    def test_get_children_age_string_exists(self):
        """Test that get_children_age_string function exists"""
        from family_config import get_children_age_string
        assert callable(get_children_age_string)

    def test_get_children_age_string_returns_string(self):
        """Test that function returns a string"""
        from family_config import get_children_age_string
        age_string = get_children_age_string()
        assert isinstance(age_string, str)

    @patch('family_config.datetime')
    def test_get_children_age_string_formats_correctly(self, mock_datetime):
        """Test that ages are formatted as comma-separated string"""
        mock_datetime.now.return_value = datetime(2025, 12, 21)
        # Keep strptime working normally
        mock_datetime.strptime = datetime.strptime

        from family_config import get_children_age_string
        age_string = get_children_age_string()

        # Should return "7, 6, and 3" or similar format
        assert "7" in age_string
        assert "6" in age_string
        assert "3" in age_string
