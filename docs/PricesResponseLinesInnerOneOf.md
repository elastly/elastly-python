# PricesResponseLinesInnerOneOf


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

## Example

```python
from elastly.models.prices_response_lines_inner_one_of import PricesResponseLinesInnerOneOf

# TODO update the JSON string below
json = "{}"
# create an instance of PricesResponseLinesInnerOneOf from a JSON string
prices_response_lines_inner_one_of_instance = PricesResponseLinesInnerOneOf.from_json(json)
# print the JSON string representation of the object
print(PricesResponseLinesInnerOneOf.to_json())

# convert the object into a dict
prices_response_lines_inner_one_of_dict = prices_response_lines_inner_one_of_instance.to_dict()
# create an instance of PricesResponseLinesInnerOneOf from a dict
prices_response_lines_inner_one_of_from_dict = PricesResponseLinesInnerOneOf.from_dict(prices_response_lines_inner_one_of_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


