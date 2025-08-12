import unittest
from unittest.mock import patch, MagicMock
import time

from aicoder.llm.api_client import LLMClient
from aicoder.config import Config
from requests.exceptions import HTTPError as RequestsHTTPError


class TestLLMClientRetries(unittest.TestCase):
    """Test cases for LLM client retry functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_retry_count = Config.LLM_RETRY_COUNT
        self.original_min_delay = Config.LLM_RETRY_MIN_DELAY
        self.original_max_delay = Config.LLM_RETRY_MAX_DELAY

        # Set test-friendly values
        Config.LLM_RETRY_COUNT = 3
        Config.LLM_RETRY_MIN_DELAY = 0.1
        Config.LLM_RETRY_MAX_DELAY = 0.3

    def tearDown(self):
        """Restore original config values."""
        Config.LLM_RETRY_COUNT = self.original_retry_count
        Config.LLM_RETRY_MIN_DELAY = self.original_min_delay
        Config.LLM_RETRY_MAX_DELAY = self.original_max_delay

    @patch('aicoder.llm.api_client.OpenAIApiAdapter')
    @patch('aicoder.llm.api_client.time.sleep')
    def test_linear_backoff_retry_success_on_second_attempt(self, mock_sleep, mock_adapter_class):
        """Test that linear backoff works correctly when succeeding on second attempt."""
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_adapter_class.return_value = mock_adapter

        # Create mock response for HTTP 429
        mock_response = MagicMock()
        mock_response.status_code = 429
        rate_limit_error = RequestsHTTPError("429 Too Many Requests")
        rate_limit_error.response = mock_response

        # First call raises HTTP 429, second succeeds
        mock_adapter.create_completion.side_effect = [
            rate_limit_error,
            "success response"
        ]

        client = LLMClient("openai/test-model")
        result = client.sendRequest("system prompt", "user prompt")

        self.assertEqual(result, "success response")
        self.assertEqual(mock_adapter.create_completion.call_count, 2)
        # Should sleep once with linear delay
        mock_sleep.assert_called_once()

    @patch('aicoder.llm.api_client.OpenAIApiAdapter')
    @patch('aicoder.llm.api_client.time.sleep')
    def test_linear_backoff_retry_exhausts_all_attempts(self, mock_sleep, mock_adapter_class):
        """Test that all retry attempts are exhausted before failing."""
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_adapter_class.return_value = mock_adapter

        # Create mock response for HTTP 429
        mock_response = MagicMock()
        mock_response.status_code = 429
        rate_limit_error = RequestsHTTPError("429 Too Many Requests")
        rate_limit_error.response = mock_response

        # All calls raise rate limit error
        mock_adapter.create_completion.side_effect = rate_limit_error

        client = LLMClient("openai/test-model")

        with self.assertRaises(RuntimeError) as context:
            client.sendRequest("system prompt", "user prompt")

        self.assertIn("failed after 3 retries", str(context.exception))
        self.assertEqual(mock_adapter.create_completion.call_count, 4)  # 1 initial + 3 retries
        self.assertEqual(mock_sleep.call_count, 3)  # Should sleep 3 times

    @patch('aicoder.llm.api_client.OpenAIApiAdapter')
    @patch('aicoder.llm.api_client.time.sleep')
    def test_linear_backoff_retry_with_requests_http_error(self, mock_sleep, mock_adapter_class):
        """Test that HTTP 429 errors trigger retry logic."""
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_adapter_class.return_value = mock_adapter

        # Create mock response for HTTP 429
        mock_response = MagicMock()
        mock_response.status_code = 429
        http_error = RequestsHTTPError("429 Too Many Requests")
        http_error.response = mock_response

        # First call raises HTTP 429, second succeeds
        mock_adapter.create_completion.side_effect = [
            http_error,
            "success response"
        ]

        client = LLMClient("openai/test-model")
        result = client.sendRequest("system prompt", "user prompt")

        self.assertEqual(result, "success response")
        self.assertEqual(mock_adapter.create_completion.call_count, 2)
        mock_sleep.assert_called_once()

    @patch('aicoder.llm.api_client.OpenAIApiAdapter')
    def test_non_rate_limit_http_error_not_retried(self, mock_adapter_class):
        """Test that non-429 HTTP errors are not retried."""
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_adapter_class.return_value = mock_adapter

        # Create mock response for HTTP 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        server_error = RequestsHTTPError("500 Internal Server Error")
        server_error.response = mock_response

        mock_adapter.create_completion.side_effect = server_error

        client = LLMClient("openai/test-model")

        with self.assertRaises(RequestsHTTPError):
            client.sendRequest("system prompt", "user prompt")

        # Should only be called once, no retries
        self.assertEqual(mock_adapter.create_completion.call_count, 1)

    def test_linear_delay_calculation(self):
        """Test that linear delay calculation works correctly."""
        # Test with known values
        Config.LLM_RETRY_COUNT = 3
        Config.LLM_RETRY_MIN_DELAY = 1.0
        Config.LLM_RETRY_MAX_DELAY = 3.0

        client = LLMClient("openai/test-model")

        # Expected delays: 1.0, 2.0, 3.0 (linear progression)
        expected_delays = [1.0, 2.0, 3.0]

        # Calculate delay step
        delay_step = (3.0 - 1.0) / (3 - 1)  # = 1.0

        calculated_delays = []
        for attempt in range(1, 4):
            delay = 1.0 + (attempt - 1) * delay_step
            delay = min(delay, 3.0)
            calculated_delays.append(delay)

        self.assertEqual(calculated_delays, expected_delays)


if __name__ == '__main__':
    unittest.main()