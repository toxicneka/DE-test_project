import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from extract import get_data_with_retry, save_to_db


class TestExtract:
    """Test cases for extract.py functionality"""

    @patch('extract.requests.get')
    def test_get_data_with_retry_success(self, mock_get):
        """Test successful API data retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'userId': 1, 'id': 1, 'title': 'Test Title', 'body': 'Test Body'}
        ]
        mock_get.return_value = mock_response

        result = get_data_with_retry()

        assert len(result) == 1
        assert result[0]['userId'] == 1
        assert result[0]['title'] == 'Test Title'
        mock_get.assert_called_once()

    @patch('extract.requests.get')
    @patch('extract.sleep')  # Mock sleep to speed up tests
    def test_get_data_with_retry_failure(self, mock_sleep, mock_get):
        """Test retry mechanism on API failure"""
        # Mock failed responses
        mock_get.side_effect = Exception("API unavailable")

        with pytest.raises(Exception, match="Failed to fetch data after 3 attempts"):
            get_data_with_retry()

        assert mock_get.call_count == 3

    @patch('extract.psycopg2.connect')
    def test_save_to_db(self, mock_connect):
        """Test database save functionality"""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cur = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        test_data = [
            {'userId': 1, 'id': 1, 'title': 'Title 1', 'body': 'Body 1'},
            {'userId': 2, 'id': 2, 'title': 'Title 2', 'body': 'Body 2'}
        ]

        save_to_db(test_data)

        # Verify connection was established
        mock_connect.assert_called_once()

        # Verify cursor was created
        mock_conn.cursor.assert_called_once()

        # Verify execute was called for each item
        assert mock_cur.execute.call_count == len(test_data)

        # Verify commit was called
        mock_conn.commit.assert_called_once()

        # Verify cursor and connection were closed
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('extract.psycopg2.connect')
    def test_save_to_db_empty_data(self, mock_connect):
        """Test database save with empty data"""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        save_to_db([])

        # Verify connection was established
        mock_connect.assert_called_once()

        # Verify no execute calls for empty data
        mock_cur.execute.assert_not_called()

        # Verify commit was still called
        mock_conn.commit.assert_called_once()
