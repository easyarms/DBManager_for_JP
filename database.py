"""Скрипт для заполнения данными таблиц в БД Postgres
и заполнения их данными из csv-файла."""

import csv

import psycopg2

conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='BETEP2112')

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
                    "INSERT INTO vacancies (title, id, salary_from, salary_to, employers_id, employers_name, url)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (row[5], row[4], salary_from, salary_to, row[0], row[1], row[6])
                )
        conn.commit()
finally:
    conn.close()
