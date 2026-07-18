import json

from elastly.connector import FileCheckpointStore, InMemoryCheckpointStore


def test_in_memory_store_round_trips_and_clears_cursors():
    store = InMemoryCheckpointStore()
    assert store.get("product") is None
    store.set("product", "42")
    assert store.get("product") == "42"
    store.set("product", None)
    assert store.get("product") is None


def test_file_store_persists_across_instances(tmp_path):
    path = tmp_path / "checkpoints.json"
    store = FileCheckpointStore(path)
    store.set("product", "7")
    store.set("quote", "2026-07-01T00:00:00Z")
    reopened = FileCheckpointStore(path)
    assert reopened.get("product") == "7"
    assert reopened.get("quote") == "2026-07-01T00:00:00Z"
    reopened.set("product", None)
    assert FileCheckpointStore(path).get("product") is None


def test_file_store_returns_none_when_the_file_does_not_exist(tmp_path):
    store = FileCheckpointStore(tmp_path / "missing" / "checkpoints.json")
    assert store.get("product") is None


def test_file_store_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "dir" / "checkpoints.json"
    FileCheckpointStore(path).set("product", "1")
    assert FileCheckpointStore(path).get("product") == "1"


def test_file_store_writes_atomically_leaving_no_temp_file(tmp_path):
    path = tmp_path / "checkpoints.json"
    FileCheckpointStore(path).set("product", "1")
    assert [p.name for p in tmp_path.iterdir()] == ["checkpoints.json"]


def test_file_store_ignores_non_object_json_and_non_string_values(tmp_path):
    path = tmp_path / "checkpoints.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    assert FileCheckpointStore(path).get("product") is None
    path.write_text(json.dumps({"product": "7", "junk": 3}), encoding="utf-8")
    store = FileCheckpointStore(path)
    assert store.get("product") == "7"
    assert store.get("junk") is None
