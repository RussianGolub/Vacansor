# filters.py - фильтрация собранных вакансий
from datetime import datetime, timedelta
from dateutil import tz

class VacancyFilter:
    @staticmethod
    def filter_vacancies(vacancies, filters):
        # применяем все фильтры к списку вакансий
        filtered = vacancies.copy()

        for key, value in filters.items():
            if value is None:
                continue

            if key == "Уровень":
                # фильтр по уровню (Junior/Middle/Senior)
                filtered = [v for v in filtered if v["Уровень"] == value]

            elif key == "Зарплата от":
                # минимальная зарплата
                filtered = [v for v in filtered if v["Зарплата"]["от"] and v["Зарплата"]["от"] >= value]

            elif key == "Зарплата до":
                # максимальная зарплата
                filtered = [v for v in filtered if v["Зарплата"]["до"] and v["Зарплата"]["до"] <= value]

            elif key == "Формат работы":
                # разные названия одного формата работы
                format_mapping = {
                    "Полный день": ["полный день", "полная занятость", "full-time"],
                    "Гибкий график": ["гибкий график", "гибкое расписание", "flexible"],
                    "Сменный график": ["сменный график", "смены", "shift"],
                    "Удалённая работа": ["удалённая работа", "удаленная работа", "remote"],
                    "Вахтовый метод": ["вахтовый метод", "вахта", "rotation"]
                }
                allowed_formats = format_mapping.get(value, [])
                filtered = [v for v in filtered if any(
                    fmt.lower() in v["Формат работы"].lower()
                    for fmt in allowed_formats
                )]

            elif key == "Регион":
                # фильтр по городу
                filtered = [v for v in filtered if v["Регион"] == value]

            elif key == "Технологии":
                # все указанные навыки должны быть в вакансии
                filtered = [v for v in filtered if all(tech in v["Требуемые технологии"] for tech in value)]

            elif key == "Дата публикации":
                # вакансии за последние N дней
                days = value
                date_limit = datetime.now(tz=tz.UTC) - timedelta(days=days)
                filtered = [v for v in filtered if
                    datetime.fromisoformat(v["Дата публикации"].replace('Z', '+00:00')).replace(tzinfo=tz.UTC) > date_limit]

        return filtered