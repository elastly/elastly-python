# PricesResponseLinesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_cents** | **float** |  | 
**currency** | **str** |  | 
**pricing_decision_id** | **str** |  | 
**reason** | [**List[PricesResponseLinesInnerOneOfReasonInner]**](PricesResponseLinesInnerOneOfReasonInner.md) |  | 
**reason_summary** | **str** |  | 
**explanation** | [**PricesResponseLinesInnerOneOfExplanation**](PricesResponseLinesInnerOneOfExplanation.md) |  | 
**guardrails_applied** | **List[str]** |  | 
**confidence** | **str** |  | 
**confidence_score** | **float** |  | 
**ok** | **bool** |  | 
**code** | **str** |  | [optional] [default to 'internal_error']
**message** | **str** |  | 
**param** | **str** |  | [optional] 

## Example

```python
from elastly.models.prices_response_lines_inner import PricesResponseLinesInner

# TODO update the JSON string below
json = "{}"
# create an instance of PricesResponseLinesInner from a JSON string
prices_response_lines_inner_instance = PricesResponseLinesInner.from_json(json)
# print the JSON string representation of the object
print(PricesResponseLinesInner.to_json())

# convert the object into a dict
prices_response_lines_inner_dict = prices_response_lines_inner_instance.to_dict()
# create an instance of PricesResponseLinesInner from a dict
prices_response_lines_inner_from_dict = PricesResponseLinesInner.from_dict(prices_response_lines_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


