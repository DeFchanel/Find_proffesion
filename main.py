import requests
from pprint import pprint
from itertools import count


url = 'https://api.hh.ru/vacancies'
prog_lang = [
    'JavaScript',
    'Java',
    'Python'
]
salaries = []
lang_salaries = []
    

def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != 'RUR':
        return None
    elif not salary_from:
        return (salary_to * 0.8)
    elif not salary_to:
        return (salary_from * 1.2)
    else:
        return ((salary_from + salary_to) / 2)


def find_vacancies(lang):
    for page in count(0):
        payload = {
            'text': f'программист {lang}',
            'area': 1,
            'page': page
        }
        response = requests.get(url, params=payload)
        response.raise_for_status()
        response_payload = response.json()
        for vacancie in response_payload['items']:
            vacancie_salary = vacancie['salary']
            if vacancie_salary:
                salary_from = vacancie_salary['from']
                salary_to = vacancie_salary['to']
                salary_currency = vacancie_salary['currency']
                salary = predict_rub_salary(salary_from, salary_to, salary_currency)
                if salary:
                    salaries.append(salary)
        if page == response_payload['pages'] - 1:
            break
    vacancies_found = response.json()['found']
    vacancies_processed = len(salaries)
    if vacancies_processed:
        average_salary = sum(salaries) // vacancies_processed
    else:
        average_salary = 0
    return { 
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }




for lang in prog_lang:
    lang_salary = {
        lang: find_vacancies(lang)
    }
    lang_salaries.append(lang_salary)
pprint(lang_salaries)



