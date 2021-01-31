import json
from urllib import parse
from mock_result import _mock_result_kmz, _mock_result_geojson


class ResponseMock:
    def __init__(self, url):
        self.status_code=200
        self.url = url
        self.fmt = self._set_fmt
        self.content = self._set_content

    def get(self, url, headers, verify):
        pass

    def json(self):
        return json.dumps(self.content)

    @property
    def _set_fmt(self):
        qs = parse.urlsplit(self.url)
        qs_dict = dict(parse.parse_qsl(qs.query))
        fmt = qs_dict['f']
        return fmt

    @property
    def _set_content(self):
        qs = parse.urlsplit(self.url)
        qs_dict = dict(parse.parse_qsl(qs.query))
        fmt = qs_dict['f']
        if fmt=='kmz':
            return _mock_result_kmz
        else:
            return _mock_result_geojson

