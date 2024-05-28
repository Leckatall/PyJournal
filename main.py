from time import time as Time
import datetime
from dataclasses import dataclass
from dateutil import parser


def get_day(the_date: datetime.date):
    with open(f"ExampleDays/{the_date.strftime("%d-%m-%Y")}.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines


def get_today():
    today = datetime.date.today().strftime("%d-%m-%Y")
    with open(f"ExampleDays/{today}.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines


@dataclass
class Entry:
    title: str
    date: datetime.date
    contents: str


class Day:
    def __init__(self, this_date, tasks):
        self.date: datetime.date = this_date
        self.tasks = tasks

        self.woke_up: Time
        self.fell_asleep: Time
        self.mood: int
        self.notes: list[Entry] = []

    def set_wake_up_time(self, time):
        self.woke_up = time

    def set_fell_asleep_time(self, time):
        self.fell_asleep = time

    def set_mood(self, mood: str):
        self.mood = mood

    def set_notes(self, notes: str):
        self.notes = notes


class Task:
    def __init__(self, name):
        self.name = name
        self.completed = False
        self.notes = ""

    def set_notes(self, notes: str):
        self.notes = notes

    def complete(self):
        self.completed = True











