from time import time as Time


class Day:
    def __init__(self, date, tasks):
        self.date = date
        self.tasks = tasks

        self.woke_up = Time()
        self.fell_asleep = Time()
        self.mood = 0
        self.notes = ""

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

    def completed(self):
        self.completed = True











