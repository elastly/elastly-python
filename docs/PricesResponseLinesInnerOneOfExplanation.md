# PricesResponseLinesInnerOneOfExplanation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**short** | **str** |  | 
**drivers** | [**List[PricesResponseLinesInnerOneOfExplanationDriversInner]**](PricesResponseLinesInnerOneOfExplanationDriversInner.md) |  | 
**stance** | **str** |  | 
**margin_pct** | **float** |  | 
**target_margin_pct** | **float** |  | 
**confidence** | **str** |  | 

## Example

```python
from elastly.models.prices_response_lines_inner_one_of_explanation import PricesResponseLinesInnerOneOfExplanation

# TODO update the JSON string below
json = "{}"
# create an instance of PricesResponseLinesInnerOneOfExplanation from a JSON string
prices_response_lines_inner_one_of_explanation_instance = PricesResponseLinesInnerOneOfExplanation.from_json(json)
# print the JSON string representation of the object
print(PricesResponseLinesInnerOneOfExplanation.to_json())

# convert the object into a dict
prices_response_lines_inner_one_of_explanation_dict = prices_response_lines_inner_one_of_explanation_instance.to_dict()
# create an instance of PricesResponseLinesInnerOneOfExplanation from a dict
prices_response_lines_inner_one_of_explanation_from_dict = PricesResponseLinesInnerOneOfExplanation.from_dict(prices_response_lines_inner_one_of_explanation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


