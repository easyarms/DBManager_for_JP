from classes import HeadHunterAPI, Connector


def main():
    vacancies_json = []

    employers_id = ['31430', '22494', '80', '6769', '8550', '3529', '97026', '1122462', '23040', '230159']
    for employer_id in employers_id:
        hh = HeadHunterAPI(employer_id)
        hh.get_vacancies(pages_count=1)
        vacancies_json.extend(hh.get_formatted_vacancies())

        hh.from_json_to_csv()

    connector = Connector(vacancies_json=vacancies_json)
    while True:
        command = input(
            "show - Вывести список всех вакансий \n"
            "exit - Выйти \n"
        )
        if command.lower() == 'exit':
            break
        elif command.lower() == 'show':
            vacancies = connector.select()
            for vacancy in vacancies:
                print(vacancy, end='\n\n')
        else:
            print('Введена неверная команда.')


if __name__ == '__main__':
    main()
