import json
from lib_common.network import HttpResponse


def test_response_json_and_status():
    response = HttpResponse(status_code=200, text='{"ok": true}', headers={})
    assert response.json() == {"ok": True}
    assert response.ok
