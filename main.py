from classes import HeadHunterAPI, Connector
from db_classes import DBManager


def main():
    vacancies_json = []

    employers_id = ['80',  # Alfa-Bank
                    '1740',  # Яндекс
                    '8550',  # ЦФТ
                    '3529',  # СБЕР
                    '22494',  # Neoflex
                    '78638',  # Tinkoff
                    '23040',  # Открытие
                    '172616',  # Evola
                    '598471',  # Evrone
                    '4300631']  # Kvando

    for employer_id in employers_id:
        hh = HeadHunterAPI(employer_id)
        hh.get_vacancies(pages_count=1)
        vacancies_json.extend(hh.get_formatted_vacancies())

    connector = Connector(vacancies_json=vacancies_json)
    db = DBManager()
    HeadHunterAPI.from_json_to_csv()
    while True:
        command = input(
            "\n------------------------------------\n"
            "1 - Вывести полный список вакансий из json-файла; \n"
            "2 - Создать новые таблицы в БД и загрузить данные из csv-файла; \n"
            "3 - Список всех компаний и количество вакансий у каждой компании; \n"
            "4 - Список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки; \n"
            "5 - Средняя зарплата по вакансиям; \n"
            "6 - Список всех вакансий, у которых зарплата выше средней по всем вакансиям; \n"
            "7 - Список всех вакансий по ключевому слову; \n"
            "exit - Выйти. \n"
        )
        if command.lower() == 'exit':
            break

        elif command.lower() == '1':
            vacancies = connector.select()
            for vacancy in vacancies:
                print(vacancy, end='\n\n')

        elif command.lower() == '2':
            DBManager.create_tables_with_data()
            print('Таблицы с актуальными данными созданы.')

        elif command.lower() == '3':
            print(db.get_companies_and_vacancies_count())

        elif command.lower() == '4':
            print(db.get_all_vacancies())

        elif command.lower() == '5':
            print(f'{round(db.get_avg_salary())} RUB')

        elif command.lower() == '6':
            print(db.get_vacancies_with_higher_salary())

        elif command.lower() == '7':
            keyword = input('Введите ключевое слово для поиска: ').lower()
            print(db.get_vacancies_with_keyword(keyword))

        else:
            print('Введена неверная команда.')


if __name__ == '__main__':
    main()
