import pytest

@pytest.fixture
def create_recurring_transaction(client, auth_headers, create_accounts, create_category):
    usd_account = create_accounts["USD"]
    category = create_category
