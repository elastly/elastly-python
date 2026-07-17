# StageRecordsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity** | **str** |  | 
**records** | [**List[StageRecordsRequestOneOf3RecordsInner]**](StageRecordsRequestOneOf3RecordsInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request import StageRecordsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequest from a JSON string
stage_records_request_instance = StageRecordsRequest.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequest.to_json())

# convert the object into a dict
stage_records_request_dict = stage_records_request_instance.to_dict()
# create an instance of StageRecordsRequest from a dict
stage_records_request_from_dict = StageRecordsRequest.from_dict(stage_records_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


