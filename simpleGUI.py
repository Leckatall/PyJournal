import PySimpleGUIQt as sg
import DBInterface
import PySide6
from dataclasses import dataclass
import main

TITLE_FORMATTING = {"font": ("Calibri", 24),
                    "justification": "center"}


def main_layout():
    return [
        [sg.Text(text='PyJournal', **TITLE_FORMATTING)],
        # [sg.Table([[]], key="_data")],
        [sg.Input(default_text="date", key='-date-'), sg.CalendarButton("Calendar", target='-date-',
                                                                        key='_CALENDAR_',
                                                                        default_date_m_d_y=(5, None, 24))],
        [sg.Button('View Day'), sg.Button('Add Entry Today'), sg.Button('ViewDB')],
        [sg.Button('QUIT')]
    ]


def day_layout(date):
    return [
        [sg.Text(text=f'Viewing {date}', **TITLE_FORMATTING)],
        [sg.Multiline(journal_db.get_entries_for_date(date), key="date_contents")],
        [sg.Button('View Day'), sg.Button('Add Entry Today')],
        [sg.Button('QUIT')]
    ]


def add_entry_layout():
    # tag_frame_layout = [
    #     [sg.Listbox(tag_list, select_mode='multiple')],
    #     [sg.Button('Add Tag')]
    # ]
    # naming_frame_layout = [
    #     [sg.Text("Name:"), sg.Input(key="Name")],
    #     [sg.Text("Description:"), sg.Multiline(key="Description")]
    # ]
    # return [
    #     [sg.Text(text='Link Importer', **TITLE_FORMATTING)],
    #     [sg.Text(text=f'currently importing: {link_name}')],
    #     [sg.Frame("", naming_frame_layout), sg.Frame("", tag_frame_layout)],
    #     [sg.Button("Add Link"), sg.Button("Cancel")]
    # ]

    return [
        [sg.Text("Title:"), sg.Input(key="Name")],
        [sg.Text("Contents:"), sg.Multiline(key="Description")],
        [sg.Button("Add Entry"), sg.Button("Cancel")]
    ]


class HandledWindow(sg.Window):
    def __init__(self, parent_window, title, layout, **kwargs):
        super().__init__(title, layout, **kwargs)
        self.parent_window: sg.Window = parent_window


class WindowHandler:
    def __init__(self, window: sg.Window):
        self.main_window: sg.Window = window
        self.sub_windows: dict[str, HandledWindow] = dict()
        self.active_window: sg.Window = self.main_window

    def close_active_window(self):
        # Not sure how to feel abt this code lol
        # ^ U should feel ashamed this is the dumbest shit I've ever seen my god
        # theoretically closing the mainwindow should close it then restart mainloop?? <- I fixed it a little now
        # hahahahaha yh that's why the program was never closing XD
        if self.active_window == self.main_window:
            self.main_window.close()
            return
        # To tell the linter that what I'm doing isn't **that** dumb
        self.active_window: HandledWindow

        next_active_window = self.active_window.parent_window
        self.active_window.close()
        self.active_window = next_active_window
        self.mainloop()

    def add_entry(self):
        self.sub_windows["AddEntry"] = HandledWindow(self.active_window,
                                                       "Add Entry",
                                                       add_entry_layout())
        self.active_window = self.sub_windows["AddEntry"]

    def import_file(self):
        ...

    def mainloop(self):
        while True:
            event, values = self.active_window.read()
            if event == sg.WIN_CLOSED or event == 'QUIT':  # if user closes window or clicks quit
                self.close_active_window()
                break
            if event == "Import File":
                self.import_file()
            if event == "Add Entry Today":
                self.add_entry()
            if event == "Add Entry":
                print("Add Entry?")

            print('You entered ')


journal_db = DBInterface.JournalDB()

sg.theme('DarkBlack')

# Create the Window
main_window = sg.Window('WebLink Manager', main_layout(), size=(750, 750))

window_handler = WindowHandler(main_window)
window_handler.mainloop()















