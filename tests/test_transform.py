import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from transform import run_transform


class TestTransform:
    """Test cases for transform.py functionality"""

    @patch('transform.psycopg2.connect')
    def test_run_transform_success(self, mock_connect):
        """Test successful transformation process"""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cur = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # Mock the count result
        mock_cur.fetchone.return_value = (10,)

        run_transform()

        # Verify connection was established
        mock_connect.assert_called_once()

        # Verify TRUNCATE was called
        mock_cur.execute.assert_any_call("TRUNCATE TABLE top_users_by_posts")

        # Verify INSERT was called
        assert mock_cur.execute.call_count >= 2

        # Verify commit was called
        mock_conn.commit.assert_called_once()

        # Verify count query was executed
        mock_cur.execute.assert_any_call("SELECT COUNT(*) FROM top_users_by_posts")

        # Verify cursor and connection were closed
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('transform.psycopg2.connect')
    def test_run_transform_database_error(self, mock_connect):
        """Test transformation with database error"""
        mock_connect.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            run_transform()

    @patch('transform.psycopg2.connect')
    def test_run_transform_empty_result(self, mock_connect):
        """Test transformation with empty result set"""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # Mock empty count result
        mock_cur.fetchone.return_value = (0,)

        run_transform()

        # Verify count query was executed and returned 0
        mock_cur.execute.assert_any_call("SELECT COUNT(*) FROM top_users_by_posts")
        mock_cur.fetchone.assert_called_once()


class TestAggregationLogic:
    """Test cases for aggregation logic (simulating SQL behavior)"""

    def test_user_post_count_aggregation(self):
        """Test the logic of counting posts per user"""
        # Simulate raw data that would come from database
        raw_posts = [
            {'user_id': 1, 'post_id': 1},
            {'user_id': 1, 'post_id': 2},
            {'user_id': 1, 'post_id': 3},
            {'user_id': 2, 'post_id': 4},
            {'user_id': 2, 'post_id': 5},
        ]

        # Simulate SQL GROUP BY logic
        user_post_counts = {}
        for post in raw_posts:
            user_id = post['user_id']
            user_post_counts[user_id] = user_post_counts.get(user_id, 0) + 1

        # Verify aggregation results
        assert user_post_counts[1] == 3
        assert user_post_counts[2] == 2
        assert len(user_post_counts) == 2

    def test_top_users_ordering(self):
        """Test ordering of users by post count"""
        user_post_counts = {1: 5, 2: 10, 3: 3, 4: 8}

        # Simulate ORDER BY posts_cnt DESC
        sorted_users = sorted(user_post_counts.items(), key=lambda x: x[1], reverse=True)

        # Verify ordering
        assert sorted_users[0] == (2, 10)  # User 2 has most posts
        assert sorted_users[1] == (4, 8)   # User 4 has second most
        assert sorted_users[2] == (1, 5)   # User 1 has third most
        assert sorted_users[3] == (3, 3)   # User 3 has least posts
