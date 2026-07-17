# elastly.IngestApi

All URIs are relative to *https://app.elastly.io*

Method | HTTP request | Description
------------- | ------------- | -------------
[**commit_ingest_batch**](IngestApi.md#commit_ingest_batch) | **POST** /api/v1/ingest/batches/{batchId}/commit | Commit a batch; the sync engine drains it
[**create_ingest_batch**](IngestApi.md#create_ingest_batch) | **POST** /api/v1/ingest/batches | Open a staged ingest batch
[**get_ingest_batch_status**](IngestApi.md#get_ingest_batch_status) | **GET** /api/v1/ingest/batches/{batchId} | Batch status, including skippedOverCap
[**stage_ingest_records**](IngestApi.md#stage_ingest_records) | **POST** /api/v1/ingest/batches/{batchId}/records | Stage up to 1000 canonical records into an open batch


# **commit_ingest_batch**
> CommitBatchResponse commit_ingest_batch(batch_id)

Commit a batch; the sync engine drains it

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.commit_batch_response import CommitBatchResponse
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
    api_instance = elastly.IngestApi(api_client)
    batch_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 

    try:
        # Commit a batch; the sync engine drains it
        api_response = api_instance.commit_ingest_batch(batch_id)
        print("The response of IngestApi->commit_ingest_batch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestApi->commit_ingest_batch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_id** | **UUID**|  | 

### Return type

[**CommitBatchResponse**](CommitBatchResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | The enqueued sync job. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**404** | Error envelope with a stable machine-readable code. |  -  |
**409** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_ingest_batch**
> BatchCreatedResponse create_ingest_batch()

Open a staged ingest batch

Requires a connector-scope key and a connected push connector.

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.batch_created_response import BatchCreatedResponse
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
    api_instance = elastly.IngestApi(api_client)

    try:
        # Open a staged ingest batch
        api_response = api_instance.create_ingest_batch()
        print("The response of IngestApi->create_ingest_batch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestApi->create_ingest_batch: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**BatchCreatedResponse**](BatchCreatedResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | The opened batch. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ingest_batch_status**
> BatchStatusResponse get_ingest_batch_status(batch_id)

Batch status, including skippedOverCap

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.batch_status_response import BatchStatusResponse
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
    api_instance = elastly.IngestApi(api_client)
    batch_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 

    try:
        # Batch status, including skippedOverCap
        api_response = api_instance.get_ingest_batch_status(batch_id)
        print("The response of IngestApi->get_ingest_batch_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestApi->get_ingest_batch_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_id** | **UUID**|  | 

### Return type

[**BatchStatusResponse**](BatchStatusResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Current status. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**404** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stage_ingest_records**
> StageRecordsResponse stage_ingest_records(batch_id, stage_records_request)

Stage up to 1000 canonical records into an open batch

### Example

* Bearer Authentication (apiKey):

```python
import elastly
from elastly.models.stage_records_request import StageRecordsRequest
from elastly.models.stage_records_response import StageRecordsResponse
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
    api_instance = elastly.IngestApi(api_client)
    batch_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID | 
    stage_records_request = elastly.StageRecordsRequest() # StageRecordsRequest | 

    try:
        # Stage up to 1000 canonical records into an open batch
        api_response = api_instance.stage_ingest_records(batch_id, stage_records_request)
        print("The response of IngestApi->stage_ingest_records:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestApi->stage_ingest_records: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_id** | **UUID**|  | 
 **stage_records_request** | [**StageRecordsRequest**](StageRecordsRequest.md)|  | 

### Return type

[**StageRecordsResponse**](StageRecordsResponse.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Records staged. |  -  |
**401** | Error envelope with a stable machine-readable code. |  -  |
**402** | Error envelope with a stable machine-readable code. |  -  |
**403** | Error envelope with a stable machine-readable code. |  -  |
**404** | Error envelope with a stable machine-readable code. |  -  |
**409** | Error envelope with a stable machine-readable code. |  -  |
**422** | Error envelope with a stable machine-readable code. |  -  |
**429** | Error envelope with a stable machine-readable code. |  -  |
**500** | Error envelope with a stable machine-readable code. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

