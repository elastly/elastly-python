# StageRecordsRequestOneOfRecordsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sku** | **str** |  | 
**external_id** | **str** |  | [optional] 
**name** | **str** |  | 
**category** | **str** |  | 
**cost_cents** | **int** |  | 
**current_price_cents** | **int** |  | 
**map_cents** | **int** |  | [optional] 
**floor_cents** | **int** |  | [optional] 
**ceiling_cents** | **int** |  | [optional] 
**is_active** | **bool** |  | [optional] 
**in_stock** | **bool** |  | [optional] 
**stock_on_hand** | **int** |  | [optional] 
**brand** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**attributes** | **Dict[str, object]** |  | [optional] 

## Example

```python
from elastly.models.stage_records_request_one_of_records_inner import StageRecordsRequestOneOfRecordsInner

# TODO update the JSON string below
json = "{}"
# create an instance of StageRecordsRequestOneOfRecordsInner from a JSON string
stage_records_request_one_of_records_inner_instance = StageRecordsRequestOneOfRecordsInner.from_json(json)
# print the JSON string representation of the object
print(StageRecordsRequestOneOfRecordsInner.to_json())

# convert the object into a dict
stage_records_request_one_of_records_inner_dict = stage_records_request_one_of_records_inner_instance.to_dict()
# create an instance of StageRecordsRequestOneOfRecordsInner from a dict
stage_records_request_one_of_records_inner_from_dict = StageRecordsRequestOneOfRecordsInner.from_dict(stage_records_request_one_of_records_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


