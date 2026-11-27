from lib_common.ai import OpenAICompatible, Message, _normalize_messages


def test_message_normalization_accepts_string_and_dataclass():
    assert _normalize_messages("hello") == [{"role": "user", "content": "hello"}]
    assert _normalize_messages(Message("user", "hi")) == [{"role": "user", "content": "hi"}]


def test_chat_stream_yields_chunks_and_stream_chat_joins(monkeypatch):
    client = OpenAICompatible("https://example.test/v1", "test-key")
    monkeypatch.setattr(client, "_iter_stream", lambda endpoint, payload: iter(["A", "B"]))
    assert list(client.chat_stream("test-model", "hello")) == ["A", "B"]
    assert client.chat("test-model", "hello", stream=True) == "AB"
    client.close()
