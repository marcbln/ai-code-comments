# Implementation Checklist: Linear Backoff for LLM Retries

A checklist to track the implementation of the linear backoff retry mechanism for HTTP 429 errors.

## Phase 1: Configuration

- [ ] Add retry parameters to `aicoder/config.py`:
  - [ ] `LLM_RETRY_COUNT` (e.g., `5`)
  - [ ] `LLM_RETRY_MIN_DELAY` (e.g., `2`)
  - [ ] `LLM_RETRY_MAX_DELAY` (e.g., `30`)

## Phase 2: Core Logic Implementation

- [ ] Refactor `LLMClient.sendRequest` in `aicoder/llm/api_client.py`:
  - [ ] Import `Config`, `time`, and necessary exception types (`OpenAiRateLimitError`, `RequestsHTTPError`).
  - [ ] Wrap the API call (`self.provider.create_completion`) in a `for` loop to handle the initial attempt plus retries.
  - [ ] Calculate the linear `delay_step` based on min/max delay and retry count.
  - [ ] Implement the `time.sleep()` call within the loop for retry attempts.
  - [ ] Ensure the sleep duration increases linearly but is capped by `LLM_RETRY_MAX_DELAY`.
  - [ ] Add logging to inform the user about the retry attempt and sleep duration.
  - [ ] Implement a `try...except` block inside the loop.
  - [ ] Catch specific rate limit exceptions (`openai.RateLimitError`).
  - [ ] Catch `requests.exceptions.HTTPError` and check if `response.status_code` is `429` before retrying.
  - [ ] Ensure other exceptions are re-raised immediately and are not caught by the retry logic.
  - [ ] Raise a final `RuntimeError` if all retry attempts are exhausted, including the last exception in the message.

## Phase 3: Testing

- [ ] Create a new test file: `tests/test_api_client_retries.py`.
- [ ] Write a unit test for a **successful retry** scenario:
  - [ ] Mock the provider's `create_completion` method to fail twice with a rate limit error, then succeed.
  - [ ] Assert that the correct successful response is returned.
  - [ ] Assert that the API call count is correct (e.g., 3 calls for 2 failures).
  - [ ] Assert that the total execution time reflects the sleep delays.
- [ ] Write a unit test for a **persistent failure** scenario:
  - [ ] Mock the provider's `create_completion` method to fail on all attempts with a rate limit error.
  - [ ] Assert that a `RuntimeError` is raised after all retries are exhausted.
  - [ ] Assert that the API call count is correct (e.g., `1` initial + `LLM_RETRY_COUNT` retries).

## Phase 4: Documentation

- [ ] Update `aicoder/.env.example` to include the new retry configuration variables (commented out as examples).
- [ ] Update `config/README.md` with a new section explaining the linear backoff feature and how the configuration parameters (`LLM_RETRY_COUNT`, etc.) work.

## Final Review

- [ ] All code changes are implemented as per the plan.
- [ ] All new and existing unit tests pass.
- [ ] The code has been linted and formatted.
- [ ] Documentation has been updated.
- [ ] The changes are committed to version control.
