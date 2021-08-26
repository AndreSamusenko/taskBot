from subprocess import call
from os import listdir


class Tasker:
    PYTHON_PATH = "python.exe"
    TESTS_FOLDER = "tests"
    INPUT_FILE = "input.txt"
    OUTPUT_FILE = "output.txt"

    def test_task(self, task_name):
        for test_num in listdir(self.TESTS_FOLDER):
            call((self.PYTHON_PATH, "hello.py"),
                 stdin=open(f"{self.TESTS_FOLDER}/{test_num}/{self.INPUT_FILE}", "r"),
                 stdout=open(self.OUTPUT_FILE, "w"))

            text_from_file = open(self.OUTPUT_FILE, "r").read()
            right_answer = open(f"{self.TESTS_FOLDER}/{test_num}/{self.OUTPUT_FILE}", "r").read()
            print(text_from_file.strip() == right_answer.strip())
