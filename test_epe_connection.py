import pytest
import requests
from mock_result import _mock_result_geojson, _mock_result_kmz
import epe_connection
from epe_connection import build_url, save_kmz, URL, HEADERS, make_params, make_request, retrieve_file

from urllib import parse
import json


@pytest.mark.skip("Integration")
@pytest.mark.parametrize('layer', (
        (20,)
))
def test_get_connection(layer):
    resp = requests.get(URL, headers=HEADERS, verify=False)
    assert resp.status_code == 200


@pytest.mark.parametrize('url, layer, fmt', (
    (URL, 20, 'geojson'),
    (URL, 1, 'geojson'),
))
def test_build_url(url, layer, fmt):
    url = build_url(url, layer)
    assert url == f'https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WMS_Webmap_EPE/MapServer/{layer}/query?where=1%3D1&outFields=%2A&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&having=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentOnly=false&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f={fmt}'


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


def get_mock(url, headers, verify=False):
    return ResponseMock(url)


@pytest.mark.parametrize('layer, fmt, expected',(
    (1, 'kmz', bytes),
    (1, 'geojson', str)
))
def test_make_request(layer, fmt, expected):
    """
    QUANDO é feito um request.get para a API
    DADO o pamâmetro f (formato
    ENTÃO ela deve regornar o content no formato especificado
    :param layer: id da layer
    :param fmt: formato do arqivo "gejson" ou "kmz"
    :return:
    """
    #Setup
    epe_connection.requests.get = get_mock
    url = build_url(URL, layer, fmt)
    resp = make_request(url)

    assert isinstance(resp.content, expected)


@pytest.mark.parametrize('layer_id, layer_name, fmt', (
        (0, '0layer0', 'geojson'),
        (0, '0layer0', 'kmz'),
        (1, '1layer1', 'geojson'),
        (1, '1layer1', 'kmz')
))
def test_retrieve_file(layer_id, layer_name, fmt):
    #Setup
    epe_connection.requests.get = get_mock

    resp = retrieve_file(URL, layer_name, layer_id, fmt)
    assert isinstance(resp, int)

