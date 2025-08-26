
# 📊 Telegram-бот для анализа IT-вакансий (rabota.by)

Этот проект — Telegram-бот на **Python**, который собирает, фильтрует и визуализирует IT-вакансии с сайта [rabota.by](https://rabota.by).  
Цель — быстрый анализ рынка труда в сфере IT в Республике Беларусь.  

[Документация](https://docs.google.com/document/d/1NkHSEcCJd_q35cPJVbyoSprp46pwudCs/edit?usp=sharing&ouid=113335923884980325046&rtpof=true&sd=true) Google диск

[Презентация](https://drive.google.com/file/d/1mNzu0zFqxHBuqIiey5X0lunzs5snT_bB/view?usp=sharing) Google диск

---

## 🔹 Возможности
- 📥 **Сбор данных** через API rabota.by (название, компания, зарплата, опыт, регион, технологии и др.)  
- 🔎 **Фильтрация вакансий** по ключевым критериям:
  - уровень (Junior / Middle / Senior)  
  - зарплата (от/до)  
  - регион  
  - формат работы (офис / удалёнка / гибрид)  
  - используемые технологии  
  - дата публикации  
- 📊 **Визуализация**:
  - средняя зарплата по уровням  
  - топ востребованных технологий  
  - количество вакансий по уровням  
  - распределение по формату работы  
  - топ-15 городов по числу вакансий  
- 🤖 **Telegram-бот**:
  - простой диалог через конечный автомат (FSM)  
  - пошаговый выбор фильтров  
  - автоматическая отправка графиков в чат  

---

## 🛠️ Технологии
- Python 3.10+  
- [aiogram](https://docs.aiogram.dev/) — для Telegram-бота  
- [requests](https://docs.python-requests.org/) — для работы с API rabota.by  
- [matplotlib](https://matplotlib.org/) и [pandas](https://pandas.pydata.org/) — для визуализации  
- [python-dateutil](https://dateutil.readthedocs.io/) — работа с датами  

---

## ⚙️ Установка и запуск

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/username/rabota-by-telegram-bot.git
   cd rabota-by-telegram-bot
