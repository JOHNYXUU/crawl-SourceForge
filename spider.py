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
            elif item.text().split(' ')[1][0] != "(":
                type = item.text().split(' ')[0].lower() + '-' + item.text().split(' ')[1].lower()
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

def get_item_index(html):
    doc = pq(html)
    items = doc('#pg_directory .off-canvas-content .l-two-column-page .l-content-column .m-project-search-results li').items()
    for item in items:
        index_tail = item.find('.result-heading-texts a').attr('href')
        if index_tail:
            index = item_index_head + index_tail
            yield index


def get_item_user_ratings(doc):
    dimensional_ratings = doc('.dimensional-ratings .dimensional-rating').items()
    user_ratings = {
        'average': doc('.rating .average').text(),
        'star_5': doc('.stars-5 .rating-label').text(),
        'star_4': doc('.stars-4 .rating-label').text(),
        'star_3': doc('.stars-3 .rating-label').text(),
        'star_2': doc('.stars-2 .rating-label').text(),
        'star_1': doc('.stars-1 .rating-label').text()
    }
    for dimensional_rating in dimensional_ratings:
        type = dimensional_rating.find('.label').text()
        user_ratings[type] = dimensional_rating.find('.rating-score .dim-rate').text() + '/5'
    return  user_ratings

def cnt_review_stars(user):
    star_num = 0
    stars = user.find('.star').items()
    for star in stars:
        if star.attr('class') == 'star  yellow':
            star_num += 1
    return  star_num

def get_user_reviews(index):
    page = 1
    no_name_num = 1
    users_reviews = {}
    while page :
        review_url = index + 'reviews/?offset={}#reviews'.format((page-1)*25)
        try:
            html = get_page_text(review_url)
        except:
            break
        doc = pq(html)
        stop_sign1 = doc.find('.info-no-reviews').text()
        stop_sign2 = (doc.find('.main-content .row p').text() == 'This project does not allow reviews to be posted.')
        if stop_sign1 or stop_sign2:
            break
        else:
            users = doc.find('#project-reviews li').items()
            for user in users:
                user_name = user.find('.footer .author-name').text()
                if user_name:
                    if user_name == '<REDACTED>':
                        user_name += '_{}'.format(no_name_num)
                        no_name_num += 1
                    review_infos = {}
                    review_infos['stars'] = cnt_review_stars(user)
                    review_infos['date'] = user.find('.footer .created-date').text()[7:]
                    review_infos['review_txt'] = user.find('.review-txt-outer .review-txt').text()
                    helpful_cnt = user.find('.helpful-count .user-count').text()
                    if helpful_cnt:
                        review_infos['help-count'] = helpful_cnt
                    else:
                        review_infos['help-count'] = '0'
                    users_reviews[user_name] = review_infos
        page += 1
    return  users_reviews

def get_item_information(item_html,index):
    doc = pq(item_html)
    name = doc('.title h1').text()
    summary = doc('.main-content .description').text()
    summary = summary.replace('\n','')
    user_ratings = get_item_user_ratings(doc)
    try:
        Categories = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[1].replace('License','')
    except:
        Categories = ''
    try:
        License = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[2]
    except:
        License = ''
    item_infos = {
        'name':name,
        'summary':summary,
        'user-ratings':user_ratings,
        'Categories':Categories,
        'License':License,
        'user_reviews':get_user_reviews(index)
    }
    return item_infos

def write_to_file(infos,url_head):
    trans = ''
    for type in translation:
        if type in url_head:
            trans += type
            break
    dir_name = '/root/SourceForgelinxjava/data/{}'.format(trans)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    with open(dir_name+'/data.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(infos,ensure_ascii=False)+'\n')
        f.close()

def main_process(page,url_head):
    url = url_head + '?page={}'.format(page)
    html = get_page_text(url)
    indexs = get_item_index(html)
    for index in indexs:
        item_html = get_page_text(index)
        infors = get_item_information(item_html,index)
        write_to_file(infors,url_head)

def main():
    start = perf_counter()
    html = get_page_text(url)
    url_heads = get_translation_type(html)
    for url_head in url_heads:
        page = get_page_num(url_head)
        for i in range(page):
            main_process(i+1,url_head)
    end = perf_counter()
    time_consumed = end - start
    print(time_consumed)
    with open('/root/SourceForgelinxjava/time.txt','a',encoding='utf-8') as f:
        f.write(time_consumed)
        f.close()
if __name__ == '__main__':
    main()
