import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yaml

with open('hofx/suite_page_hofx.yaml', 'r') as yml:
    widget_dict = yaml.safe_load(yml)

LARGEFONT = 14


class tkinterApp(tk.Tk):
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.geometry("800x350")

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, Model):
            frame = F(container, self)
            # initializing frame of that object from
            # startpage, page1, page2 respectively with for loop
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# first window frame startpage


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Button to go to HofX Model
        label = ttk.Label(self, text="Startpage", font=LARGEFONT).pack()
        button1 = ttk.Button(self, text="HofX",
                             command=lambda: controller.show_frame(Model)).pack()


# Main Application for Model Component

class Model(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Create widgets/grid
        self.entry_list = []
        self.drop_down_list = []
        for widget in widget_dict['elements']:
            self.check_widget_type(widget)
        # controller.geometry('1000x500')
        # Make entries
        self.make_entry(parent)
        # Submit Button
        submit = ttk.Button(self, text='Generate YAML', command=self.send_to_file)
        submit.pack(side=tk.LEFT, padx=5, pady=5)
        # Back Button
        backbutton = ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage))
        backbutton.pack(side=tk.LEFT, padx=5, pady=5)
        # quit = tk.Button(self, text='Quit', command=self.quit)
        # quit.pack(side=tk.LEFT, padx=5, pady=5)

    def send_to_file(self):
        for entry in self.entries:
            field = entry[0]
            text = entry[1].get()
            print('%s: "%s"' % (field, text))

    def check_widget_type(self, widget):
        self.widget = widget['name']
        if widget['widget type'] == 'entry':
            self.entry_list.append(self.widget)

    def make_entry(self):
        self.entries = []  # Move this up and make a master list of all widget values/selections
        for entry in self.entry_list:
            row = tk.Frame(self)
            lab = tk.Label(row, width=15, text=entry, anchor='w')
            ent = tk.Entry(row, textvariable=tk.StringVar())
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries.append((entry, ent))


# Driver Code
app = tkinterApp()
app.mainloop()
