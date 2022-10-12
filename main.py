import json
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from random import choice
import simpleaudio
import time
import re
import os

WIDTH = 400
HEIGHT = 550
IMAGE_WIDTH = 310
IMAGE_HEIGHT = 460

class Model:
    count = None
    bpm = None
    chord_files = None
    chord = None

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.hand_mode_bool = True
        self.is_group_selected, self.start, self.are_chords_displayed, self.is_pop_closed = (False, False, False, False)

        self.chord_files = os.listdir('chord_images')
        self.chord_files_right = os.listdir('chord_images_right')

        self.group_chord_files = []
        self.thumbnail_list = []
        self.presave_new_group = []

        self.bpm, self.time, self.count = (0, 0, 0)
        # self.time = 0, self.count = 0
        self.chord, self.spaced_names, self.save_data = (None, None, None)

        self.group_values = self.get_values_for_dropdown()

    def toggle_hand_mode(self):
        if self.hand_mode_bool:
            self.hand_mode_bool = False
        else:
            self.hand_mode_bool = True
        self.view.hand_mode_var.set(self.get_hand_mode())
        print(self.hand_mode_bool)

    def get_hand_mode(self):
        if self.hand_mode_bool:
            return 'Left Handed Mode'
        else:
            return 'Right Handed Mode'

    def get_values_for_dropdown(self):
        try:
            with open('chord_group_log.json', mode='r') as file:
                data = json.load(file)
                new_list = [i for i in data]
                new_list.append('Add New Chord Group')
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return ['Add New Chord Group']
        else:
            # print(data['name'])
            return new_list

    def load_chord_group(self):
        """Loads chord list from groups saved in the json log."""
        # empty the group chord files with each run of this function.
        self.group_chord_files = []
        file = open('chord_group_log.json', mode='r')
        data = json.load(file)
        selection = self.view.custom_group_dropdown.get()
        if selection in data:
            for chord in data[selection]['chords']:
                name = f'{chord}.png'
                print(name)
                self.group_chord_files.append(name)
                self.get_files()

    def get_files(self):
        """Determines where to source the file paths based on handedness and whether a group of chords is selected."""
        # Left or Right handed mode
        if self.hand_mode_bool:
            files = self.chord_files
        else:
            files = self.chord_files_right
        if not self.is_group_selected:
            chord = choice(files)
        else:
            chord = choice(self.group_chord_files)
        if self.hand_mode_bool:
            self.chord_image = PhotoImage(file=f'chord_images/{chord}')
        else:
            self.chord_image = PhotoImage(file=f'chord_images_right/{chord}')
        self.view.canvas.itemconfig(self.view.image, image=self.chord_image)

    def start_view(self):
        """Starts the View/ Gui Interface."""
        self.view.set_up(self)
        self.view.start_mainloop()

    def start_counter(self):
        if self.start is False:
            try:
                self.bpm = int(self.view.dropdown.get())
            except ValueError:
                self.bpm = 60
            else:
                if self.bpm > 120:
                    self.bpm = 120

            self.start = True
            self.counter(self.view)

    def stop_counter(self):
        self.start = False
        self.view.root.after_cancel(self.metronome)

    def counter(self, view):
        if self.start:
            self.time = int((60 / self.bpm - 0.1) * 1000)
        self.count += 1
        if self.count < 5:
            self.play_strong_beat()
            self.get_files()
            self.count = 0

        self.metronome = self.view.root.after(self.time, lambda: self.counter(self.view))

    def play_strong_beat(self):
        strong_beat = simpleaudio.WaveObject.from_wave_file('strong_beat.wav')
        strong_beat.play()

    def on_start_button(self):
        self.start_counter()

    def on_ok_btn(self):
        selection = self.view.custom_group_dropdown.get()
        if selection == 'Add New Chord Group':
            self.view.create_popup()
        else:
            self.is_group_selected = True
            self.load_chord_group()
    def pp_presave_chords(self):
        self.presave_new_group = []
        left_box = self.view.left_box
        all_items = left_box.get(0, END)
        selected_index = left_box.curselection()
        self.presave_new_group = [all_items[item] for item in selected_index]
        # print(self.presave_new_group)
        self.pp_display_chords()

    def pp_display_chords(self):
        self.are_chords_displayed = True
        self.thumbnail_list = []
        self.thumbnail_files = []
        self.spaced_names = []
        r_counter = self.view.r_counter
        c_counter = self.view.c_counter
        # Format Chord Names without Spaces so that they match the file names.
        self.spaced_names = [chord.replace(" ", "") for chord in self.presave_new_group]
        for item in self.spaced_names:
            if self.hand_mode_bool:
                path = f'thumbnails/{item}.png'
            else:
                path = f'thumbnails_right/{item}.png'

            thumbnail = PhotoImage(file=path)
            self.thumbnail_list.append(thumbnail)
        for thumbnail in self.thumbnail_list:
            new_label = ttk.Label(self.view.right_frame, image=thumbnail)
            new_label.grid(row=r_counter, column=c_counter)
            c_counter += 1
            if c_counter == 3:
                r_counter += 1
                c_counter = 0

    def pp_save_chord_group(self):
        if self.are_chords_displayed:
            name = self.view.right_entry.get()
            self.save_data = {
                name: {
                    'chords': self.spaced_names,
                }
            }
            if name == 'name':
                messagebox.showwarning(title='Change Name', message="Please enter a group name.")
            else:
                try:
                    file = open('chord_group_log.json', mode='r')
                    data = json.load(file)
                    data.update(self.save_data)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    file = open('chord_group_log.json', mode='w')
                    json.dump(self.save_data, file, indent=4)
                else:
                    file = open('chord_group_log.json', mode='w')
                    json.dump(data, file, indent=4)
                finally:
                    file.close()
                    self.save_data, self.spaced_names = (None, None)
                    self.thumbnail_list = []
                    self.are_chords_displayed = False
                    self.view.custom_group_dropdown['values'] = self.group_values
                    print(name)


class View:
    width = 500
    height = 700
    image_width = 310
    image_height = 460

    chord_image = None
    label_index = 0
    dropdown_index = 0

    def set_up(self, controller):
        self.controller = controller
        self.root = Tk()
        self.root.title('Caged Chord Switcher')
        self.image = None
        self.root.maxsize(width=self.width, height=self.height)
        self.root.config(padx=10, pady=10)
        self.set_theme()
        self.set_vars()
        self.get_chord()
        self.create_image()
        self.create_dropdown()
        self.create_buttons()
        self.create_labels()
        self.controller.get_hand_mode()

    def get_chord(self):
        # file_source = f'chord_images/{}'
        img_src = f'chord_images/MinorACagedShape.png'
        self.chord_image = PhotoImage(file=img_src)

    def create_image(self):
        self.image_frame = Frame(self.root, width=320, height=440)
        self.canvas = Canvas(self.image_frame, width=320, height=440, bg='#333333')
        self.image = self.canvas.create_image(self.image_width / 2, self.image_height / 2, image=self.chord_image)
        self.image_frame.grid(row=2, column=1, columnspan=3)
        self.canvas.grid(row=2, column=1, columnspan=3, padx=10, pady=10)


    def create_dropdown(self):
        self.custom_group_dropdown = ttk.Combobox(self.root, width=30)
        self.custom_group_dropdown['values'] = self.controller.group_values
        self.custom_group_dropdown.current(0)
        self.custom_group_dropdown.grid(row=0, column=1, sticky='EW')
        self.dropdown = ttk.Combobox(self.root, width=30)
        self.dropdown['values'] = [i for i in range(10, 121)]
        self.dropdown.current(50)
        self.dropdown.grid(row=3, column=1, columnspan=2, sticky='E')

    def create_labels(self):
        self.bpm_label = ttk.Label(text='BPM')
        self.bpm_label.grid(row=3, column=1, sticky='W')

    def create_buttons(self):
        self.hand_mode_var = StringVar()
        self.hand_mode_var.set(self.controller.get_hand_mode())
        self.hand_mode_btn = ttk.Button(textvariable=self.hand_mode_var, width=30, command=self.controller.toggle_hand_mode)
        self.hand_mode_btn.grid(row=6, column=1, columnspan=2, sticky='EW')
        self.ok_btn = ttk.Button(text='Ok', width=10, command=self.controller.on_ok_btn)
        self.ok_btn.grid(row=0, column=2)
        self.start_btn = ttk.Button(text='Start', width=10, command=self.controller.on_start_button)
        self.start_btn.grid(row=4, column=1, pady=10, sticky='W')
        self.stop_btn = ttk.Button(text='Stop', width=10, command=self.controller.stop_counter)
        self.stop_btn.grid(row=4, column=2, pady=10, sticky='E')

    def set_theme(self):
        self.root.tk.call('source', 'azure/azure.tcl')
        self.root.tk.call('set_theme', 'dark')

    def set_vars(self):
        self.chord_img_src = StringVar()

    def create_popup(self):
        self.p_width, self.p_height = (550, 600)
        self.index = 1
        self.window = Toplevel()
        self.window.maxsize(width=self.p_width, height=self.p_height)
        self.window.geometry(f'{self.p_width}x{self.p_height}')
        self.r_counter, self.counter = (0, 0)
        self.pp_set_right_side()
        self.pp_set_left_side()

    def pp_set_left_side(self):
        self.left_scroll = ttk.Scrollbar(self.window, orient=VERTICAL)
        self.left_scroll.grid(row=0, column=1)
        self.left_frame = ttk.Frame(self.window, height=self.p_width * .8)
        self.left_frame.grid(row=0, column=0, rowspan=5, sticky='W')
        self.left_box = Listbox(self.left_frame, width=22, height=35, selectmode='multiple')
        self.left_box_values = []
        for file in self.controller.chord_files:
            name = str(file).split('.')[0]
            s_name = re.sub(r'(?<![A-Z]\W)(?=[A-Z])', ' ', name)
            self.left_box_values.append(s_name)
        list_boxes = [self.left_box.insert(self.index, name) for name in self.left_box_values]
        self.left_box.grid(row=2, column=1, rowspan=2)

    def pp_set_right_side(self):
        PADDING = 5
        self.c_counter = 0
        self.r_counter = 1
        self.right_frame = ttk.Frame(self.window, height=self.p_height)
        self.right_frame.grid(row=0, column=2, sticky='E')
        self.right_entry = ttk.Entry(self.right_frame, width=50)
        self.right_entry.insert(0, 'name')
        self.right_entry.grid(row=4, column=0, columnspan=6, sticky='EW', padx=PADDING, pady=PADDING)
        self.numbered_labels = []

        self.add_chords_button = ttk.Button(self.right_frame, text='Add Chords', width=10,
                                            command=self.controller.pp_presave_chords)
        self.add_chords_button.grid(column=0, row=5, columnspan=6, sticky='EW', padx=PADDING, pady=PADDING)
        self.group_button = ttk.Button(self.right_frame, text='Save Group', width=10,
                                       command=self.controller.pp_save_chord_group)
        self.group_button.grid(column=0, row=6, columnspan=6, sticky='EW', padx=PADDING, pady=PADDING)

    def start_mainloop(self):
        self.root.mainloop()


c = Controller(Model(), View())
c.start_view()
