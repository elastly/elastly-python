# AckWritebacksResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied** | **int** |  | 
**failed** | **int** |  | 
**expired** | **int** |  | 

## Example

```python
from elastly.models.ack_writebacks_response import AckWritebacksResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AckWritebacksResponse from a JSON string
ack_writebacks_response_instance = AckWritebacksResponse.from_json(json)
# print the JSON string representation of the object
print(AckWritebacksResponse.to_json())

# convert the object into a dict
ack_writebacks_response_dict = ack_writebacks_response_instance.to_dict()
# create an instance of AckWritebacksResponse from a dict
ack_writebacks_response_from_dict = AckWritebacksResponse.from_dict(ack_writebacks_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


