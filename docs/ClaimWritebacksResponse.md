# ClaimWritebacksResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tasks** | [**List[ClaimWritebacksResponseTasksInner]**](ClaimWritebacksResponseTasksInner.md) |  | 

## Example

```python
from elastly.models.claim_writebacks_response import ClaimWritebacksResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ClaimWritebacksResponse from a JSON string
claim_writebacks_response_instance = ClaimWritebacksResponse.from_json(json)
# print the JSON string representation of the object
print(ClaimWritebacksResponse.to_json())

# convert the object into a dict
claim_writebacks_response_dict = claim_writebacks_response_instance.to_dict()
# create an instance of ClaimWritebacksResponse from a dict
claim_writebacks_response_from_dict = ClaimWritebacksResponse.from_dict(claim_writebacks_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


