# PricesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**lines** | [**List[PricesResponseLinesInner]**](PricesResponseLinesInner.md) |  | 

## Example

```python
from elastly.models.prices_response import PricesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PricesResponse from a JSON string
prices_response_instance = PricesResponse.from_json(json)
# print the JSON string representation of the object
print(PricesResponse.to_json())

# convert the object into a dict
prices_response_dict = prices_response_instance.to_dict()
# create an instance of PricesResponse from a dict
prices_response_from_dict = PricesResponse.from_dict(prices_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


