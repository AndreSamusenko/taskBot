from requests import get as req_get, post as req_post
from threading import Thread
from json import dumps as json_dumps, dump as json_dump, load as json_load
from Tasker import Tasker
from time import sleep
from copy import copy


class TelegramBot:
    TOKEN = "1958366332:AAE-Pl4mc4R0ntBravSOAKPHXDVd68_mbBk"
    BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
    BASE_NAME = "progress.json"
    ADMIN_ID = 523468577

    WELCOME_MES = "Выбирай действие на клаве внизу 👇"
    CHOOSE_TASK_MES = "Выбирай одну из задач 📋"
    NOW_IN_SOLUTION_MES = "🤔 Сейчас решается задача "
    TASK_SELECTED_MES = "Задача выбрана ✔"
    AVOID_SOLVING_MES = "Ты успешно отказался от решения задачи ✔"
    TESTING_TASK_MES = "Тестируем решение ⏳"
    TASK_FAILED_MES = "❌ Не прошёл тест №"
    ACCEPTED_MES = "✅ Принято!"
    INCORRECT_FILE_MES = "❌ Некорректный файл"
    ERRORS_IN_CODE_MES = "🚧 Ошибки в коде:\n"
    NO_TASK_SELECTED_MES = "Сейчас нет решаемых задач 😶"
    STOP_MES = "закончить"
    SOLVED_TASKS_MES = "📊 Всего решенных задач: "
    NO_SOLVED_MES = "🤪 Ты пока не решили ни одной задачи"
    ALL_STATS_COMMAND = "stats"
    TIME_EXCEED_MES = "❌ Превышено время ожидания ответа."

    NOT_DETECTED_MES = "⛔ Неизвестная команда"
    SOLVE_TASKS_MES = "🧠 Решать задачи"
    MY_STATS_MES = "📈 Моя статистика"
    NOW_IN_PROGRESS_MES = "🤔 Решаемая сейчас задача"

    HELP_TEXT = "Данный бот🤖 создан для тренировки навыков программирования👨‍💻.\n" \
                "Он умеет выдавать задачи, проверять их решение, вести статистику.\n" \
                "Пока поддерживается только язык программирования Python 🐍.\n\n" \
                "Все ответы для задач проверяются посимвольно, поэтому для прохождения тестов " \
                "необходимо избегать лишних символов в выводе (например, лишнего пробела в конце строки).\n" \
                "Если хочешь перестать решать задачу, отправляй боту слово 'закончить'.\n" \
                "Решение можно присылать в виде текста сообщением, либо же python-файлом."

    MAIN_KEYBOARD = {"keyboard": [[SOLVE_TASKS_MES],
                                  [MY_STATS_MES]],
                     "one_time_keyboard": False}

    offset = 0
    states = {}
    solved_tasks = {}

    def __init__(self):
        self.read_from_base()
        Thread(target=self.start_parsing).start()

    def start_parsing(self):
        while True:
            self.parse_messages()
            sleep(1)

    def parse_messages(self):
        response = self.get_updates()

        for update in response["result"]:
            if mes := update.get("message"):
                text = mes.get("text")
                chat_id = mes["chat"]["id"]
                document = mes.get("document")

                if text:
                    state = self.states.get(chat_id, "start")

                    if state == "start":
                        if text == "/start":
                            self.send_message(chat_id, self.HELP_TEXT)
                            self.send_keyboard(chat_id)

                        elif text == "/keyboard":
                            self.send_keyboard(chat_id)

                        elif text == "/help":
                            self.send_message(chat_id, self.HELP_TEXT)

                        elif text == self.NOW_IN_PROGRESS_MES:
                            self.send_message(chat_id, self.NO_TASK_SELECTED_MES)

                        elif text == self.MY_STATS_MES:
                            self.get_stats(chat_id)

                        elif text == self.SOLVE_TASKS_MES:
                            self.solve_tasks_action(chat_id)

                        elif text == self.ALL_STATS_COMMAND and chat_id == self.ADMIN_ID:
                            message = ""
                            for user in self.solved_tasks:
                                message += user + ": " + ", ".join(list(self.solved_tasks[user])) + "\n"

                            self.send_message(chat_id, message)

                        else:
                            self.send_message(chat_id, self.NOT_DETECTED_MES)

                    else:
                        if text.lower() == self.STOP_MES:
                            self.send_message(chat_id, self.AVOID_SOLVING_MES)
                            self.states.pop(chat_id, None)

                        elif text == self.SOLVE_TASKS_MES:
                            self.solve_tasks_action(chat_id)
                            self.states.pop(chat_id, None)

                        elif text == self.NOW_IN_PROGRESS_MES:
                            self.send_message(chat_id, self.NOW_IN_SOLUTION_MES + f'"{state}"')

                        else:
                            open(tasker.USER_CODE_FILE, "w", encoding="UTF-8").write(text)
                            Thread(target=self.start_testing, args=(chat_id, state)).start()

                elif document:
                    state = self.states.get(chat_id, "start")
                    if state != "start":
                        self.work_with_file(document, chat_id, state)

            elif callback_query := update.get("callback_query"):
                if mes := callback_query.get("message"):
                    chat_id = mes.get("chat", {}).get("id")
                    data = callback_query.get('data')
                    callback_query_id = callback_query.get("id")
                    mes_id = mes.get("message_id")

                    self.select_task(chat_id, mes_id, data, callback_query_id)

        if response["result"]:
            self.offset = response["result"][-1]['update_id'] + 1

    def start_testing(self, chat_id, state):
        req_post(self.BASE_URL + "sendMessage",
                 data={"chat_id": chat_id,
                       "text": self.TESTING_TASK_MES})

        test_failed = tasker.test_task(state)
        errors = open(tasker.ERROR_FILE, "r", encoding="UTF-8").read()
        if errors:
            message = self.ERRORS_IN_CODE_MES + errors
        elif test_failed and test_failed == tasker.ENDLESS_CYCLE_ERROR_CODE:
            message = self.TIME_EXCEED_MES
        elif test_failed:
            message = self.TASK_FAILED_MES + str(test_failed)
        else:
            message = self.ACCEPTED_MES
            self.states.pop(chat_id, None)

            user_id = str(chat_id)
            if self.solved_tasks.get(user_id):
                self.solved_tasks[user_id].add(state)

            else:
                self.solved_tasks[user_id] = set()
                self.solved_tasks[user_id].add(state)

            Thread(target=self.save_base).start()

        self.send_message(chat_id, message)

    def solve_tasks_action(self, chat_id):
        tasks = tasker.get_all_tasks()

        buttons = []
        solved_tasks = self.solved_tasks.get(str(chat_id), set())
        for task in tasks:
            task_with_tag = task + ("✅" if task in solved_tasks else "")
            buttons.append([{"text": task_with_tag, 'callback_data': task}])

        keyboard = json_dumps({'inline_keyboard': buttons})
        req_post(self.BASE_URL + "sendMessage",
                 data={"chat_id": chat_id,
                       "text": self.CHOOSE_TASK_MES,
                       'reply_markup': keyboard})

    def send_keyboard(self, chat_id):
        req_post(self.BASE_URL + "sendMessage",
                 data={"chat_id": chat_id,
                       "text": self.WELCOME_MES,
                       'reply_markup': json_dumps(self.MAIN_KEYBOARD)})

    def edit_keyboard(self, chat_id, mes_id, data):
        req_post(self.BASE_URL + "editMessageText",
                 data={"chat_id": chat_id,
                       "message_id": mes_id,
                       "text": self.NOW_IN_SOLUTION_MES + f'"{data}"',
                       "reply_markup": json_dumps({})})

    def answer_keyboard_button(self, callback_query_id):
        req_post(self.BASE_URL + "answerCallbackQuery",
                 data={"callback_query_id": callback_query_id,
                       "text": self.TASK_SELECTED_MES})

    def work_with_file(self, document, chat_id, state):
        file_id = document.get('file_id')

        file_path = req_get(self.BASE_URL + "getFile",
                            params={"file_id": file_id}).json().get('result').get('file_path')

        if file_path and file_path[-3:] == ".py":
            file = req_get(f"https://api.telegram.org/file/bot{self.TOKEN}/{file_path}")
            open(tasker.USER_CODE_FILE, "w", encoding="UTF-8").write(file.text)

            Thread(target=self.start_testing, args=(chat_id, state)).start()
        else:
            req_post(self.BASE_URL + "sendMessage",
                     data={"chat_id": chat_id,
                           "text": self.INCORRECT_FILE_MES})

    def select_task(self, chat_id, mes_id, data, callback_query_id):
        self.edit_keyboard(chat_id, mes_id, data)
        self.answer_keyboard_button(callback_query_id)

        task = tasker.get_task(data)
        req_post(self.BASE_URL + "sendMessage",
                 data={"chat_id": chat_id,
                       "text": self.__parse_task__(task)})
        self.states[chat_id] = data

    def send_message(self, chat_id, text):
        req_post(self.BASE_URL + "sendMessage",
                 data={"chat_id": chat_id,
                       "text": text})

    def get_updates(self):
        return req_get(self.BASE_URL + "getUpdates", data={"offset": self.offset}).json()

    def get_stats(self, chat_id):
        total = len(tasker.get_all_tasks())
        if solved_tasks := self.solved_tasks.get(str(chat_id)):
            message = self.SOLVED_TASKS_MES + f"{str(len(solved_tasks))}/{total}" + "\n\n"
            for task in sorted(solved_tasks):
                message += task + " ✅" + "\n"
        else:
            message = self.NO_SOLVED_MES

        self.send_message(chat_id, message)

    def save_base(self):
        base_to_json = copy(self.solved_tasks)
        for key in base_to_json:
            base_to_json[key] = list(base_to_json[key])

        with open(self.BASE_NAME, 'w', encoding="UTF-8") as f:
            json_dump(base_to_json, f)

    def read_from_base(self):
        with open(self.BASE_NAME, "r", encoding="UTF-8") as f:
            base_from_json = json_load(f)

        self.solved_tasks = {}
        for key in base_from_json:
            self.solved_tasks[key] = set(base_from_json[key])

    @staticmethod
    def __parse_task__(task):
        # examples_raw = task[tasker.EXAMPLE_FILE].split()
        # examples = []

        decorated_task = "-------------------------Условие---------------------------\n" \
                         f"{task[tasker.TASK_FILE]}\n" \
                         "-------------------------------------------------------------\n\n\n" \
                         "-----------------------Входные данные-------------------\n" \
                         f"{task[tasker.INPUT_CONDITION]}\n" \
                         "-------------------------------------------------------------\n\n\n" \
                         "-----------------------Выходные данные------------------\n" \
                         f"{task[tasker.OUTPUT_CONDITION]}\n" \
                         "-------------------------------------------------------------\n\n\n" \
                         "------------------------Примеры----------------------------\n" \
                         f"{task[tasker.EXAMPLE_FILE]}\n" \
                         "-------------------------------------------------------------\n"
        return decorated_task


# ----------MAIN-------------
tg_bot = TelegramBot()
tasker = Tasker()
