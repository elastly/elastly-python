# BatchStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | 
**entities** | **List[str]** |  | 
**record_count** | **int** |  | 
**skipped_over_cap** | **int** |  | 
**error** | **str** |  | 

## Example

```python
from elastly.models.batch_status_response import BatchStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BatchStatusResponse from a JSON string
batch_status_response_instance = BatchStatusResponse.from_json(json)
# print the JSON string representation of the object
print(BatchStatusResponse.to_json())

# convert the object into a dict
batch_status_response_dict = batch_status_response_instance.to_dict()
# create an instance of BatchStatusResponse from a dict
batch_status_response_from_dict = BatchStatusResponse.from_dict(batch_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


