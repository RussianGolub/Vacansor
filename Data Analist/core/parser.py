# parser.py - сбор и обработка вакансий с hh.ru
import requests
import json
from datetime import datetime
from tqdm import tqdm
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor


class VacancyParser:
    def __init__(self):
        # настройки для API
        self.APP_TOKEN = (
            "APPLJ92H8JP5G51IFD02RPC054KKO5THN9CML3SDHO795VEJ3F76S57GRTM59RSF"
        )
        self.USER_AGENT = "VacancyBot/1.0 (andre.ilutin@yandex.by)"
        self.API_URL = "https://api.hh.ru/vacancies"
        self.executor = ThreadPoolExecutor(max_workers=10)

    def safe_request(self, url, headers, params=None):  # запрос с обработкой ошибок

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"запрос не удался: {e}")
            return None

    def detect_job_level(
        self, experience_text
    ):  # определяем уровень по требуемому опыту
        if not experience_text:
            return "не указано"

        exp = experience_text.lower()
        if "нет" in exp or "0" in exp or "без опыта" in exp:
            return "Junior"
        elif ("1" in exp and "3" in exp) or ("от 1 года" in exp):
            return "Middle"
        elif "3" in exp or "6" in exp or "более" in exp:
            return "Senior"
        return "не указано"

    def parse_vacancy(self, item):  # парсим полные данные вакансии по ID
        vacancy_id = item.get("id")
        url = f"{self.API_URL}/{vacancy_id}"
        response = self.safe_request(url, self.get_headers())
        if not response:
            return None

        vacancy_data = response.json()

        # вытаскиваем зарплату, регион и навыки
        salary = vacancy_data.get("salary") or {}
        area = vacancy_data.get("area", {})
        skills = [skill["name"] for skill in vacancy_data.get("key_skills", [])]

        # конвертируем валюту в BYN (курс фиксированный)
        currency_rates = {"USD": 3.1, "EUR": 3.5, "RUR": 0.033}
        original_currency = salary.get("currency", "BYR")
        rate = currency_rates.get(original_currency, 1)

        # собираем всё в словарь
        return {
            "Название вакансии": vacancy_data.get("name"),
            "Компания": vacancy_data.get("employer", {}).get("name"),
            "Ссылка": vacancy_data.get("alternate_url", ""),
            "Зарплата": {
                "от": salary.get("from") * rate if salary.get("from") else None,
                "до": salary.get("to") * rate if salary.get("to") else None,
                "валюта": (
                    "BYN" if original_currency in currency_rates else original_currency
                ),
                "грязная": salary.get("gross", False),
            },
            "Опыт работы": vacancy_data.get("experience", {}).get("name"),
            "Тип занятости": vacancy_data.get("employment", {}).get("name"),
            "Формат работы": vacancy_data.get("schedule", {}).get("name"),
            "Требуемые технологии": skills,
            "Регион": area.get("name", "Не указано"),
            "Дата публикации": vacancy_data.get("published_at"),
            "Уровень": self.detect_job_level(
                vacancy_data.get("experience", {}).get("name")
            ),
        }

    def get_headers(self):  # заголовок для запросов к API
        return {
            "Authorization": f"Bearer {self.APP_TOKEN}",
            "User-Agent": self.USER_AGENT,
            "HH-User-Agent": self.USER_AGENT,
        }

    def fetch_vacancies(self, search_query, max_pages=20):  # метод для сбора вакансий
        headers = self.get_headers()
        params = {
            "text": quote(search_query),
            "area": 16,  # 16 - код Беларуси в hh.ru
            "per_page": 100,  # максимум на страницу
            "host": "rabota.by",  # только вакансии с rabota.by
        }

        # общее количество вакансий
        response = self.safe_request(self.API_URL, headers, params)
        if not response or response.status_code != 200:
            return []

        data = response.json()
        total = data.get("found", 0)
        if total == 0:
            return []

        # сколько страниц нужно обработать
        pages = min(max_pages, (total // 100) + 1)
        all_items = []

        # краткие данные вакансий
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for page in range(pages):
                future = executor.submit(
                    self.process_page, page, headers, params.copy()
                )
                futures.append(future)

            for future in tqdm(futures, desc="сбор вакансий"):
                all_items.extend(future.result())

        # парсим полные данные
        with ThreadPoolExecutor(max_workers=10) as executor:
            vacancies = list(
                tqdm(
                    executor.map(self.parse_vacancy, all_items),
                    total=len(all_items),
                    desc="обработка вакансий",
                )
            )

        return [v for v in vacancies if v is not None]

    def process_page(self, page, headers, params):
        # обработка одной страницы с вакансиями
        params.update({"page": page})
        response = self.safe_request(self.API_URL, headers, params)
        if response and response.status_code == 200:
            return response.json().get("items", [])
        return []

    def save_to_json(self, data, filename):
        # сохранение данных в JSON-файл
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\nданные сохранены в файл: {filename}")
