# WritebackAckRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[WritebackAckRequestResultsInner]**](WritebackAckRequestResultsInner.md) |  | 

## Example

```python
from elastly.models.writeback_ack_request import WritebackAckRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WritebackAckRequest from a JSON string
writeback_ack_request_instance = WritebackAckRequest.from_json(json)
# print the JSON string representation of the object
print(WritebackAckRequest.to_json())

# convert the object into a dict
writeback_ack_request_dict = writeback_ack_request_instance.to_dict()
# create an instance of WritebackAckRequest from a dict
writeback_ack_request_from_dict = WritebackAckRequest.from_dict(writeback_ack_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


