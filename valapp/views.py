import datetime
import xml.etree.cElementTree as ET

from django.http import JsonResponse
import requests


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
    date_one = datetime.datetime.strptime(date_one, '%Y-%m-%d').strftime('%d/%m/%Y')
    date_two = datetime.datetime.strptime(date_two, '%Y-%m-%d').strftime('%d/%m/%Y')

    data_one = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params={'date_req': date_one}).text
    data_two = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params={'date_req': date_two}).text

    value_one = value_two = ''

    root_one = ET.fromstring(data_one)
    for valute in root_one.findall('Valute'):
        if valute.find('CharCode').text == val:
            value_one = float(valute.find('Value').text.replace(',', '.'))
            break

    root_two = ET.fromstring(data_two)
    for valute in root_two.findall('Valute'):
        if valute.find('CharCode').text == val:
            value_two = float(valute.find('Value').text.replace(',', '.'))
            break

    response = {date_one: value_one, date_two: value_two, 'difference': round((value_one - value_two), 4)}

    return JsonResponse(response)
