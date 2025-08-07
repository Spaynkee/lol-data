import pytest
from unittest.mock import MagicMock, Mock, patch
from lolData.management.helpers.lolparser import LolParser


@pytest.mark.django_db
def test_store_puuid_existing_user_calls_save():
    # Mock user instance
    mock_user = Mock()
    mock_user.puuid = None
    mock_user.save = Mock()

    # Mock the QuerySet filter().first() to return user
    mock_qs = MagicMock()
    mock_qs.first.return_value = mock_user

    with patch('lolData.models.LeagueUsers.objects') as mock_objects:
        mock_objects.filter.return_value = mock_qs

        parser = LolParser()
        account_name = "test_account"
        puuid = "test_puuid"

        parser.store_puuid(account_name, puuid)

        mock_objects.filter.assert_called_once_with(summoner_name=account_name)
        mock_qs.first.assert_called_once()

        # Confirm user.puuid was set and save was called
        assert mock_user.puuid == puuid
        mock_user.save.assert_called_once()


@pytest.mark.django_db
def test_store_puuid_no_user_does_nothing():
    # Simulate no user found (first() returns None)
    mock_qs = MagicMock()
    mock_qs.first.return_value = None

    with patch('lolData.models.LeagueUsers.objects') as mock_objects:
        mock_objects.filter.return_value = mock_qs

        parser = LolParser()
        account_name = "test_account"
        puuid = "test_puuid"

        # Should not raise and no save call
        parser.store_puuid(account_name, puuid)

        mock_objects.filter.assert_called_once_with(summoner_name=account_name)
        mock_qs.first.assert_called_once()
        # No user to save, so nothing else to check


@pytest.mark.django_db
def test_get_account_id_found_returns_puuid():
    # Mock user with puuid attribute
    mock_user = Mock()
    mock_user.puuid = "riot-puuid-123"

    # Mock QuerySet filter().first() returns mock_user
    mock_qs = MagicMock()
    mock_qs.first.return_value = mock_user

    with patch('lolData.models.LeagueUsers.objects') as mock_objects:
        mock_objects.filter.return_value = mock_qs

        parser = LolParser()
        account_name = "test_account"

        result = parser.get_account_id(account_name)

        mock_objects.filter.assert_called_once_with(summoner_name=account_name)
        mock_qs.first.assert_called_once()
        assert result == "riot-puuid-123"


@pytest.mark.django_db
def test_get_account_id_not_found_returns_none():
    mock_qs = MagicMock()
    mock_qs.first.return_value = None

    with patch('lolData.models.LeagueUsers.objects') as mock_objects:
        mock_objects.filter.return_value = mock_qs

        parser = LolParser()
        account_name = "test_account"

        result = parser.get_account_id(account_name)

        mock_objects.filter.assert_called_once_with(summoner_name=account_name)
        mock_qs.first.assert_called_once()
        assert result is None
