import httpx


def test_url():
    url_str = "http://127.0.0.1:1337/to/path?q=a#test"
    url = httpx.URL(url_str)
    assert url.netloc == b"127.0.0.1:1337"
    assert url.path == "/to/path"
    assert url.query == b"q=a"
    assert url.fragment == "test"
