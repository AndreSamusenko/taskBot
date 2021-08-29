from subprocess import call
from os import listdir
from os.path import isfile

class Tasker:
    PYTHON_PATH = "python.exe"
    TESTS_FOLDER = "tests"
    TASKS_FOLDER = "tasks"
    INPUT_FILE = "input.txt"
    OUTPUT_FILE = "output.txt"
    USER_CODE_FILE = "user_code.py"
    TASK_FILE = "Условие.txt"
    INPUT_CONDITION = "Входные.txt"
    OUTPUT_CONDITION = "Выходные.txt"
    EXAMPLE_FILE = "Пример.txt"

    def test_task(self, task_name):
        tests_pass = 0

        for test_num in listdir(f"{self.TASKS_FOLDER}/{task_name}/{self.TESTS_FOLDER}"):
            call((self.PYTHON_PATH, self.USER_CODE_FILE),
                 stdin=open(f"{self.TASKS_FOLDER}/{task_name}/{self.TESTS_FOLDER}/{test_num}/{self.INPUT_FILE}", "r"),
                 stdout=open(f"{self.TASKS_FOLDER}/{self.OUTPUT_FILE}", "w"))

            user_answer = open(f"{self.TASKS_FOLDER}/{self.OUTPUT_FILE}", "r").read()
            right_answer = open(f"{self.TASKS_FOLDER}/{task_name}/{self.TESTS_FOLDER}/{test_num}/{self.OUTPUT_FILE}", "r").read()

            if user_answer.strip() != right_answer.strip():
                return tests_pass

            tests_pass += 1
        return True

    def __safe_open__(self, task_name, file_name):
        path = f"{self.TASKS_FOLDER}/{task_name}/{file_name}"

        text = "Пока нет условия"
        if isfile(path):
            text = open(path, "r", encoding="UTF-8").read()

        return text

    def get_task(self, task_name):
        condition = "условие"
        input_data = "входные"
        output_data = "выходные"
        example = "пример"

        task = {condition: self.__safe_open__(task_name, self.TASK_FILE),
                input_data: self.__safe_open__(task_name, self.INPUT_CONDITION),
                output_data: self.__safe_open__(task_name, self.OUTPUT_CONDITION),
                example: self.__safe_open__(task_name, self.EXAMPLE_FILE)}

        return task

    def get_all_tasks(self):
        return listdir(self.TASKS_FOLDER)

