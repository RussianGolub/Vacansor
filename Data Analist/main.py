# это консольное приложение с таким же функционалом, что и у тг-бота
from core.parser import VacancyParser
from core.filters import VacancyFilter
from core.visualizer import DataVisualizer
from datetime import datetime


def main_menu():
    print("\nГлавное меню:")
    print("1. Построить статистику")
    print("2. Фильтровать вакансии")
    print("3. Выход")
    return input("Выберите действие: ")

def visualization_menu():
    print("\nВизуализация данных:")
    print("1. Распределение зарплат по уровням")
    print("2. Популярность навыков")
    print("3. Распределение по уровням опыта")
    print("4. Формат работы")
    print("5. Распределение по городам")
    print("6. Назад")
    return input("Выберите тип графика: ")

def filter_menu():
    print("\nФильтры:")
    print("1. По уровню")
    print("2. По зарплате")
    print("3. По формату работы")
    print("4. По региону")
    print("5. По навыку")
    print("6. По дате публикации")
    print("7. Применить фильтры и показать результаты")
    print("8. Сбросить фильтры")
    print("9. Назад")
    return input("Выберите фильтр: ")

def main():
    parser = VacancyParser()
    filter = VacancyFilter()

    search_query = input("Введите тему для поиска (IT, Java, Python и т.д.): ")

    vacancies = parser.fetch_vacancies(search_query)
    print('Количество найденных вакансий:',len(vacancies))
    if not vacancies:
        print("Нет данных для анализа")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"vacancies_{search_query}_{timestamp}.json"
    parser.save_to_json(vacancies, filename)

    current_vacancies = vacancies.copy()
    active_filters = {}

    while True:
        choice = main_menu()

        if choice == '1':
            while True:
                viz_choice = visualization_menu()
                if viz_choice == '1':
                    DataVisualizer.plot_salary_distribution(current_vacancies)
                elif viz_choice == '2':
                    DataVisualizer.plot_technology_popularity(current_vacancies)
                elif viz_choice == '3':
                    DataVisualizer.plot_experience_distribution(current_vacancies)
                elif viz_choice == '4':
                    DataVisualizer.plot_work_format(current_vacancies)
                elif viz_choice == '5':
                    DataVisualizer.plot_city_distribution(current_vacancies)
                elif viz_choice == '6':
                    break

        elif choice == '2':
            while True:
                filter_choice = filter_menu()

                if filter_choice == '1':
                    level = input("Введите уровень (Junior/Middle/Senior): ").capitalize()
                    active_filters["Уровень"] = level if level in ["Junior", "Middle", "Senior"] else None

                elif filter_choice == '2':
                    salary_from = input("Зарплата от (оставьте пустым если не важно): ")
                    salary_to = input("Зарплата до (оставьте пустым если не важно): ")
                    active_filters["Зарплата от"] = int(salary_from) if salary_from else None
                    active_filters["Зарплата до"] = int(salary_to) if salary_to else None

                elif filter_choice == '3':
                    work_format = input("Введите формат работы(Полный день,Удаленная работа,Гибридный день): ")
                    active_filters["Формат работы"] = work_format

                elif filter_choice == '4':
                    region = input("Введите регион (Минск/Другие города): ")
                    active_filters["Регион"] = region

                elif filter_choice == '5':
                    techs = input("Введите навыки через запятую: ").split(',')
                    active_filters["Технологии"] = [t.strip() for t in techs]

                elif filter_choice == '6':
                    days = input("Вакансии за последние N дней: ")
                    active_filters["Дата публикации"] = int(days) if days.isdigit() else None

                elif filter_choice == '7':
                    current_vacancies = filter.filter_vacancies(vacancies, active_filters)
                    print(f"\nНайдено вакансий: {len(current_vacancies)}")
                    for vac in current_vacancies[:5]:
                        print(f"\n{'='*50}")
                        print(f"📌 Должность: {vac['Название вакансии']}")
                        print(f"🏢 Компания: {vac['Компания']}")
                        print(f"🔗 Уровень: {vac['Уровень']}")
                        print(f"💰 Зарплата: {vac['Зарплата']['от']} - {vac['Зарплата']['до']} {vac['Зарплата']['валюта']}")
                        print(f"🔗 Ссылка: {vac['Ссылка']}")
                        print(f"{'='*50}")

                elif filter_choice == '8':
                    active_filters = {}
                    current_vacancies = vacancies.copy()
                    print("\nФильтры сброшены")

                elif filter_choice == '9':
                    break

        elif choice == '3':
            print("Выход из программы")
            break

if __name__ == "__main__":
    main()