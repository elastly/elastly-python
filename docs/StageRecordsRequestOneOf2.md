# StageRecordsRequestOneOf2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity** | **str** |  | 
**records** | [**List[StageRecordsRequestOneOf2RecordsInner]**](StageRecordsRequestOneOf2RecordsInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request_one_of2 import StageRecordsRequestOneOf2

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf2 from a JSON string
stage_records_request_one_of2_instance = StageRecordsRequestOneOf2.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf2.to_json())

# convert the object into a dict
stage_records_request_one_of2_dict = stage_records_request_one_of2_instance.to_dict()
# create an instance of StageRecordsRequestOneOf2 from a dict
stage_records_request_one_of2_from_dict = StageRecordsRequestOneOf2.from_dict(stage_records_request_one_of2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


