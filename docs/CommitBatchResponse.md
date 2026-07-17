# CommitBatchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** |  | 

## Example

```python
from elastly.models.commit_batch_response import CommitBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CommitBatchResponse from a JSON string
commit_batch_response_instance = CommitBatchResponse.from_json(json)
# print the JSON string representation of the object
print(CommitBatchResponse.to_json())

# convert the object into a dict
commit_batch_response_dict = commit_batch_response_instance.to_dict()
# create an instance of CommitBatchResponse from a dict
commit_batch_response_from_dict = CommitBatchResponse.from_dict(commit_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


