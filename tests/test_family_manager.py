"""
Tests for family_manager.py - System Prompt Context Pre-fetching

Following TDD approach:
1. Write tests FIRST
2. Run tests and watch them FAIL
3. Implement minimal code to pass
4. Run tests again and watch them PASS
5. Refactor
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestCreateMessages:
    """Test that create_messages pre-fetches all required context"""

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_prefetches_all_context(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that create_messages calls all context functions"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs\nChild2 (age 6): princesses, art"
        mock_forecast.invoke.return_value = "Sunny, 75F"

        from family_manager import create_messages

        # Call function
        result = create_messages({})

        # Verify all context was pre-fetched
        mock_age_string.assert_called_once()
        mock_interests_string.assert_called_once()
        mock_forecast.invoke.assert_called_once_with({})
        mock_datetime.now.assert_called()

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_includes_weather_in_prompt(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that weather forecast is included in system prompt"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs\nChild2 (age 6): princesses, art"
        mock_forecast.invoke.return_value = "Rainy, 45F"

        from family_manager import create_messages

        result = create_messages({})

        # Verify weather is in system prompt
        system_prompt = result["messages"][0]["content"]
        assert "Rainy, 45F" in system_prompt

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_includes_date_in_prompt(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that today's date is included in system prompt"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs\nChild2 (age 6): princesses, art"
        mock_forecast.invoke.return_value = "Sunny, 75F"

        from family_manager import create_messages

        result = create_messages({})

        # Verify date is in system prompt
        system_prompt = result["messages"][0]["content"]
        assert "2025-12-21" in system_prompt

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_includes_children_ages_in_prompt(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that children's ages are included in system prompt"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs\nChild2 (age 6): princesses, art"
        mock_forecast.invoke.return_value = "Sunny, 75F"

        from family_manager import create_messages

        result = create_messages({})

        # Verify ages are in system prompt (now via interests_string)
        system_prompt = result["messages"][0]["content"]
        assert "age 7" in system_prompt or "7, 6, and 3" in system_prompt

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_returns_correct_structure(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that create_messages returns properly formatted messages"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs\nChild2 (age 6): princesses, art"
        mock_forecast.invoke.return_value = "Sunny, 75F"

        from family_manager import create_messages

        result = create_messages({})

        # Verify structure
        assert "messages" in result
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][1]["role"] == "user"
        assert isinstance(result["messages"][0]["content"], str)
        assert isinstance(result["messages"][1]["content"], str)

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_system_prompt_is_facts_not_instructions(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that system prompt contains facts, not instructions to call tools"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs\nChild2 (age 6): princesses, art"
        mock_forecast.invoke.return_value = "Sunny, 75F"

        from family_manager import create_messages

        result = create_messages({})
        system_prompt = result["messages"][0]["content"]

        # Should NOT contain instructions to check weather
        # (weather is already in the prompt)
        assert "check the weather" not in system_prompt.lower() or "weather forecast:" in system_prompt.lower()

        # SHOULD contain weather section
        assert "weather" in system_prompt.lower()

    @patch('family_manager.get_weekend_forecast')
    @patch('family_manager.get_children_interests_string')
    @patch('family_manager.get_children_age_string')
    @patch('family_manager.datetime')
    def test_create_messages_includes_interests_in_prompt(
        self, mock_datetime, mock_age_string, mock_interests_string, mock_forecast
    ):
        """Test that children's interests are included in system prompt"""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-12-21"
        mock_age_string.return_value = "7, 6, and 3"
        mock_interests_string.return_value = "Grayson (age 7): animals, dinosaurs, science"
        mock_forecast.invoke.return_value = "Sunny, 75F"

        from family_manager import create_messages

        result = create_messages({})
        system_prompt = result["messages"][0]["content"]

        # Verify interests are in system prompt
        assert "animals" in system_prompt.lower()
        assert "dinosaurs" in system_prompt.lower()


class TestToolsList:
    """Test that tools list only contains event fetchers"""

    def test_tools_list_does_not_include_weather(self):
        """Test that get_weekend_forecast is NOT in tools list"""
        from family_manager import tools

        tool_names = [tool.name for tool in tools]
        assert "get_weekend_forecast" not in tool_names

    def test_tools_list_does_not_include_date(self):
        """Test that get_today_date is NOT in tools list"""
        from family_manager import tools

        tool_names = [tool.name for tool in tools]
        assert "get_today_date" not in tool_names

    def test_tools_list_includes_event_fetchers(self):
        """Test that event fetching tools are still in tools list"""
        from family_manager import tools

        tool_names = [tool.name for tool in tools]
        assert "get_metroparks_events" in tool_names
        assert "get_columbus_zoo_events" in tool_names
        assert "get_lynd_fruit_farm_events" in tool_names

    def test_tools_list_has_only_event_fetchers(self):
        """Test that tools list contains ONLY event fetchers"""
        from family_manager import tools

        # Should have exactly 6 tools (all event fetchers)
        # Legacy: metroparks, zoo, lynd_fruit_farm
        # New AI-assisted: conservatory, olentangy_caverns, wilds
        assert len(tools) == 6
