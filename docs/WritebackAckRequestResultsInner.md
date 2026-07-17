# WritebackAckRequestResultsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**ok** | **bool** |  | 
**error** | **str** |  | [optional] 

## Example

```python
from elastly.models.writeback_ack_request_results_inner import WritebackAckRequestResultsInner

# TODO update the JSON string below
json = "{}"
# create an instance of WritebackAckRequestResultsInner from a JSON string
writeback_ack_request_results_inner_instance = WritebackAckRequestResultsInner.from_json(json)
# print the JSON string representation of the object
print(WritebackAckRequestResultsInner.to_json())

# convert the object into a dict
writeback_ack_request_results_inner_dict = writeback_ack_request_results_inner_instance.to_dict()
# create an instance of WritebackAckRequestResultsInner from a dict
writeback_ack_request_results_inner_from_dict = WritebackAckRequestResultsInner.from_dict(writeback_ack_request_results_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


