import datetime
import xml.etree.cElementTree as ET

from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import requests


@cache_page(None)
def get_val_view(request):
    data = requests.get('http://www.cbr.ru/scripts/XML_valFull.asp').text
    root = ET.fromstring(data)

    response = {}

    for item in root.findall('Item'):
        char_code = item.find('ISO_Char_Code').text
        name = item.find('Name').text
        response[char_code] = name

    return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


def get_dif_view(request, val, date_one, date_two):
    today = datetime.datetime.today().date()

    try:
        date_one = datetime.datetime.strptime(date_one, '%Y-%m-%d').date()
        date_two = datetime.datetime.strptime(date_two, '%Y-%m-%d').date()
    except:
        response = {'Error': 'Incorrect date format, should be YYYY-MM-DD'}
        return JsonResponse(response)

    if date_one > today or date_two > today:
        response = {'Error': 'Incorrect date'}
        return JsonResponse(response)

    date_one = date_one.strftime('%d/%m/%Y')
    date_two = date_two.strftime('%d/%m/%Y')

    data_one = cache.get(date_one)
    if not data_one:
        data_one = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params={'date_req': date_one}).text
        cache.set(date_one, data_one, 86400)

    data_two = cache.get(date_two)
    if not data_two:
        data_two = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params={'date_req': date_two}).text
        cache.set(date_two, data_two, 86400)

    value_one = value_two = 0

    root_one = ET.fromstring(data_one)
    for valute in root_one.findall('Valute'):
        if valute.find('CharCode').text == val:
            value_one = float(valute.find('Value').text.replace(',', '.'))
            break

    if value_one == 0:
        response = {'Error': 'Incorrect valute code'}
        return JsonResponse(response)

    root_two = ET.fromstring(data_two)
    for valute in root_two.findall('Valute'):
        if valute.find('CharCode').text == val:
            value_two = float(valute.find('Value').text.replace(',', '.'))
            break

    response = {'Valute': val, date_one: value_one, date_two: value_two, 'difference': round((value_one - value_two), 4)}

    return JsonResponse(response)
