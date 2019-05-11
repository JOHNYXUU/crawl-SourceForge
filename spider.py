from requests.exceptions import RequestException as RE
from multiprocessing import Pool
from pyquery import PyQuery as pq
import requests
import json
import re
import os
from config import*
from time import perf_counter

def get_main_page_text(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
        return None
    except RE:
        print('ERROR when requesting main page')
        return None

def get_item_page_text(index):
    try:
        res = requests.get(index)
        if res.status_code == 200:
            return res.text
        return None
    except RE:
        print('ERROR when requesting item page')
        return  None

def get_review_page_text(review_url):
    try:
        res = requests.get(review_url)
        if res.status_code == 200:
            return res.text
        return None
    except RE:
        print('ERROR when requesting review page')
        return  None

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
        'star_1': doc('.stars-1 .rating-label').text(),
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
            html = get_review_page_text(review_url)
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
        Categories = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[1][:-8]
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

def write_to_file(infos):
    with open('C:\\Users\\11634\\Desktop\\Python\\爬虫\\实战\\SourceForgelinxjava\\data.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(infos,ensure_ascii=False)+'\n')
        f.close()

def main(page):
    url = url_head + '?page={}'.format(page)
    html = get_main_page_text(url)
    indexs = get_item_index(html)
    for index in indexs:
        item_html = get_item_page_text(index)
        infors = get_item_information(item_html,index)
        write_to_file(infors)

if __name__ == '__main__':
    start = perf_counter()
    groups = [x for x in range(1, 999)]
    pool = Pool()
    pool.map(main, groups)
    end = perf_counter()
    time_consumed = end - start
    print(time_consumed)