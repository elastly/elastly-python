# StageRecordsRequestOneOf3


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity** | **str** |  | 
**records** | [**List[StageRecordsRequestOneOf3RecordsInner]**](StageRecordsRequestOneOf3RecordsInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request_one_of3 import StageRecordsRequestOneOf3

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf3 from a JSON string
stage_records_request_one_of3_instance = StageRecordsRequestOneOf3.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf3.to_json())

# convert the object into a dict
stage_records_request_one_of3_dict = stage_records_request_one_of3_instance.to_dict()
# create an instance of StageRecordsRequestOneOf3 from a dict
stage_records_request_one_of3_from_dict = StageRecordsRequestOneOf3.from_dict(stage_records_request_one_of3_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


