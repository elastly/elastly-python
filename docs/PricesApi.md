# elastly.PricesApi

All URIs are relative to *https://app.elastly.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_prices**](PricesApi.md#get_prices) | **POST** /api/v1/prices | Price up to 100 lines in one idempotent call


# **get_prices**
> PricesResponse get_prices(idempotency_key, prices_request)

Price up to 100 lines in one idempotent call

Requires an erp-scope key. Every response line is either a priced output (ok: true) or a typed per-line error (ok: false); a single bad line never fails the batch.

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.prices_request import PricesRequest
from elastly.models.prices_response import PricesResponse
from elastly.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://app.elastly.io
# See configuration.py for a list of all supported configuration parameters.
configuration = elastly.Configuration(
    host = "https://app.elastly.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: apiKey
configuration = elastly.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with elastly.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = elastly.PricesApi(api_client)
    idempotency_key = 'idempotency_key_example' # str | Unique key for this logical request. Retries must reuse the same key; a replay returns the stored response.
    prices_request = elastly.PricesRequest() # PricesRequest | 

    try:
        # Price up to 100 lines in one idempotent call
        api_response = api_instance.get_prices(idempotency_key, prices_request)
        print("The response of PricesApi->get_prices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PricesApi->get_prices: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **idempotency_key** | **str**| Unique key for this logical request. Retries must reuse the same key; a replay returns the stored response. | 
 **prices_request** | [**PricesRequest**](PricesRequest.md)|  | 

### Return type

[**PricesResponse**](PricesResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Per-line results. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**409** | Error envelope with a stable machine-readable code. |  -  |
**422** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

