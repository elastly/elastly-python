# Elastly Python SDK

The official Python client for the [Elastly](https://elastly.io) REST API.

Elastly prices quote and order lines for B2B sellers. Send a line (product, customer, quantity) and get back a price with the reasoning behind it: which pricing rules fired, what each one added, and how confident the engine is. The engine learns from the outcomes you feed back, so prices improve over time.

This client covers the full v1 API:

- **Prices**: price up to 100 lines in one call.
- **Ingest**: push products, customers, quotes, and orders from your own system in staged batches.
- **Write-backs**: pull approved price changes into your system and confirm them once applied.

## Install

```bash
pip install elastly
```

Requires Python 3.9 or newer.

## Authenticate

Create an API key in the dashboard (Settings, then API keys). Keys are scoped: an `erp` key prices lines, a `connector` key ingests data and claims write-backs. Send the key as a bearer token.

## Price a line

```python
import uuid

import elastly

configuration = elastly.Configuration(access_token="elastly_live_...")

with elastly.ApiClient(configuration) as api_client:
    prices = elastly.PricesApi(api_client)

    response = prices.get_prices(
        idempotency_key=str(uuid.uuid4()),
        prices_request=elastly.PricesRequest(
            lines=[
                elastly.PricesRequestLinesInner(
                    product_sku="SKU-1042",
                    customer_external_id="CUST-88",
                    quantity=25,
                )
            ]
        ),
    )

    for line in response.lines:
        result = line.actual_instance
        if result.ok:
            print(result.price_cents, result.currency, result.reason_summary)
        else:
            print("failed:", result.code, result.message)
```

Every response line is either a priced result (`ok` is true) or a per-line error. One bad line never fails the batch.

## Retries and idempotency

`POST /v1/prices` requires an `Idempotency-Key` header. Use a fresh key for each logical request and reuse the same key on retries. A replay returns the stored response, so a retried call never prices twice.

## Close the loop

Elastly learns from the difference between the price it recommended and the price your team actually charged. When you ingest quotes, echo the `pricingDecisionId` you received from the prices call on the matching quote line. Skip that and the engine has nothing to learn from.

## Documentation

- [API reference](https://elastly.io/docs/api)
- Per-endpoint docs for this client live in [docs](./docs).

## About this repository

This code is generated from the Elastly OpenAPI contract, so pull requests against generated files get overwritten by the next release. If something is broken or missing, open an issue or email support@elastly.io.

## License

[MIT](./LICENSE)
