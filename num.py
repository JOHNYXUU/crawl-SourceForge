from requests.exceptions import RequestException as RE
from multiprocessing import Pool
from pyquery import PyQuery as pq
import requests
import json
import re
import os
from config import*
from time import perf_counter

translation = []

def get_page_text(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
        return None
    except RE:
        print('ERROR when requesting this page {}'.format(url))
        return  None

def get_translation_type(html):
    url_heads = []
    doc = pq(html)
    items = doc.find('#facet-natlanguage li').items()
    for item in items:
        if item.text() != 'More...':
            if item.text().split(' ')[1] == '(Simplified)':
                type = item.text().split(' ')[0].lower() + 'simplified'
            elif item.text().split(' ')[1] == '(Traditional)':
                type = item.text().split(' ')[0].lower() + 'traditional'
            elif 'Slovene' in item.text():
                type = 'slovenian'
            elif 'Brazilian Portuguese' in item.text():
                type = 'portuguesebrazilian'
            elif 'Irish Gaelic' in item.text():
                type = 'irish_gaelic'
            elif 'Scottish Gaelic' in item.text():
                type = 'scottish-gaelic'
            elif item.text().split(' ')[1][0] != "(":
                type = item.text().split(' ')[0].lower() + item.text().split(' ')[1].lower()
            else:
                type = item.text().split(' ')[0].lower()
            translation.append(type)
            url_heads.append("https://sourceforge.net/directory/natlanguage:{}/language:java/os:linux/".format(type))
    return url_heads

def get_page_num(url_head):
    left = 1
    right = 999
    mid = (left + right)//2
    while(left<right):
        url = url_head + '?page={}'.format(mid)
        html = get_page_text(url)
        doc = pq(html)
        if 'No results found.' in doc.find('.project_info').text():
            right = mid - 1
        else:
            left = mid + 1
        mid = (left + right)//2
    return mid-1

for url_head in get_translation_type(get_page_text(url)):
    start = perf_counter()
    print(get_page_num(url_head))
    end = perf_counter()
    print(end - start)
