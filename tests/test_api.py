"""
Unit tests for WellTegra ML API

Tests all API endpoints with mocked BigQuery responses
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_bigquery():
    """Mock BigQuery client"""
    with patch('main.bq_client') as mock_bq:
        yield mock_bq


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_success(self, client, mock_bigquery):
        """Test successful health check"""
        # Mock BigQuery response
        mock_result = [{'count': 3}]
        mock_bigquery.query.return_value.result.return_value = mock_result

        response = client.get('/api/v1/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'bigquery' in data

    def test_health_check_failure(self, client, mock_bigquery):
        """Test health check when BigQuery fails"""
        # Mock BigQuery failure
        mock_bigquery.query.side_effect = Exception("Connection failed")

        response = client.get('/api/v1/health')
        assert response.status_code == 503

        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'


class TestRunsEndpoint:
    """Test /api/v1/runs endpoint"""

    def test_get_runs_success(self, client, mock_bigquery):
        """Test getting all runs"""
        # Mock BigQuery response
        mock_runs = [
            {
                'run_id': 'byford-r16',
                'run_name': 'Byford R16',
                'well_name': 'Anonymized',
                'run_date': None,
                'tool_count': 8,
                'total_length': 61.1,
                'max_od': 4.75,
                'outcome': 'Historical record'
            }
        ]

        mock_bigquery.query.return_value.result.return_value = [
            MagicMock(**{k: v for k, v in run.items()}) for run in mock_runs
        ]

        response = client.get('/api/v1/runs')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['count'] == 1
        assert len(data['data']) == 1

    def test_get_runs_with_limit(self, client, mock_bigquery):
        """Test getting runs with limit parameter"""
        mock_bigquery.query.return_value.result.return_value = []

        response = client.get('/api/v1/runs?limit=10')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_get_runs_with_sort(self, client, mock_bigquery):
        """Test getting runs with sort parameters"""
        mock_bigquery.query.return_value.result.return_value = []

        response = client.get('/api/v1/runs?sort_by=max_od&order=asc')
        assert response.status_code == 200


class TestRunDetailEndpoint:
    """Test /api/v1/runs/<run_id> endpoint"""

    def test_get_run_detail_success(self, client, mock_bigquery):
        """Test getting specific run details"""
        # Mock run data
        mock_run = {
            'run_id': 'byford-r16',
            'run_name': 'Byford R16',
            'well_name': 'Anonymized',
            'run_date': None,
            'tool_count': 8,
            'total_length': 61.1,
            'max_od': 4.75,
            'outcome': 'Historical record',
            'lessons': 'Test lessons'
        }

        mock_tools = [
            {
                'tool_id': 'byford-r16-1',
                'position': 1,
                'tool_name': 'Landing Sub',
                'od': 3.5,
                'neck_diameter': 2.75,
                'length': 1.2,
                'tool_category': 'drillstring'
            }
        ]

        # Mock BigQuery responses
        mock_bigquery.query.return_value.result.return_value = [
            MagicMock(**{k: v for k, v in mock_run.items()})
        ]

        response = client.get('/api/v1/runs/byford-r16')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data

    def test_get_run_detail_not_found(self, client, mock_bigquery):
        """Test getting non-existent run"""
        # Mock empty result
        mock_bigquery.query.return_value.result.return_value = []

        response = client.get('/api/v1/runs/nonexistent')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestToolsEndpoint:
    """Test /api/v1/tools endpoint"""

    def test_get_tools_success(self, client, mock_bigquery):
        """Test getting tool statistics"""
        mock_tools = [
            {
                'tool_name': 'Fishing Jars',
                'tool_category': 'fishing',
                'usage_count': 2,
                'avg_od': 3.25,
                'avg_length': 7.9,
                'min_od': 3.25,
                'max_od': 3.25
            }
        ]

        mock_bigquery.query.return_value.result.return_value = [
            MagicMock(**{k: v for k, v in tool.items()}) for tool in mock_tools
        ]

        response = client.get('/api/v1/tools')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_get_tools_with_category_filter(self, client, mock_bigquery):
        """Test getting tools filtered by category"""
        mock_bigquery.query.return_value.result.return_value = []

        response = client.get('/api/v1/tools?category=fishing')
        assert response.status_code == 200

    def test_get_tools_with_min_usage(self, client, mock_bigquery):
        """Test getting tools with minimum usage filter"""
        mock_bigquery.query.return_value.result.return_value = []

        response = client.get('/api/v1/tools?min_usage=2')
        assert response.status_code == 200


class TestAnalyticsEndpoint:
    """Test /api/v1/analytics endpoint"""

    def test_get_analytics_success(self, client, mock_bigquery):
        """Test getting analytics summary"""
        mock_summary = {
            'total_runs': 3,
            'total_tools': 18,
            'avg_toolstring_length': 48.9,
            'max_toolstring_length': 61.1,
            'avg_max_od': 5.5,
            'avg_tools_per_run': 6.0
        }

        mock_categories = [
            {'tool_category': 'fishing', 'count': 8, 'avg_length': 5.2},
            {'tool_category': 'completion', 'count': 5, 'avg_length': 7.9}
        ]

        mock_bigquery.query.return_value.result.return_value = [
            MagicMock(**{k: v for k, v in mock_summary.items()})
        ]

        response = client.get('/api/v1/analytics')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data


class TestIndexEndpoint:
    """Test root endpoint"""

    def test_index(self, client):
        """Test API documentation endpoint"""
        response = client.get('/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'name' in data
        assert 'version' in data
        assert 'endpoints' in data


class TestErrorHandlers:
    """Test error handlers"""

    def test_404_error(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['status'] == 'error'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
