# PricesRequestLinesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**customer_id** | **str** |  | [optional] 
**customer_external_id** | **str** |  | [optional] 
**product_sku** | **str** |  | [optional] 
**product_external_id** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] [default to 1]
**order_value_cents** | **int** |  | [optional] 
**order_total_quantity** | **int** |  | [optional] 
**urgency** | **str** |  | [optional] 

## Example

```python
from elastly.models.prices_request_lines_inner import PricesRequestLinesInner

# TODO update the JSON string below
json = "{}"
# create an instance of PricesRequestLinesInner from a JSON string
prices_request_lines_inner_instance = PricesRequestLinesInner.from_json(json)
# print the JSON string representation of the object
print(PricesRequestLinesInner.to_json())

# convert the object into a dict
prices_request_lines_inner_dict = prices_request_lines_inner_instance.to_dict()
# create an instance of PricesRequestLinesInner from a dict
prices_request_lines_inner_from_dict = PricesRequestLinesInner.from_dict(prices_request_lines_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


