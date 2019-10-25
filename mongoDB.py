from pymongo import MongoClient
from pprint import pprint
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from vacancy import hh

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
jobs = []
title = 'python'

for i in range(2):
    html_hh = requests.get(f'https://hh.ru/search/vacancy?text={title}&page={i}', headers=headers).text
    parsed_hh = bs(html_hh, 'lxml')

    job_opportunity = parsed_hh.find_all('div', {
        'data-qa': ['vacancy-serp__vacancy', 'vacancy-serp__vacancy vacancy-serp__vacancy_premium']})

    for job in job_opportunity:
        job_data = {}
        job_name = job.find('a').text
        link = job.find('a').get('href', '')
        site = re.findall(r'\w+.ru', link)
        salary = job.find('div', {'class': 'vacancy-serp-item__compensation'})

        if salary is None:
            salary_min = 'None'
            salary_max = 'None'

        elif 'от' in salary.getText():
            salary_min = re.findall("\d.+", salary.getText())[0].replace('\xa0', '')
            salary_max = 'None'

        elif 'до' in salary.getText():
            salary_min = 'None'
            salary_max = re.findall("\d.+", salary.getText())[0].replace('\xa0', '')

        elif '-' in salary.getText():
            s = re.split('-', salary.getText())
            salary_min = s[0].replace('\xa0', '')
            salary_max = s[1].replace('\xa0', '')

        job_data['name'] = job_name
        job_data['link'] = link
        job_data['salary_min'] = salary_min
        job_data['salary_max'] = salary_max
        job_data['site'] = site

        jobs.append(job_data)

# Задание 2. Парсим Superjob

for i in range(2):
    html_sj = requests.get(f'https://www.superjob.ru/vacancy/search/?keywords={title}&page={i}', headers=headers).text
    parsed_sj = bs(html_sj, 'lxml')

    job_opp_sj = parsed_sj.find_all('div', {'class': '_3syPg _1_bQo _2FJA4'})

    for job in job_opp_sj:
        job_data = {}
        job_name = job.find('a').text
        link = 'https://superjob.ru' + job.find('a').get('href', '')
        site = re.findall(r'\w+.ru', link)
        salary = job.find('span', {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})

        if salary is not None:
            if 'от' in salary.getText():
                salary_min = re.findall("\d.+", salary.getText())[0].replace('\xa0', '')
                salary_max = 'None'

            elif '—' in salary.getText():
                s_sj = re.split('\xa0—\xa0', salary.getText())
                salary_min = s_sj[0].replace('\xa0', '')
                salary_max = s_sj[1].replace('\xa0', '')
            else:
                salary_max = salary.getText().replace('\xa0', '')
                salary_min = salary.getText().replace('\xa0', '')
        else:
            salary_min = 'None'
            salary_max = 'None'

        job_data['name'] = job_name
        job_data['link'] = link
        job_data['salary_min'] = salary_min
        job_data['salary_max'] = salary_max
        job_data['site'] = str(site[0]) # Не понятно почему в базу уходит как список

        jobs.append(job_data)


# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД

client = MongoClient('localhost', 27017)
db = client['VACANCY']
jobs_opportunity = db.jobs_opportunity

def job_opportunity_db(data):
    jobs_opportunity.insert_many(data)
    return

job_opportunity_db(jobs)


# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы

sum = int(input('Задайте минимальное значение: '))

def salary(sum):
    object = jobs_opportunity.find({'salary_min': {'$gte': sum}}, {'name', 'salary_min'});
    for obj in object:
        pprint(f"<{obj['name']}> <{obj['salary_min']}>")


salary(sum)

               
# obj = []
# object = jobs_opportunity.find()
# for obj in object:
#     if obj['salary_min'] != None and obj['salary_min'] != 'None' and obj['salary_min'] != 'По договорённости':
#         ob = int(re.findall('[0-9]+', obj['salary_min'])[0])

#         if ob >= sum:
#             print (obj['name'], '-', ob)
#             continue

#     else:
#         continue


# 3*)Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
# # 
# # jobs_opportunity.update_one(
# #     {'link':job_data['link']},
# #     {'$set':job_data},
# #     upsert=True
# # )
