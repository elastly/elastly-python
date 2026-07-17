# PricesResponseLinesInnerOneOf1


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ok** | **bool** |  | 
**code** | **str** |  | [optional] [default to 'internal_error']
**message** | **str** |  | 
**param** | **str** |  | [optional] 

## Example

```python
from elastly.models.prices_response_lines_inner_one_of1 import PricesResponseLinesInnerOneOf1

# TODO update the JSON string below
json = "{}"
# create an instance of PricesResponseLinesInnerOneOf1 from a JSON string
prices_response_lines_inner_one_of1_instance = PricesResponseLinesInnerOneOf1.from_json(json)
# print the JSON string representation of the object
print(PricesResponseLinesInnerOneOf1.to_json())

# convert the object into a dict
prices_response_lines_inner_one_of1_dict = prices_response_lines_inner_one_of1_instance.to_dict()
# create an instance of PricesResponseLinesInnerOneOf1 from a dict
prices_response_lines_inner_one_of1_from_dict = PricesResponseLinesInnerOneOf1.from_dict(prices_response_lines_inner_one_of1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


