from requests import get as req_get, post as req_post
from threading import Thread
from json import dumps as json_dumps
from Tasker import Tasker
from time import sleep

class TelegramBot:
    TOKEN = "1958366332:AAE-Pl4mc4R0ntBravSOAKPHXDVd68_mbBk"
    BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

    WELCOME_MES = "Выбирай действие на клаве внизу 👇"
    CHOOSE_TASK_MES = "Выбирай одну из задач"
    NOW_IN_SOLUTION_MES = "Сейчас решается задача "
    TASK_SELECTED_MES = "Задача выбрана"

    NOT_DETECTED_MES = "Неизвестная команда"
    SOLVE_TASKS_MES = "Решать задачи"
    MY_STATS_MES = "Моя статистика"
    ACTION_3 = "Действие 3"

    MAIN_KEYBOARD = {"keyboard": [[SOLVE_TASKS_MES],
                                  [MY_STATS_MES],
                                  [ACTION_3]],
                     "one_time_keyboard": False}

    offset = 0
    states = {}

    def __init__(self):
        Thread(target=self.start_parsing).start()

    def start_parsing(self):
        while True:
            self.parse_messages()
            sleep(1)

    def parse_messages(self):
        response = req_get(self.BASE_URL + "getUpdates", data={"offset": self.offset}).json()

        for update in response["result"]:
            if mes := update.get("message"):
                text = mes.get("text")
                chat_id = mes["chat"]["id"]

                if text:
                    state = self.states.get(chat_id, "start")

                    if state == "start":
                        if text == "/start":
                            req_post(self.BASE_URL + "sendMessage",
                                     data={"chat_id": chat_id,
                                           "text": self.WELCOME_MES,
                                           'reply_markup': json_dumps(self.MAIN_KEYBOARD)})

                        elif text == self.SOLVE_TASKS_MES:
                            tasks = tasker.get_all_tasks()

                            buttons = []
                            for task in tasks:
                                buttons.append([{"text": task, 'callback_data': task}])

                            keyboard = json_dumps({'inline_keyboard': buttons})
                            req_post(self.BASE_URL + "sendMessage",
                                     data={"chat_id": chat_id,
                                           "text": self.CHOOSE_TASK_MES,
                                           'reply_markup': keyboard})

                        else:
                            req_post(self.BASE_URL + "sendMessage",
                                     data={"chat_id": chat_id,
                                           "text": self.NOT_DETECTED_MES})

                    # elif state == "add":
                    #     pass
                    #     req_post(self.BASE_URL + "sendMessage",
                    #              data={"chat_id": chat_id,
                    #                    "text": message})
                    #     self.states.pop(chat_id, None)

            elif callback_query := update.get("callback_query"):
                if mes := callback_query.get("message"):
                    chat_id = mes.get("chat", {}).get("id")
                    data = callback_query.get('data')
                    callback_query_id = callback_query.get("id")
                    mes_id = mes.get("message_id")

                    # редактирование клавы

                    req_post(self.BASE_URL + "editMessageText",
                             data={"chat_id": chat_id,
                                   "message_id": mes_id,
                                   "text": self.NOW_IN_SOLUTION_MES + f'"{data}"',
                                   "reply_markup": json_dumps({})})

                    # ответ на нажатие клавиши в клаве
                    req_post(self.BASE_URL + "answerCallbackQuery",
                             data={"callback_query_id": callback_query_id,
                                   "text": self.TASK_SELECTED_MES})

                    task = tasker.get_task(data)
                    req_post(self.BASE_URL + "sendMessage",
                             data={"chat_id": chat_id,
                                   "text": self.__parse_task__(task)})

        if response["result"]:
            self.offset = response["result"][-1]['update_id'] + 1

    @staticmethod
    def __parse_task__(task):
        # examples_raw = task[tasker.EXAMPLE_FILE].split()
        # examples = []

        decorated_task = "-------------------------Условие---------------------------\n\n" \
                         f"{task[tasker.TASK_FILE]}\n\n" \
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
