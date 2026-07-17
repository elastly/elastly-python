# StageRecordsRequestOneOf1RecordsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**external_id** | **str** |  | 
**segment** | **str** |  | [optional] 
**region** | **str** |  | [optional] 
**country** | **str** |  | [optional] 
**credit_terms** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**is_active** | **bool** |  | [optional] 
**attributes** | **Dict[str, object]** |  | [optional] 

## Example

```python
from elastly.models.stage_records_request_one_of1_records_inner import StageRecordsRequestOneOf1RecordsInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf1RecordsInner from a JSON string
stage_records_request_one_of1_records_inner_instance = StageRecordsRequestOneOf1RecordsInner.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf1RecordsInner.to_json())

# convert the object into a dict
stage_records_request_one_of1_records_inner_dict = stage_records_request_one_of1_records_inner_instance.to_dict()
# create an instance of StageRecordsRequestOneOf1RecordsInner from a dict
stage_records_request_one_of1_records_inner_from_dict = StageRecordsRequestOneOf1RecordsInner.from_dict(stage_records_request_one_of1_records_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


