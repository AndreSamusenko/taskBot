from subprocess import Popen, TimeoutExpired
from os import listdir
from os.path import isfile
from config import ConfigData

config_data = ConfigData()


class Tasker:
    PYTHON_PATH = config_data.PYTHON_PATH
    TESTS_FOLDER = "tests"
    TASKS_FOLDER = "tasks"
    INPUT_FILE = "input.txt"
    OUTPUT_FILE = "output.txt"
    USER_CODE_FILE = "scr/your_code.py"
    TASK_FILE = "Условие.txt"
    INPUT_CONDITION = "Входные.txt"
    OUTPUT_CONDITION = "Выходные.txt"
    ERROR_FILE = "scr/error.txt"
    EXAMPLE_FILE = "Пример.txt"
    EXAMPLES_SPLIT = "-------------------------------------------------------------"
    ENDLESS_CYCLE_ERROR_CODE = 999

    def test_task(self, task_name):
        open(self.ERROR_FILE, "w").write("")
        tests_pass = 1

        for test_num in listdir(f"{self.TASKS_FOLDER}/{task_name}/{self.TESTS_FOLDER}"):
            try:
                task = Popen((self.PYTHON_PATH, self.USER_CODE_FILE),
                             stdin=open(f"{self.TASKS_FOLDER}/{task_name}/{self.TESTS_FOLDER}/{test_num}/{self.INPUT_FILE}", "r"),
                             stdout=open(self.OUTPUT_FILE, "w"), stderr=open(self.ERROR_FILE, "w"))
                task.wait(1)

            except TimeoutExpired:
                return self.ENDLESS_CYCLE_ERROR_CODE

            user_answer = open(self.OUTPUT_FILE, "r").read()
            right_answer = open(f"{self.TASKS_FOLDER}/{task_name}/{self.TESTS_FOLDER}/{test_num}/{self.OUTPUT_FILE}", "r").read()

            if user_answer.strip() != right_answer.strip():
                return tests_pass

            tests_pass += 1
        return 0

    def __safe_open__(self, task_name, file_name):
        path = f"{self.TASKS_FOLDER}/{task_name}/{file_name}"

        text = "Пока нет условия"
        if isfile(path):
            text = open(path, "r", encoding="UTF-8").read()

        return text

    def get_task(self, task_name):
        files = [self.TASK_FILE, self.INPUT_CONDITION, self.OUTPUT_CONDITION, self.EXAMPLE_FILE]

        task = {}
        for file in files:
            task[file] = self.__safe_open__(task_name, file)

        return task

    def get_all_tasks(self):
        return sorted(listdir(self.TASKS_FOLDER))

