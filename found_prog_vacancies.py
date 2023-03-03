import requests
from itertools import count
import os
from dotenv import load_dotenv
from terminaltables import AsciiTable



def predict_rub_salary_sj(lang):
    sj_salaries = []
    headers = {
        "X-Api-App-Id" : sj_key
    }
    for page in count(0):
        sj_payload = {
            'keyword': f'программист {lang}',
            'town': 4,
            'page': page
        }
        superjob_response = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers, params=sj_payload)
        superjob_response.raise_for_status()
        superjob_answer = superjob_response.json()
        for vacancie in superjob_answer['objects']:
            salary_from = vacancie['payment_from']
            salary_to = vacancie['payment_to']
            salary_currency = vacancie['currency']
            sj_salary = predict_rub_salary(salary_from, salary_to, salary_currency)
            if sj_salary:
                sj_salaries.append(sj_salary)
        if not superjob_answer['more']:
            break
    vacancies_found = superjob_answer['total']
    vacancies_processed = len(sj_salaries)
    if vacancies_processed:
        average_salary = sum(sj_salaries) // vacancies_processed
    else:
        average_salary = 0
    return { 
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }


def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != 'RUR' and salary_currency != 'rub':
        return None
    if not salary_from:
        return (salary_to * 0.8)
    elif not salary_to:
        return (salary_from * 1.2)
    else:
        return ((salary_from + salary_to) / 2)


def predict_rub_salary_hh(lang):
    hh_salaries = []
    for page in count(0):
        payload = {
            'text': f'программист {lang}',
            'area': 1,
            'page': page
        }
        response_hh = requests.get('https://api.hh.ru/vacancies', params=payload)
        response_hh.raise_for_status()
        response_hh_payload = response_hh.json()
        for vacancie in response_hh_payload['items']:
            vacancie_salary = vacancie['salary']
            if vacancie_salary:
                salary_from = vacancie_salary['from']
                salary_to = vacancie_salary['to']
                salary_currency = vacancie_salary['currency']
                salary = predict_rub_salary(salary_from, salary_to, salary_currency)
                if salary:
                    hh_salaries.append(salary)
        if page == response_hh_payload['pages'] - 1:
            break
    vacancies_found = response_hh_payload['found']
    vacancies_processed = len(hh_salaries)
    if vacancies_processed:
        average_salary = sum(hh_salaries) // vacancies_processed
    else:
        average_salary = 0
    return { 
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }



def make_table(lang_salaries, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]
    for lang, vacancie_info in lang_salaries.items():
        raw = [lang, vacancie_info['vacancies_found'], vacancie_info['vacancies_processed'], vacancie_info['average_salary']]
        table_data.append(raw)
    table = AsciiTable(table_data, title)
    print(table.table)


if __name__ == '__main__':
    load_dotenv()
    sj_key = os.getenv('SUPERJOB_KEY')
    prog_lang = [
        'JavaScript',
        'Java',
        'Python'
    ]
    lang_salaries_hh = {}
    lang_salaries_sj = {}
    title_sj = 'SuperJob Moscow'
    title_hh = 'HeadHunter Moscow'
    for lang in prog_lang:
        lang_salary_sj = predict_rub_salary_sj(lang)
        lang_salaries_sj[lang] = lang_salary_sj
        lang_salary_hh = predict_rub_salary_hh(lang)
        lang_salaries_hh[lang] = lang_salary_hh
    make_table(lang_salaries_sj, title_sj)
    make_table(lang_salaries_hh, title_hh)