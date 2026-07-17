# StageRecordsRequestOneOf3RecordsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**external_id** | **str** |  | 
**customer_external_id** | **str** |  | [optional] 
**source_quote_external_id** | **str** |  | [optional] 
**currency** | **str** |  | 
**exchange_rate** | **float** |  | [optional] 
**sold_at** | **datetime** |  | 
**lines** | [**List[StageRecordsRequestOneOf3RecordsInnerLinesInner]**](StageRecordsRequestOneOf3RecordsInnerLinesInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request_one_of3_records_inner import StageRecordsRequestOneOf3RecordsInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf3RecordsInner from a JSON string
stage_records_request_one_of3_records_inner_instance = StageRecordsRequestOneOf3RecordsInner.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf3RecordsInner.to_json())

# convert the object into a dict
stage_records_request_one_of3_records_inner_dict = stage_records_request_one_of3_records_inner_instance.to_dict()
# create an instance of StageRecordsRequestOneOf3RecordsInner from a dict
stage_records_request_one_of3_records_inner_from_dict = StageRecordsRequestOneOf3RecordsInner.from_dict(stage_records_request_one_of3_records_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


