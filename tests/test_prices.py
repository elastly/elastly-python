import json

from elastly import (
    ApiClient,
    Configuration,
    IngestApi,
    PricesApi,
    PricesRequest,
    PricesRequestLinesInner,
    PricesResponse,
    WritebacksApi,
)
from elastly.models.prices_response_lines_inner_one_of import PricesResponseLinesInnerOneOf
from elastly.models.prices_response_lines_inner_one_of1 import PricesResponseLinesInnerOneOf1

# Canonical GET /v1/prices 200 body: one priced line and one failed line.
CANONICAL_PRICES_200_BODY = """
{"lines":[
 {"ok":true,"priceCents":1299,"currency":"USD","pricingDecisionId":"pd-A","reason":[{"param":"base","marginDeltaBps":120}],"reasonSummary":"Base margin","explanation":{"short":"held","drivers":[{"param":"base","label":"Base","points":1.2,"direction":"up"}],"stance":"standard","marginPct":18.5,"targetMarginPct":19,"confidence":"high"},"guardrailsApplied":[],"confidence":"high","confidenceScore":0.91},
 {"ok":false,"code":"unknown_product","message":"Unknown product."}
]}
"""


def test_prices_response_resolves_priced_and_error_variants():
    # REGRESSION GUARD: `ok` is a boolean `const` discriminator. An earlier
    # contract bug stringified it ("true"/"false"), which made every /v1/prices
    # line fail to deserialize into its oneOf variant. This asserts the two
    # variants resolve from real JSON booleans so that class of bug cannot
    # return silently.
    response = PricesResponse.from_json(CANONICAL_PRICES_200_BODY)

    assert len(response.lines) == 2

    priced = response.lines[0].actual_instance
    assert isinstance(priced, PricesResponseLinesInnerOneOf)
    assert priced.ok is True
    assert priced.price_cents == 1299
    assert priced.currency == "USD"
    assert priced.pricing_decision_id == "pd-A"

    error = response.lines[1].actual_instance
    assert isinstance(error, PricesResponseLinesInnerOneOf1)
    assert error.ok is False
    assert error.code == "unknown_product"
    assert error.message == "Unknown product."


def test_prices_request_serializes_line_fields():
    request = PricesRequest(lines=[PricesRequestLinesInner(product_sku="SKU-1", quantity=25)])

    payload = json.loads(request.to_json())
    line = payload["lines"][0]
    assert line["productSku"] == "SKU-1"
    assert line["quantity"] == 25

    round_tripped = PricesRequest.from_json(request.to_json())
    assert round_tripped.lines[0].product_sku == "SKU-1"
    assert round_tripped.lines[0].quantity == 25


def test_api_classes_construct_with_configuration_access_token():
    configuration = Configuration(access_token="elastly_live_testtoken")
    client = ApiClient(configuration)

    prices = PricesApi(client)
    ingest = IngestApi(client)
    writebacks = WritebacksApi(client)

    for api in (prices, ingest, writebacks):
        assert api.api_client is client
        assert api.api_client.configuration.access_token == "elastly_live_testtoken"

    assert configuration.auth_settings()["apiKey"]["value"] == "Bearer elastly_live_testtoken"
