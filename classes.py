import csv
import json

import requests


class ParsingError(Exception):
    def __str__(self):
        return 'Ошибка получения данных по API'


class Vacancy:
    __slots__ = ('id', 'title', 'url', 'salary_from', 'salary_to', 'employer_id', 'employer_name', 'api')

    def __init__(self, vacancy_id, title, url, salary_from, salary_to, employer_id, employer_name, api):
        self.id = vacancy_id
        self.title = title
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.employer_id = employer_id
        self.employer_name = employer_name
        self.api = api

    def __str__(self):
        salary_from = f'Oт {self.salary_from}' if self.salary_from else ''
        salary_to = f'До {self.salary_to}' if self.salary_to else ''
        if self.salary_from is None and self.salary_to is None:
            salary_from = 'Не указана'

        return f'Вакансия: \"{self.title}\"' \
               f'\nКомпания: \"{self.employer_name}, {self.employer_id}\"' \
               f'\nЗарплата: {salary_from} {salary_to}' \
               f'\nURL: {self.url}'


class Connector:
    def __init__(self, vacancies_json):
        self.__filename = 'vacancies.json'
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        with open(self.__filename, 'w', encoding='utf-8') as file:
            json.dump(vacancies_json, file, ensure_ascii=False, indent=4)

    def select(self):
        with open(self.__filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        vacancies = [Vacancy(x['id'],
                             x['title'],
                             x['url'],
                             x['salary_from'],
                             x['salary_to'],
                             x['employer_id'],
                             x['employer_name'],
                             x['api']) for x in data]
        return vacancies


class HeadHunterAPI:

    def __init__(self, employer_id):
        self.__headers = {
            "User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
        }

        self.__params = {
            'page': 0,
            'employer_id': employer_id,
            'per_page': 100
        }

        self.__vacancies = []

    def get_request(self):
        response = requests.get('https://api.hh.ru/vacancies',
                                headers=self.__headers,
                                params=self.__params)
        if response.status_code != 200:
            raise ParsingError
        return response.json()['items']

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy['salary'])
            formatted_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['name'],
                'url': vacancy['alternate_url'],
                'salary_from': salary_from,
                'salary_to': salary_to,
                'employer_id': vacancy['employer']['id'],
                'employer_name': vacancy['employer']['name'],
                'api': 'HeadHunter'
            })
        return formatted_vacancies

    def get_vacancies(self, pages_count=10):
        while self.__params['page'] < pages_count:
            print(f"HeadHunter, парсинг по страницам... ", end=": ")

            try:
                values = self.get_request()
            except ParsingError:
                print('Ошибка получения данных!')
                break
            print(f"Найдено: {len(values)} вакансий.")
            self.__vacancies.extend(values)
            self.__params['page'] += 1

    @staticmethod
    def get_salary(salary):
        formatted_salary = [None, None]
        if salary and salary['from'] and salary['from'] != 0:
            formatted_salary[0] = salary['from'] if salary['currency'].lower() == 'rur' else salary['from'] * 78
        if salary and salary['to'] and salary['to'] != 0:
            formatted_salary[1] = salary['to'] if salary['currency'].lower() == 'rur' else salary['to'] * 78
        return formatted_salary

    @staticmethod
    def from_json_to_csv():
        with open('vacancies.json', 'r') as json_file:
            vacancies = json.load(json_file)

        with open('data.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)

            if csv_file.tell() == 0:
                headers = ['employer_id', 'employer_name', 'salary_from', 'salary_to', 'id', 'title', 'url']
                writer.writerow(headers)

            for vacancy in vacancies:
                employer_id = vacancy['employer_id']
                employer_name = vacancy['employer_name']
                salary_from = vacancy['salary_from']
                salary_to = vacancy['salary_to']
                id = vacancy['id']
                title = vacancy['title']
                url = vacancy['url']
                row = [employer_id, employer_name, salary_from, salary_to, id, title, url]
                writer.writerow(row)
