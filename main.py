from classes import HeadHunterAPI, Connector, DBManager


def main():
    vacancies_json = []

    employers_id = ['31430', '22494', '80', '6769', '8550', '3529', '97026', '1122462', '23040', '230159']

    connector = Connector(vacancies_json=vacancies_json)
    db = DBManager()
    while True:
        command = input(
            "---\n"
            "1 - Список всех компаний и количество вакансий у каждой компании; \n"
            "2 - Список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки; \n"
            "3 - Средняя зарплата по вакансиям; \n"
            "4 - Список всех вакансий, у которых зарплата выше средней по всем вакансиям; \n"
            "5 - Список всех вакансий по ключевому слову; \n"
            "6 - Обновить данные csv-файла; ” \n"
            "exit - Выйти. \n"
        )
        if command.lower() == 'exit':
            break

        elif command.lower() == '1':
            print(db.get_companies_and_vacancies_count())

        elif command.lower() == '2':
            print(db.get_all_vacancies())

        elif command.lower() == '3':
            print(db.get_avg_salary())

        elif command.lower() == '4':
            print(db.get_vacancies_with_higher_salary())

        elif command.lower() == '5':
            keyword = input('Введите ключевое слово для поиска: ').lower()
            print(db.get_vacancies_with_keyword(keyword))

        elif command.lower() == '6':
            vacancies = connector.select()
            for vacancy in vacancies:
                print(vacancy, end='\n\n')

        elif command.lower() == '7':
            for employer_id in employers_id:
                hh = HeadHunterAPI(employer_id)
                hh.get_vacancies(pages_count=1)
                vacancies_json.extend(hh.get_formatted_vacancies())

                hh.from_json_to_csv()
        else:
            print('Введена неверная команда.')


if __name__ == '__main__':
    main()
