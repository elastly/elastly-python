# StageRecordsRequestOneOf1


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity** | **str** |  | 
**records** | [**List[StageRecordsRequestOneOf1RecordsInner]**](StageRecordsRequestOneOf1RecordsInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request_one_of1 import StageRecordsRequestOneOf1

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf1 from a JSON string
stage_records_request_one_of1_instance = StageRecordsRequestOneOf1.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf1.to_json())

# convert the object into a dict
stage_records_request_one_of1_dict = stage_records_request_one_of1_instance.to_dict()
# create an instance of StageRecordsRequestOneOf1 from a dict
stage_records_request_one_of1_from_dict = StageRecordsRequestOneOf1.from_dict(stage_records_request_one_of1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


