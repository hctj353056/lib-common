import json
import pytest
from lib_common import utils


def test_chunks_validates_size():
    assert utils.chunks([1, 2, 3], 2) == [[1, 2], [3]]
    with pytest.raises(ValueError):
        utils.chunks([1], 0)


def test_atomic_json_roundtrip(tmp_path):
    path = tmp_path / "data.json"
    utils.save_json({"中文": 1}, str(path))
    assert json.loads(path.read_text(encoding="utf-8")) == {"中文": 1}
