# StageRecordsRequestOneOf


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity** | **str** |  | 
**records** | [**List[StageRecordsRequestOneOfRecordsInner]**](StageRecordsRequestOneOfRecordsInner.md) |  | 

## Example

```python
from elastly.models.stage_records_request_one_of import StageRecordsRequestOneOf

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOf from a JSON string
stage_records_request_one_of_instance = StageRecordsRequestOneOf.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOf.to_json())

# convert the object into a dict
stage_records_request_one_of_dict = stage_records_request_one_of_instance.to_dict()
# create an instance of StageRecordsRequestOneOf from a dict
stage_records_request_one_of_from_dict = StageRecordsRequestOneOf.from_dict(stage_records_request_one_of_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


