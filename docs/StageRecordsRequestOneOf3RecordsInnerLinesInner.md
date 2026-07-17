# StageRecordsRequestOneOf3RecordsInnerLinesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_sku** | **str** |  | 
**quantity** | **float** |  | 
**cost_cents** | **int** |  | 
**sold_price_cents** | **int** |  | 
**attributes** | **Dict[str, object]** |  | [optional] 

## Example

```python
from elastly.models.stage_records_request_one_of3_records_inner_lines_inner import StageRecordsRequestOneOf3RecordsInnerLinesInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf3RecordsInnerLinesInner from a JSON string
stage_records_request_one_of3_records_inner_lines_inner_instance = StageRecordsRequestOneOf3RecordsInnerLinesInner.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf3RecordsInnerLinesInner.to_json())

# convert the object into a dict
stage_records_request_one_of3_records_inner_lines_inner_dict = stage_records_request_one_of3_records_inner_lines_inner_instance.to_dict()
# create an instance of StageRecordsRequestOneOf3RecordsInnerLinesInner from a dict
stage_records_request_one_of3_records_inner_lines_inner_from_dict = StageRecordsRequestOneOf3RecordsInnerLinesInner.from_dict(stage_records_request_one_of3_records_inner_lines_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


