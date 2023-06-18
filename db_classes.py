import csv
import os

import psycopg2


class DBManager:
    """Класс для подключения к базе данных,
    загрузки обновлённых таблиц
    и получения данных по вакансиям из списка компаний"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user='postgres',
            password=os.getenv("DB_PASSWORD")
        )
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.conn.close()

    @classmethod
    def create_tables_with_data(cls):
        """Статический метод для заполнения данными таблиц в БД Postgres
        и заполнения их данными из csv-файла"""

        conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password=os.getenv("DB_PASSWORD"))

        try:
            with conn:
                cur = conn.cursor()
                cur.execute('''CREATE TABLE employers
                             (employers_id int PRIMARY KEY,
                              employers_name varchar(100) NOT NULL);''')

                cur.execute('''CREATE TABLE vacancies
                             (title varchar(100) NOT NULL,
                              id int PRIMARY KEY,
                              salary_from int,
                              salary_to int,
                              employers_id int NOT NULL,
                              employers_name varchar(100) NOT NULL,
                              url TEXT NOT NULL,
                              FOREIGN KEY (employers_id) REFERENCES employers(employers_id));''')
                employers = []

                with open('data.csv', 'r') as f:
                    csvreader = csv.reader(f)
                    next(csvreader)
                    for row in csvreader:
                        if row[0] not in employers:
                            employers.append(row[0])
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO employers (employers_id, employers_name)"
                                "VALUES (%s, %s)",
                                (row[0], row[1])
                            )
                conn.commit()

                with open('data.csv', 'r') as f:
                    csvreader = csv.reader(f)
                    next(csvreader)
                    for row in csvreader:
                        salary_from = int(row[2]) if row[2] != '' else None
                        salary_to = int(row[3]) if row[3] != '' else None
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO vacancies ("
                            "title, id, salary_from, salary_to, employers_id, employers_name, url)"
                            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (row[5], row[4], salary_from, salary_to, row[0], row[1], row[6])
                        )
                conn.commit()
        finally:
            conn.close()

    def get_companies_and_vacancies_count(self):
        """Метод для вывода списка всех компаний и количество вакансий у каждой компании"""

        query = '''
            SELECT employers_name, COUNT(*) 
            FROM vacancies 
            GROUP BY employers_name 
            ORDER BY COUNT(*) DESC
        '''
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    def get_all_vacancies(self):
        """Метод для вывода всех вакансий с указанием
        названия компании, названия вакансии, зарплаты и ссылки"""

        query = '''
            SELECT e.employers_name, v.title, v.salary_from, v.salary_to, v.url 
            FROM vacancies v
            JOIN employers e
            ON v.employers_id = e.employers_id
        '''
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    def get_avg_salary(self):
        """Метод для вывода средней зарплаты по всем вакансиям"""
        query = '''
            SELECT AVG(salary_from + salary_to)/2 
            FROM vacancies
        '''
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result[0]

    def get_vacancies_with_higher_salary(self):
        """Метод для вывода всех вакансий, у которых зарплата выше средней"""

        avg_salary = self.get_avg_salary()
        query = '''
            SELECT e.employers_name, v.title, v.salary_from, v.salary_to, v.url 
            FROM vacancies v 
            JOIN employers e 
            USING (employers_id)
            WHERE (salary_from + salary_to)/2 > %s
        '''
        self.cur.execute(query, (avg_salary,))
        result = self.cur.fetchall()
        return result

    def get_vacancies_with_keyword(self, keyword):
        """Метод для вывода всех вакансий по ключевому слову keyword"""

        query = '''
            SELECT e.employers_name, v.title, v.salary_from, v.salary_to, v.url 
            FROM vacancies v 
            JOIN employers e 
            USING (employers_id)
            WHERE title ILIKE %s
        '''
        self.cur.execute(query, ('%' + keyword + '%',))
        result = self.cur.fetchall()
        return result
