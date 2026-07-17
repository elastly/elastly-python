# PricesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**lines** | [**List[PricesRequestLinesInner]**](PricesRequestLinesInner.md) |  | 

## Example

```python
from elastly.models.prices_request import PricesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PricesRequest from a JSON string
prices_request_instance = PricesRequest.from_json(json)
# print the JSON string representation of the object
print(PricesRequest.to_json())

# convert the object into a dict
prices_request_dict = prices_request_instance.to_dict()
# create an instance of PricesRequest from a dict
prices_request_from_dict = PricesRequest.from_dict(prices_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


