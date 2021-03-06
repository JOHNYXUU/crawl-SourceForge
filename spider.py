from requests.exceptions import RequestException as RE
from multiprocessing import Pool
from pyquery import PyQuery as pq
import requests
import json
import re
import os
from config import*
from time import perf_counter
import  pymysql
import pymysql.cursors

translation = []#用于存放所有翻译语言的名称
maxtimes = 5 #设置最大请求次数
id = 1

def get_page_text(url): #用于获取页面HTML代码的text
    times = maxtimes
    while times:
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.text
            else:
                times -= 1
                if times == 0:
                    with open(dir_name+'timeanderror.txt', 'a', encoding='utf-8') as f:
                        f.write(url+'\n')
                        f.close()
                    return None
                else:
                    continue
        except RE:
            times -= 1
            if times == 0:
                with open(dir_name+'timeanderror.txt', 'a', encoding='utf-8') as f:
                    f.write(url+'\n')
                    f.close()                #假如无法请求，报错，同时存储错误网页的网址
                return  None
            else:
                continue

def get_translation_type(html):#用于获得翻译语言的类型，和原始的url组成新的url_head，为的是处理项目数目过多而导致的999页后无法浏览
    url_heads = []#存放所有的url_head
    doc = pq(html)
    items = doc.find('#facet-natlanguage li').items()
    for item in items:
        if item.text() != 'More...':
            if item.text().split(' ')[1] == '(Simplified)':#简体中文
                type = item.text().split(' ')[0].lower() + 'simplified'
            elif item.text().split(' ')[1] == '(Traditional)':#繁体中文
                type = item.text().split(' ')[0].lower() + 'traditional'
            elif 'Brazilian Portuguese' in item.text():#以下四个较为特殊，因此单独处理
                type = 'portuguesebrazilian'
            elif 'Slovene' in item.text():
                type = 'slovenian'
            elif 'Irish Gaelic' in item.text():
                type = 'irish_gaelic'
            elif 'Scottish Gaelic' in item.text():
                type = 'scottish-gaelic'
            else:#一般情况，仅把语言名称换成小写即可
                type = item.text().split(' ')[0].lower()
            translation.append(type)
            url_heads.append("https://sourceforge.net/directory/natlanguage:{}/language:java/os:linux/".format(type))#和原始的url组成新的url_head，假如找别的分类，这个也要修改成合适的url
    return url_heads

# def get_page_num(url_head):#利用二分法求这种翻译语言下的项目共有几页
#     times = maxtimes
#     while times:
#         try:
#             left = 1
#             right = 999#999为上限，因为999页过后不能浏览，所以假如项目的分类不精确，该爬虫爬取信息将不完整
#             mid = (left + right)//2
#             while(left<right):
#                 url = url_head + '?page={}'.format(mid)
#                 html = get_page_text(url)
#                 doc = pq(html)
#                 if 'No results found.' in doc.find('.project_info').text():#No results found.为超出页数范围的标志
#                     right = mid - 1
#                 else:
#                     left = mid + 1
#                 mid = (left + right)//2
#             return mid-1
#         except:
#             times -= 1
#             if times == 0:#假如五次依然不行，就返回页数为0,并且记录这个网页
#                 with open(dir_name+'timeanderror.txt', 'a', encoding='utf-8') as f:
#                     f.write(url_head)
#                     f.close()
#                 return 0
#             else:
#                 continue

def get_item_index(html):#获得某个项目的网址
    doc = pq(html)
    items = doc('#pg_directory .off-canvas-content .l-two-column-page .l-content-column .m-project-search-results li').items()
    for item in items:
        index_tail = item.find('.result-heading-texts a').attr('href')
        if index_tail:
            index = item_index_head + index_tail
            yield index

def get_item_user_ratings(doc):#获得项目的星级评价，包括平均星数和每个级别有几个人给
    dimensional_ratings = doc('.dimensional-ratings .dimensional-rating').items()
    user_ratings = {
        'average': doc('.rating .average').text(),
        'star_5': doc('.stars-5 .rating-label').text(),
        'star_4': doc('.stars-4 .rating-label').text(),
        'star_3': doc('.stars-3 .rating-label').text(),
        'star_2': doc('.stars-2 .rating-label').text(),
        'star_1': doc('.stars-1 .rating-label').text()
    }
    user_ratings['ease']=''
    user_ratings['features'] = ''
    user_ratings['design'] = ''
    user_ratings['support'] = ''
    for dimensional_rating in dimensional_ratings:#获得项目的dimensional_rating，就是项目网页中星级评价右边那个
        type = dimensional_rating.find('.label').text()
        user_ratings[type] = dimensional_rating.find('.rating-score .dim-rate').text() + '/5'
    return  user_ratings

def cnt_review_stars(user):#计算某个用户给这个项目打了几颗星
    star_num = 0
    stars = user.find('.star').items()
    for star in stars:
        if star.attr('class') == 'star  yellow':
            star_num += 1
    return  star_num

def get_user_reviews(index):#获得用户的评价，汇总了上面两个评价种类
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
        if stop_sign1 or stop_sign2:#翻页停止的标志，1是指有评论且翻到头，2是指压根就没人评论这个项目
            break
        else:
            users = doc.find('#project-reviews li').items()
            for user in users:
                user_name = user.find('.footer .author-name').text()
                if user_name:
                    if user_name == '<REDACTED>':#假如匿名评价，为此加上个数，来区分
                        user_name += '_{}'.format(no_name_num)
                        no_name_num += 1
                    review_infos = {}
                    review_infos['stars'] = cnt_review_stars(user)
                    review_infos['date'] = user.find('.footer .created-date').text()[7:]#评价日期
                    review_infos['review_txt'] = user.find('.review-txt-outer .review-txt').text()#评价内容
                    helpful_cnt = user.find('.helpful-count .user-count').text()#认为该评价有用的人数
                    if helpful_cnt:
                        review_infos['help_count'] = helpful_cnt
                    else:
                        review_infos['help_count'] = '0'
                    users_reviews[user_name] = review_infos
        page += 1
    return  users_reviews

def get_item_information(item_html,index):#获得项目所有信息的总框架
    doc = pq(item_html)
    name = doc('.title h1').text()#名称
    summary = doc('.main-content .description').text()#总结
    summary = summary.replace('\n','')
    user_ratings = get_item_user_ratings(doc)#用户评价
    CandL = doc('.main-content .row.psp-section .small-12.medium-5.columns').text()#Category和License都在这里
    if (('Categories' in CandL) and ('License' in CandL)):#Category和License都有
        Categories = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[1].replace('License', '')
        License = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[2]
    elif (('Categories' in CandL) or ('License' in CandL)):
        if ('Categories' in CandL):#只有Category
            Categories = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[1]
            License = ''
        else:#只有License
            License = doc('.main-content .row.psp-section .small-12.medium-5.columns').text().split('\n')[1]
            Categories = ''
    else:#都没有
        Categories = License =''

    item_infos = {
        'name':name,
        'summary':summary,
        'user_ratings':user_ratings,
        'Categories':Categories,
        'Licenses':License,
        'user_reviews':get_user_reviews(index)
    }
    return item_infos

def write_to_file(infos,url_head):#写入本地文件
    trans = ''
    for type in translation:
        if type in url_head:
            trans = type
            break
    dirname= dir_name+'{}'.format(trans)#改成你的文件目录（注意这是以项目的翻译语言分类存储的）
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(dirname+'/data.txt','a',encoding='utf-8') as f:#存储为txt文件
        f.write(json.dumps(infos,ensure_ascii=False)+'\n')
        f.close()

def save_to_mysql(item_infos):
    # 打开数据库连接
    global id
    db = pymysql.connect(mysql_host,mysql_username,mysql_passwords,mysql_database)
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql_1 = "INSERT INTO briefintro (name, \
           summary, Categories,Licenses) \
           VALUES ('{0}','{1}','{2}','{3}')"\
            .format(pymysql.escape_string(item_infos['name']),pymysql.escape_string(item_infos['summary']),item_infos['Categories'],item_infos['Licenses'])

    sql_2 = "INSERT INTO userratings (average,num_of_5stars,num_of_4stars,num_of_3stars,num_of_2stars,num_of_1star, \
           Ease,Features,Design,Support) \
           VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')"\
            .format(item_infos['user_ratings']['average'],item_infos['user_ratings']['star_5'],item_infos['user_ratings']['star_4'],
                    item_infos['user_ratings']['star_3'],item_infos['user_ratings']['star_2'],item_infos['user_ratings']['star_1'],
                    item_infos['user_ratings']['ease'],item_infos['user_ratings']['features'],item_infos['user_ratings']['design'],item_infos['user_ratings']['support'])
    try:
        cursor.execute(sql_1)
        cursor.execute(sql_2)
        db.commit()
        for user in item_infos['user_reviews']:
            sql_3 = "INSERT INTO userreviews (id,nickname,num_of_stars, \
                       date,review_txt,helpful_cnt) \
                       VALUES ({0},'{1}',{2},'{3}','{4}','{5}')" \
                .format(id,user,item_infos['user_reviews'][user]['stars'],item_infos['user_reviews'][user]['date'],
                        pymysql.escape_string(item_infos['user_reviews'][user]['review_txt']),item_infos['user_reviews'][user]['help_count'])
            cursor.execute(sql_3)
            db.commit()
        id += 1
    except Exception as e:
        print('{}'.format(item_infos['name']),end=' ')
        print(e)

    # 关闭数据库连接
    db.close()

def main_process(url_head):#获得分类网址后的主要过程
    for page in range(999):
        url = url_head + '?page={}'.format(page+1)
        html = get_page_text(url)
        doc = pq(html)
        if 'No results found.' in doc.find('.project_info').text():
            break
        else:
            try:
                indexs = get_item_index(html)
                for index in indexs:
                        item_html = get_page_text(index)
                        infors = get_item_information(item_html,index)
                        # write_to_file(infors,url_head)
                        save_to_mysql(infors)
                print(url+' is ok')
            except Exception as e:
                print(e)
                with open(dir_name+'timeanderror.txt', 'a', encoding='utf-8') as f:
                    f.write(url+'\n'+'in main_process')
                    f.close()
                pass

def main():
    start = perf_counter()#用于计算时间的花费
    html = get_page_text(url)
    url_heads = get_translation_type(html)
    for url_head in url_heads:#对于每一个分类，一页一页的爬
        main_process(url_head)
    print(happy_end)
    end = perf_counter()#用于计算时间的花费
    time_consumed = end - start#用于计算时间的花费
    with open(dir_name+'timeanderror.txt','a',encoding='utf-8') as f:
        f.write("all works are done!\n")
        f.write('{}'.format(time_consumed)+' s')
        f.close()

if __name__ == '__main__':
    main()
