# BatchCreatedResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batch_id** | **str** |  | 
**connector_id** | **str** |  | 

## Example

```python
from elastly.models.batch_created_response import BatchCreatedResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BatchCreatedResponse from a JSON string
batch_created_response_instance = BatchCreatedResponse.from_json(json)
# print the JSON string representation of the object
print(BatchCreatedResponse.to_json())

# convert the object into a dict
batch_created_response_dict = batch_created_response_instance.to_dict()
# create an instance of BatchCreatedResponse from a dict
batch_created_response_from_dict = BatchCreatedResponse.from_dict(batch_created_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


