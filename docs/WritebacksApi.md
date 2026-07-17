# elastly.WritebacksApi

All URIs are relative to *https://app.elastly.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ack_writebacks**](WritebacksApi.md#ack_writebacks) | **POST** /api/v1/writebacks/ack | Acknowledge applied or failed write-backs
[**claim_writebacks**](WritebacksApi.md#claim_writebacks) | **POST** /api/v1/writebacks/claim | Lease pending price write-backs for this connector


# **ack_writebacks**
> AckWritebacksResponse ack_writebacks(writeback_ack_request)

Acknowledge applied or failed write-backs

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.ack_writebacks_response import AckWritebacksResponse
from elastly.models.writeback_ack_request import WritebackAckRequest
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
    api_instance = elastly.WritebacksApi(api_client)
    writeback_ack_request = elastly.WritebackAckRequest() # WritebackAckRequest | 

    try:
        # Acknowledge applied or failed write-backs
        api_response = api_instance.ack_writebacks(writeback_ack_request)
        print("The response of WritebacksApi->ack_writebacks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WritebacksApi->ack_writebacks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **writeback_ack_request** | [**WritebackAckRequest**](WritebackAckRequest.md)|  | 

### Return type

[**AckWritebacksResponse**](AckWritebacksResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ack outcome. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**422** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **claim_writebacks**
> ClaimWritebacksResponse claim_writebacks(claim_writebacks_request=claim_writebacks_request)

Lease pending price write-backs for this connector

Requires a connector-scope key. Each task carries leaseUntil; acks after the lease are counted as expired, never applied.

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.claim_writebacks_request import ClaimWritebacksRequest
from elastly.models.claim_writebacks_response import ClaimWritebacksResponse
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
    api_instance = elastly.WritebacksApi(api_client)
    claim_writebacks_request = elastly.ClaimWritebacksRequest() # ClaimWritebacksRequest |  (optional)

    try:
        # Lease pending price write-backs for this connector
        api_response = api_instance.claim_writebacks(claim_writebacks_request=claim_writebacks_request)
        print("The response of WritebacksApi->claim_writebacks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WritebacksApi->claim_writebacks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_writebacks_request** | [**ClaimWritebacksRequest**](ClaimWritebacksRequest.md)|  | [optional] 

### Return type

[**ClaimWritebacksResponse**](ClaimWritebacksResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Leased tasks. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

