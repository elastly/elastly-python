# StageRecordsRequestOneOf2RecordsInnerLinesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_sku** | **str** |  | 
**quantity** | **float** |  | 
**cost_cents** | **int** |  | 
**quoted_price_cents** | **int** |  | 
**pricing_decision_id** | **str** |  | 
**elastly_quoted_price_cents** | **int** |  | [optional] 
**salesperson_price_reason** | **str** |  | [optional] 
**attributes** | **Dict[str, object]** |  | [optional] 

## Example

```python
from elastly.models.stage_records_request_one_of2_records_inner_lines_inner import StageRecordsRequestOneOf2RecordsInnerLinesInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf2RecordsInnerLinesInner from a JSON string
stage_records_request_one_of2_records_inner_lines_inner_instance = StageRecordsRequestOneOf2RecordsInnerLinesInner.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf2RecordsInnerLinesInner.to_json())

# convert the object into a dict
stage_records_request_one_of2_records_inner_lines_inner_dict = stage_records_request_one_of2_records_inner_lines_inner_instance.to_dict()
# create an instance of StageRecordsRequestOneOf2RecordsInnerLinesInner from a dict
stage_records_request_one_of2_records_inner_lines_inner_from_dict = StageRecordsRequestOneOf2RecordsInnerLinesInner.from_dict(stage_records_request_one_of2_records_inner_lines_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


