import matplotlib.pyplot as plt  # основа для построения графиков
import pandas as pd  # работа с табличными данными
import seaborn as sns  # делаем графики красивыми
import numpy as np  # сложные математические операции


class DataVisualizer:
    plt.style.use("seaborn-v0_8")  # выбираем стиль графиков

    @staticmethod
    def plot_salary_distribution(vacancies):
        # показываем, сколько платят джунам, миддлам и сеньорам
        levels = ["Junior", "Middle", "Senior"]
        medians = []

        # собираем данные: для каждого уровня находим медианную зарплату
        for level in levels:
            salaries = [
                v["Зарплата"]["от"]
                for v in vacancies
                if v["Уровень"] == level and v["Зарплата"]["от"]
            ]
            medians.append(np.median(salaries) if salaries else 0)

        # рисуем столбчатую диаграмму
        plt.figure(figsize=(10, 6))
        colors = ["#4CAF50", "#2196F3", "#9C27B0"]  # зеленый, синий, фиолетовый
        bars = plt.bar(levels, medians, color=colors)

        # добавляем цифры поверх столбцов для наглядности
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.0f} BYN",
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
            )

        # оформляем график
        plt.title("Сколько платят на разных уровнях", pad=20, fontsize=14)
        plt.xlabel("Уровень специалиста", fontsize=12)
        plt.ylabel("Медианная зарплата (BYN)", fontsize=12)
        plt.grid(axis="y", alpha=0.3)  # сетка
        plt.ylim(0, max(medians) * 1.2 if medians else 1000)  # масштабируем ось Y
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_technology_popularity(vacancies):
        tech_counts = {}
        for vac in vacancies:
            for tech in vac.get("Требуемые технологии", []):
                tech_counts[tech] = tech_counts.get(tech, 0) + 1

        df = pd.DataFrame(list(tech_counts.items()), columns=["Навык", "Количество"])
        df = df.sort_values("Количество", ascending=False).head(15)

        plt.figure(figsize=(12, 8))
        bars = plt.barh(df["Навык"], df["Количество"], color="#2ecc71")

        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width}",
                ha="left",
                va="center",
            )

        plt.title("Топ-15 востребованных навыков", fontsize=14, pad=20)
        plt.xlabel("Количество упоминаний", fontsize=12)
        plt.ylabel("")
        plt.gca().invert_yaxis()
        plt.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_experience_distribution(vacancies):
        levels = ["Junior", "Middle", "Senior"]
        counts = [
            sum(1 for v in vacancies if v["Уровень"] == level) for level in levels
        ]
        total = sum(counts)
        percents = [f"{(c/total)*100:.1f}%" for c in counts] if total else ["0%"] * 3

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(levels, counts, color=["#e74c3c", "#3498db", "#9b59b6"])

        for bar, percent in zip(bars, percents):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height}\n({percent})",
                ha="center",
                va="bottom",
            )

        plt.title("Распределение вакансий по уровням", fontsize=14, pad=20)
        plt.xlabel("Уровень", fontsize=12)
        plt.ylabel("Количество вакансий", fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_work_format(vacancies):
        formats = {}
        for vac in vacancies:
            fmt = vac["Формат работы"]
            formats[fmt] = formats.get(fmt, 0) + 1

        sorted_formats = sorted(formats.items(), key=lambda x: x[1], reverse=True)
        labels = [f[0] for f in sorted_formats]
        sizes = [f[1] for f in sorted_formats]

        plt.figure(figsize=(10, 10))
        colors = plt.cm.tab20.colors
        explode = [0.05] * len(labels)

        wedges, texts, autotexts = plt.pie(
            sizes,
            labels=labels,
            autopct=lambda p: f"{p:.1f}%" if p >= 5 else "",
            startangle=140,
            colors=colors,
            explode=explode,
            textprops={"fontsize": 10},
        )

        plt.title("Распределение по форматам работы", fontsize=14, pad=20)
        plt.axis("equal")
        plt.legend(
            wedges,
            labels,
            title="Форматы",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_city_distribution(vacancies, top_n=15):
        city_counts = {}
        for vac in vacancies:
            city = vac["Регион"] or "Не указано"
            city_counts[city] = city_counts.get(city, 0) + 1

        df = pd.DataFrame(city_counts.items(), columns=["Город", "Количество"])
        df = df.sort_values("Количество", ascending=False).head(top_n)

        plt.figure(figsize=(12, 8))
        bars = plt.barh(df["Город"], df["Количество"], color="#f39c12")

        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width}",
                ha="left",
                va="center",
            )

        plt.title(f"Топ-{top_n} городов по количеству вакансий", fontsize=14, pad=20)
        plt.xlabel("Количество вакансий", fontsize=12)
        plt.ylabel("")
        plt.gca().invert_yaxis()
        plt.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()
