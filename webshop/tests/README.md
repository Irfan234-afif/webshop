# Webshop Unit Tests

This directory contains unit tests for the Webshop application.

## Test Structure

Existing tests are located in `webshop/tests/`. To ensure a reliable testing environment, we use a custom base class `WebshopTestCase` defined in `webshop/tests/test_base.py`.

### WebshopTestCase

`WebshopTestCase` inherits from `frappe.tests.utils.FrappeTestCase` and automatically handles the setup of complex ERPNext dependencies that are often missing in a clean test site.

**What it sets up:**

- **Company**: Creates `_Test Company` with default currency and settings.
- **Accounting**: Fixes Account Types for `Debtors` (Receivable) and `Creditors` (Payable) to pass Journal Entry validation.
- **Stock**: Creates all standard `Stock Entry Type` records (Material Receipt, Repack, etc.) and a default Warehouse.
- **Cleanup**: Automatically wipes conflicting `Item Price` and `Tax Rule` records before running tests to prevent `DuplicateEntryError`.

## How to Write New Tests

To create a new test file, simply inherit from `WebshopTestCase`:

```python
from webshop.tests.test_base import WebshopTestCase

class TestMyFeature(WebshopTestCase):
    def test_something(self):
        # Your test logic here
        pass
```

You do **NOT** need to run any manual setup scripts or `bench execute` commands. The base class handles everything in `setUpClass`.

## Running Tests

Run tests using the standard bench command:

```bash
bench --site test.localhost run-tests --app webshop --module webshop.tests.test_auth
```

Or run all webshop tests:

```bash
bench --site test.localhost run-tests --app webshop
```
