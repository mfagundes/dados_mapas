import time

import requests
import json

from colorama import Fore, init
from slugify import slugify

from urllib.parse import urlencode

from lista_layers import LAYERS

init(autoreset=True)
URL = "https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WMS_Webmap_EPE/MapServer/{layer}/query?"
HEADERS = {
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, image/apng, */*;q=0.8, application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'gisepeprd2.epe.gov.br',
    'Referer': URL,
    'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}


def make_params(url, fmt='geojson'):
    params = dict(
        where="1=1",
        outFields="*",
        text='',
        objectIds='',
        time='',
        geometry='',
        geometryType='esriGeometryEnvelope',
        inSR='',
        spatialRel='esriSpatialRelIntersects',
        relationParam='',
        returnGeometry='true',
        returnTrueCurves='false',
        maxAllowableOffset='',
        geometryPrecision='',
        outSR='',
        having='',
        returnIdsOnly='false',
        returnCountOnly='false',
        orderByFields='',
        groupByFieldsForStatistics='',
        outStatistics='',
        returnZ='false',
        returnM='false',
        gdbVersion='',
        historicMoment='',
        returnDistinctValues='false',
        resultOffset='',
        resultRecordCount='',
        queryByDistance='',
        returnExtentOnly='false',
        datumTransformation='',
        parameterValues='',
        rangeValues='',
        quantizationParameters='',
        featureEncoding='esriDefault',
        f=fmt
    )

    return params


def build_url(url, layer, fmt='geojson'):
    """
    https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WMS_Webmap_EPE/MapServer/20/query?
    where=1%3D1
    &text=
    &objectIds=
    &time=
    &geometry=
    &geometryType=esriGeometryEnvelope
    &inSR=
    &spatialRel=esriSpatialRelIntersects
    &relationParam=
    &outFields=*
    &returnGeometry=true
    &returnTrueCurves=false
    &maxAllowableOffset=
    &geometryPrecision=
    &outSR=
    &having=
    &returnIdsOnly=false
    &returnCountOnly=false
    &orderByFields=
    &groupByFieldsForStatistics=
    &outStatistics=
    &returnZ=false
    &returnM=false
    &gdbVersion=
    &historicMoment=
    &returnDistinctValues=false
    &resultOffset=
    &resultRecordCount=
    &queryByDistance=
    &returnExtentOnly=false
    &datumTransformation=
    &parameterValues=
    &rangeValues=
    &quantizationParameters=
    &featureEncoding=esriDefault
    &f=geojson

    :return:
    """
    params = make_params(url, fmt)
    layer = str(layer)
    url = url.format(layer=layer)
    url += urlencode(params)
    return url


def make_request(url):
    headers = HEADERS
    resp = requests.get(url, headers=headers, verify=False)
    return resp


def retrieve_file(url, layer_name, layer_id, fmt):
    res = False
    # params = make_params(url, fmt)
    url = build_url(url, layer_id, fmt)
    resp = make_request(url)
    if fmt=='kmz':
        res = save_kmz(resp.content, layer_name)
    else:
        try:
            json_data = json.loads(resp.content)
            if 'error' not in json_data:
                res = save_geojson(json_data, layer_name)
            else:
                print(Fore.RED + f"Layer {layer_name} não é uma layer de dados {fmt}")
        except Exception:
            print("erro no json")
    # try:
    #     json_data = json.loads(resp.content)
    #     if 'error' not in json_data:
    #         res = save_geojson(json_data, layer_name)
    # except TypeError:
    #     res = save_kmz(resp.content, layer_name)
    return res


def save_kmz(file, layer_name):
    res = False
    save_ = False
    filename = slugify(layer_name)
    try:
        resp = json.loads(file)
        if 'error' in resp:
            raise TypeError
    except TypeError:
        print(Fore.RED + f"Layer {layer_name} não é um arquivo kmz válido")
        save_ = False
    except UnicodeDecodeError:
        save_ = True

    if save_ is True:
        with open(f'kmz/{filename}.kmz', 'wb') as f:
            res = f.write(file)


    return res


def save_geojson(file, layer_name):
    filename = slugify(layer_name)
    with open(f'geojson/{filename}.geojson', 'w') as f:
        res = f.write(json.dumps(file))
    return res



if __name__ == '__main__':
    layers = LAYERS

    for layer in layers:
        layer_name, layer_id = list(layer.items())[0]
        print(Fore.GREEN + layer_name, layer_id)
        for fmt in ['geojson', 'kmz']:
            retrieve_file(URL, layer_name, layer_id, fmt=fmt)
            time.sleep(10)
