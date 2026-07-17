# ClaimWritebacksResponseTasksInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**product_sku** | **str** |  | 
**product_external_id** | **str** |  | 
**price_cents** | **float** |  | 
**currency** | **str** |  | 
**exchange_rate_to_base** | **float** |  | [optional] 
**reason_summary** | **str** |  | [optional] 
**pricing_decision_id** | **str** |  | [optional] 
**lease_until** | **str** |  | 
**target** | **Dict[str, object]** |  | 

## Example

```python
from elastly.models.claim_writebacks_response_tasks_inner import ClaimWritebacksResponseTasksInner

# TODO update the JSON string below
json = "{}"
# create an instance of ClaimWritebacksResponseTasksInner from a JSON string
claim_writebacks_response_tasks_inner_instance = ClaimWritebacksResponseTasksInner.from_json(json)
# print the JSON string representation of the object
print(ClaimWritebacksResponseTasksInner.to_json())

# convert the object into a dict
claim_writebacks_response_tasks_inner_dict = claim_writebacks_response_tasks_inner_instance.to_dict()
# create an instance of ClaimWritebacksResponseTasksInner from a dict
claim_writebacks_response_tasks_inner_from_dict = ClaimWritebacksResponseTasksInner.from_dict(claim_writebacks_response_tasks_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


