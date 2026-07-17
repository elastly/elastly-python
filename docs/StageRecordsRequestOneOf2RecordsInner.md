# StageRecordsRequestOneOf2RecordsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**external_id** | **str** |  | 
**customer_external_id** | **str** |  | 
**outcome** | **str** |  | 
**currency** | **str** |  | [optional] 
**exchange_rate** | **float** |  | [optional] 
**created_at** | **datetime** |  | 
**decided_at** | **datetime** |  | [optional] 
**lost_reason** | **str** |  | [optional] 
**lines** | [**List[StageRecordsRequestOneOf2RecordsInnerLinesInner]**](StageRecordsRequestOneOf2RecordsInnerLinesInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request_one_of2_records_inner import StageRecordsRequestOneOf2RecordsInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf2RecordsInner from a JSON string
stage_records_request_one_of2_records_inner_instance = StageRecordsRequestOneOf2RecordsInner.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf2RecordsInner.to_json())

# convert the object into a dict
stage_records_request_one_of2_records_inner_dict = stage_records_request_one_of2_records_inner_instance.to_dict()
# create an instance of StageRecordsRequestOneOf2RecordsInner from a dict
stage_records_request_one_of2_records_inner_from_dict = StageRecordsRequestOneOf2RecordsInner.from_dict(stage_records_request_one_of2_records_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


