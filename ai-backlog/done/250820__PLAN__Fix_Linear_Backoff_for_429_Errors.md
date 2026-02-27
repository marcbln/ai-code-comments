# Implementation Plan: Fix Linear Backoff for 429 Errors

This plan details the necessary steps to correct the retry logic for HTTP 429 "Too Many Requests" errors originating from the OpenRouter API.

## Phase 1: Analysis and Objective

### Current Problem
The retry mechanism in `aicoder/llm/api_client.py` is designed to catch `requests.exceptions.HTTPError` for rate-limiting errors. However, the `OpenRouterApiAdapter` in `aicoder/llm/providers/openrouter.py` catches this specific error and wraps it in a generic `RuntimeError`. This prevents the `LLMClient` from identifying the error as a retryable rate-limit issue, causing it to fail immediately.

### Objective
Modify the error handling in `aicoder/llm/providers/openrouter.py` to allow `requests.exceptions.HTTPError` to propagate up to the `LLMClient`, enabling the existing linear backoff retry logic to function as intended.

---

## Phase 2: Modify the OpenRouter API Adapter

The core task is to adjust the `try...except` block within the `create_completion` method of the `OpenRouterApiAdapter`.

**File to modify:** `aicoder/llm/providers/openrouter.py`

**Instructions:**

1.  Locate the `create_completion` method.
2.  Replace the existing method with the updated version below. The key change is to specifically catch and re-raise `requests.exceptions.HTTPError` while continuing to wrap other, non-retryable exceptions.

**Current Code (`create_completion` method):**
```python
    def create_completion(self, model: str, messages: list, verbose: bool = False) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        try:
            data, headers = self.build_request(model, messages)
            headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })

            if verbose:
                print(f"Making request to OpenRouter API with model: {model}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            response_json = response.json()
            if 'choices' not in response_json:
                raise RuntimeError(f"OpenRouter API error: 'choices' key missing in response. Full response: {response_json}")
            return response_json['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenRouter API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {str(e)}")
```

**New Code (`create_completion` method):**
```python
    def create_completion(self, model: str, messages: list, verbose: bool = False) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        data, headers = self.build_request(model, messages)
        headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })

        if verbose:
            print(f"Making request to OpenRouter API with model: {model}")

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            response_json = response.json()
            if 'choices' not in response_json:
                raise RuntimeError(f"OpenRouter API error: 'choices' key missing in response. Full response: {response_json}")
            return response_json['choices'][0]['message']['content']

        except requests.exceptions.HTTPError:
            # Re-raise HTTPError to allow the LLMClient's retry logic to catch it.
            raise
        except requests.exceptions.RequestException as e:
            # Wrap other network-related errors (e.g., timeout, connection error).
            raise RuntimeError(f"OpenRouter API request failed with a network error: {str(e)}") from e
        except Exception as e:
            # Wrap other unexpected errors (e.g., JSON parsing).
            raise RuntimeError(f"OpenRouter API error during response processing: {str(e)}") from e
```

### Rationale for Change
This new structure correctly distinguishes between retryable HTTP errors (which are passed up to the client) and other unexpected network or processing errors (which are wrapped in a `RuntimeError` and treated as non-retryable).

---

## Phase 3: Verification and Testing

To ensure the fix is working correctly and has not introduced regressions, run the existing unit test suite. The tests in `tests/test_api_client_retries.py` are designed to simulate `HTTPError` scenarios and will validate the fix.

**Instructions:**

1.  Navigate to the root directory of the project.
2.  Execute the following command to run all unit tests:

    ```bash
    python -m unittest discover tests
    ```

**Expected Outcome:**
All tests in `tests/test_api_client_retries.py` should pass. This confirms that:
-   `HTTPError` with status code 429 now correctly triggers the retry logic.
-   `HTTPError` with other status codes (e.g., 500) are correctly treated as non-retryable.
-   The client correctly exhausts all retries before failing on persistent 429 errors.

---

## Phase 4: Final Review

Complete the following checklist to confirm the successful implementation of the plan.

- [ ] **Code Change:** The `create_completion` method in `aicoder/llm/providers/openrouter.py` has been updated as specified in Phase 2.
- [ ] **Testing:** All unit tests pass successfully after running the command from Phase 3.
- [ ] **Code Quality:** The code remains clean, formatted, and free of linting errors.
- [ ] **Functionality:** The primary objective of enabling linear backoff for 429 errors has been achieved.


