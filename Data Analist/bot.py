import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from matplotlib import pyplot as plt
from core.parser import VacancyParser
from core.filters import VacancyFilter
from core.visualizer import DataVisualizer
import matplotlib

matplotlib.use("Agg")

from config import TOKEN, HH_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}


class Form(StatesGroup):
    search_query = State()
    filter_salary_from = State()
    filter_salary_to = State()
    filter_work_format = State()
    filter_region = State()
    filter_tech = State()
    filter_days = State()


class UserData:
    def __init__(self):
        self.vacancies = []
        self.current_vacancies = []
        self.filters = {}
        self.search_query = ""
        self.last_menu_message_id = None


parser = VacancyParser()
parser.APP_TOKEN = HH_TOKEN


class TelegramVisualizer(DataVisualizer):
    @staticmethod
    def save_plot(filename):
        plt.savefig(filename, bbox_inches="tight")
        plt.close()

    @classmethod
    def plot_salary_distribution(cls, vacancies):
        if not vacancies:
            return False
        super().plot_salary_distribution(vacancies)
        cls.save_plot("salary.png")
        return True

    @classmethod
    def plot_technology_popularity(cls, vacancies):
        if not vacancies:
            return False
        super().plot_technology_popularity(vacancies)
        cls.save_plot("tech.png")
        return True

    @classmethod
    def plot_work_distribution(cls, vacancies):
        if not vacancies:
            return False
        super().plot_work_format(vacancies)
        cls.save_plot("work.png")
        return True

    @classmethod
    def plot_exp_distribution(cls, vacancies):
        if not vacancies:
            return False
        super().plot_experience_distribution(vacancies)
        cls.save_plot("exp.png")
        return True

    @classmethod
    def plot_city_distribution(cls, vacancies):
        if not vacancies:
            return False
        super().plot_city_distribution(vacancies)
        cls.save_plot("city.png")
        return True


@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔍 Начать поиск вакансий", callback_data="start_search"
                )
            ],
            [types.InlineKeyboardButton(text="🚪 Выход", callback_data="exit_app")],
        ]
    )

    await message.answer(
        "👋 Добро пожаловать в бот для анализа вакансий!\n"
        "📊 Здесь вы можете найти и проанализировать вакансии с HeadHunter\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data == "start_search")
async def start_search_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data[user_id] = UserData()

    await callback.message.answer(
        "Введите поисковый запрос (Например: Java):",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(Form.search_query)
    await callback.answer()


@dp.message(Form.search_query)
async def process_search(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id].search_query = message.text

    await message.answer("⏳ Идет поиск вакансий...")

    vacancies = parser.fetch_vacancies(message.text)
    user_data[user_id].vacancies = vacancies
    user_data[user_id].current_vacancies = vacancies.copy()

    await message.answer(
        f"Найдено вакансий: {len(vacancies)}\n" "Выберите действие:",
        reply_markup=main_keyboard(),
    )
    await state.clear()


def main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📊 Построить статистику")],
            [types.KeyboardButton(text="⚙️ Фильтровать вакансии")],
            [types.KeyboardButton(text="🔍 Новый поиск")],
            [types.KeyboardButton(text="❌ Выход")],
        ],
        resize_keyboard=True,
    )


def back_to_menu_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад к выбору графиков", callback_data="back_to_viz_menu"
                )
            ]
        ]
    )


@dp.callback_query(F.data == "exit_app")
async def exit_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    await callback.message.answer(
        "Сессия завершена", reply_markup=types.ReplyKeyboardRemove()
    )
    await callback.answer()


@dp.message(F.text == "🔍 Новый поиск")
async def new_search(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id] = UserData()  # Сбрасываем данные пользователя

    await message.answer(
        "Введите новый поисковый запрос:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Form.search_query)


@dp.message(F.text == "📊 Построить статистику")
async def visualization_menu(message: types.Message, user_id: int = None):
    if user_id is None:
        user_id = message.from_user.id

    try:
        if user_data[user_id].last_menu_message_id:
            await bot.delete_message(
                message.chat.id, user_data[user_id].last_menu_message_id
            )
    except:
        pass

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="💰 Зарплаты по уровням", callback_data="viz_salary"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🛠️ Популярные навыки", callback_data="viz_tech"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📊 Распределение по уровням", callback_data="viz_exp"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🏢 Форматы работы", callback_data="viz_work"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🌍 Распределение по городам", callback_data="viz_city"
                )
            ],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
        ]
    )

    msg = await message.answer("📈 Выберите тип графика:", reply_markup=keyboard)
    user_data[user_id].last_menu_message_id = msg.message_id


@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("Выберите действие:", reply_markup=main_keyboard())
    await callback.message.delete()


@dp.callback_query(F.data == "back_to_viz_menu")
async def back_to_viz_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await visualization_menu(callback.message, user_id)


@dp.callback_query(F.data.startswith("viz_"))
async def process_viz(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    viz_type = callback.data.split("_")[1]
    vacancies = user_data[user_id].current_vacancies

    method_mapping = {
        "work": "plot_work_distribution",
        "exp": "plot_exp_distribution",
        "city": "plot_city_distribution",
        "tech": "plot_technology_popularity",
        "salary": "plot_salary_distribution",
    }

    if not vacancies:
        await callback.message.answer("Нет данных для построения графика")
        return

    try:
        if user_data[user_id].last_menu_message_id:
            try:
                await bot.delete_message(
                    callback.message.chat.id, user_data[user_id].last_menu_message_id
                )
            except:
                pass

        method_name = method_mapping.get(viz_type)
        if not method_name:
            raise AttributeError(f"Неизвестный тип графика: {viz_type}")

        viz_method = getattr(TelegramVisualizer, method_name)
        success = viz_method(vacancies)

        if not success:
            await callback.message.answer("Недостаточно данных для построения графика")
            return

        file = f"{viz_type}.png"
        await callback.message.answer_photo(
            FSInputFile(file),
            caption="Результат визуализации:",
            reply_markup=back_to_menu_keyboard(),
        )
        os.remove(file)
    except Exception as e:
        await callback.message.answer(f"Ошибка при построении графика: {str(e)}")


@dp.message(F.text == "⚙️ Фильтровать вакансии")
async def filter_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📊 По уровню", callback_data="filter_level"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="💰 Зарплата от", callback_data="filter_salary_from"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="💸 Зарплата до", callback_data="filter_salary_to"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🏢 Формат работы", callback_data="filter_work_format"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🌍 Регион", callback_data="filter_region"
                )
            ],
            [types.InlineKeyboardButton(text="🛠️ Навыки", callback_data="filter_tech")],
            [
                types.InlineKeyboardButton(
                    text="📅 Дата публикации", callback_data="filter_days"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="✅ Применить фильтры", callback_data="apply_filters"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🔄 Сбросить фильтры", callback_data="reset_filters"
                )
            ],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
        ]
    )
    await message.answer("🔍 Выберите тип фильтра:", reply_markup=keyboard)


@dp.callback_query(F.data == "filter_level")
async def filter_level(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Junior", callback_data="level_Junior")],
            [types.InlineKeyboardButton(text="Middle", callback_data="level_Middle")],
            [types.InlineKeyboardButton(text="Senior", callback_data="level_Senior")],
            [types.InlineKeyboardButton(text="Сбросить", callback_data="level_None")],
        ]
    )
    await callback.message.answer("Выберите уровень:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("level_"))
async def process_level(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    level = callback.data.split("_")[1]
    if level == "None":
        user_data[user_id].filters.pop("Уровень", None)
    else:
        user_data[user_id].filters["Уровень"] = level
    await callback.message.answer(
        f"Установлен уровень: {level if level != 'None' else 'Сброшен'}"
    )


@dp.callback_query(F.data == "filter_salary_from")
async def filter_salary_from(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите минимальную зарплату:")
    await state.set_state(Form.filter_salary_from)


@dp.message(Form.filter_salary_from)
async def process_salary_from(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        salary = int(message.text)
        user_data[user_id].filters["Зарплата от"] = salary
        await message.answer(f"Установлена минимальная зарплата: {salary}")
    except ValueError:
        await message.answer("Некорректное значение")
    await state.clear()


@dp.callback_query(F.data == "filter_salary_to")
async def filter_salary_to(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите максимальную зарплату:")
    await state.set_state(Form.filter_salary_to)


@dp.message(Form.filter_salary_to)
async def process_salary_to(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        salary = int(message.text)
        user_data[user_id].filters["Зарплата до"] = salary
        await message.answer(f"Установлена максимальная зарплата: {salary}")
    except ValueError:
        await message.answer("Некорректное значение")
    await state.clear()


@dp.callback_query(F.data == "filter_work_format")
async def filter_work_format(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🕘 Полный день", callback_data="work_full"
                ),
                types.InlineKeyboardButton(
                    text="⏱️ Гибкий график", callback_data="work_flex"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="🔄 Сменный график", callback_data="work_shift"
                ),
                types.InlineKeyboardButton(
                    text="🏠 Удалённая работа", callback_data="work_remote"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="🏕️ Вахтовый метод", callback_data="work_rotation"
                )
            ],
            [types.InlineKeyboardButton(text="❌ Сбросить", callback_data="work_none")],
        ]
    )
    await callback.message.answer("🏢 Выберите формат работы:", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("work_"))
async def process_work_format(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    work_format = callback.data.split("_")[1]

    format_mapping = {
        "full": "Полный день",
        "flex": "Гибкий график",
        "shift": "Сменный график",
        "remote": "Удалённая работа",
        "rotation": "Вахтовый метод",
        "none": None,
    }

    selected_format = format_mapping.get(work_format)

    if selected_format:
        user_data[user_id].filters["Формат работы"] = selected_format
        await callback.message.answer(f"✅ Установлен формат: {selected_format}")
    else:
        user_data[user_id].filters.pop("Формат работы", None)
        await callback.message.answer("❌ Формат работы сброшен")

    await callback.answer()


@dp.callback_query(F.data == "apply_filters")
async def apply_filters(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    filtered = VacancyFilter.filter_vacancies(
        user_data[user_id].vacancies, user_data[user_id].filters
    )
    user_data[user_id].current_vacancies = filtered

    text = f"Найдено вакансий: {len(filtered)}\n"
    for vac in filtered[:5]:
        text += f"\n{vac['Название вакансии']}\nЗарплата: {vac['Зарплата']['от']}-{vac['Зарплата']['до']} {vac['Зарплата']['валюта']}\nСсылка: {vac['Ссылка']}\n"

    await callback.message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "reset_filters")
async def reset_filters(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id].filters = {}
    user_data[user_id].current_vacancies = user_data[user_id].vacancies.copy()
    await callback.message.answer("Фильтры сброшены")


@dp.callback_query(F.data == "filter_region")
async def filter_region(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название региона:")
    await state.set_state(Form.filter_region)


@dp.message(Form.filter_region)
async def process_region(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id].filters["Регион"] = message.text
    await message.answer(f"Установлен регион: {message.text}")
    await state.clear()


@dp.callback_query(F.data == "filter_tech")
async def filter_tech(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите навыки через запятую:")
    await state.set_state(Form.filter_tech)


@dp.message(Form.filter_tech)
async def process_tech(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    techs = [t.strip() for t in message.text.split(",")]
    user_data[user_id].filters["Технологии"] = techs
    await message.answer(f"Установлены навыки: {', '.join(techs)}")
    await state.clear()


@dp.callback_query(F.data == "filter_days")
async def filter_days(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите количество дней:")
    await state.set_state(Form.filter_days)


@dp.message(Form.filter_days)
async def process_days(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        days = int(message.text)
        user_data[user_id].filters["Дата публикации"] = days
        await message.answer(f"Установлен период: последние {days} дней")
    except ValueError:
        await message.answer("Некорректное значение")
    await state.clear()


if __name__ == "__main__":
    dp.run_polling(bot)
