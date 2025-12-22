"""
Family Configuration Module

Stores children's information and provides utilities for calculating current ages.
This module serves as the single source of truth for family data.
"""

from datetime import datetime
from typing import List, Dict


# Children data with birthdates
CHILDREN = [
    {
        "name": "Grayson",
        "birthdate": "2018-04-27"
    },
    {
        "name": "Child2",
        "birthdate": "2019-12-03"
    },
    {
        "name": "Child3",
        "birthdate": "2022-02-22"
    }
]


def get_children_ages() -> List[int]:
    """
    Calculate current ages of all children based on their birthdates.

    Returns:
        List[int]: A list of ages (in years) for each child

    Example:
        >>> ages = get_children_ages()
        >>> print(ages)  # On 2025-12-21
        [7, 6, 3]
    """
    today = datetime.now()
    ages = []

    for child in CHILDREN:
        # Parse birthdate string to datetime
        birth = datetime.strptime(child['birthdate'], '%Y-%m-%d')

        # Calculate age in years
        # Account for whether birthday has occurred this year
        age = today.year - birth.year

        # If birthday hasn't occurred yet this year, subtract 1
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1

        ages.append(age)

    return ages


def get_children_age_string() -> str:
    """
    Get a formatted string of children's ages suitable for system prompts.

    Returns:
        str: Comma-separated ages (e.g., "7, 6, and 3")

    Example:
        >>> age_string = get_children_age_string()
        >>> print(age_string)
        "7, 6, and 3"
    """
    ages = get_children_ages()

    if len(ages) == 0:
        return ""
    elif len(ages) == 1:
        return str(ages[0])
    elif len(ages) == 2:
        return f"{ages[0]} and {ages[1]}"
    else:
        # For 3+ children: "7, 6, and 3"
        all_but_last = ", ".join(str(age) for age in ages[:-1])
        return f"{all_but_last}, and {ages[-1]}"
