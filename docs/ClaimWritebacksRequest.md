# ClaimWritebacksRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **int** |  | [optional] [default to 100]

## Example

```python
from elastly.models.claim_writebacks_request import ClaimWritebacksRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ClaimWritebacksRequest from a JSON string
claim_writebacks_request_instance = ClaimWritebacksRequest.from_json(json)
# print the JSON string representation of the object
print(ClaimWritebacksRequest.to_json())

# convert the object into a dict
claim_writebacks_request_dict = claim_writebacks_request_instance.to_dict()
# create an instance of ClaimWritebacksRequest from a dict
claim_writebacks_request_from_dict = ClaimWritebacksRequest.from_dict(claim_writebacks_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


