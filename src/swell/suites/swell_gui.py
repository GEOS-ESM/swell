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
        self.widget_inputs = []
        for widget in widget_dict['elements']:
            self.check_widget_type(widget)

        # Submit Button
        submit = ttk.Button(self, text='Generate YAML', command=self.send_to_file)
        submit.pack(side=tk.LEFT, padx=5, pady=5)
        # Back Button
        backbutton = ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage))
        backbutton.pack(side=tk.LEFT, padx=5, pady=5)

    def send_to_file(self):
        for widget in self.widget_inputs:
            field = widget[0]['name']
            value = widget[1].get()
            print('%s: "%s"' % (field, value))

    def check_widget_type(self, widget):
        self.widget = widget
        if widget['widget type'] == 'entry':
            self.make_entry()
        elif widget['widget type'] == 'radio button':
            self.make_radio_btn()
        elif widget['widget type'] == 'dropdown':
            self.make_dropdown()
        else:
            print('Widget not defined')

    def make_entry(self):
        row = tk.Frame(self)
        lab = tk.Label(row, width=15, text=self.widget['name'], anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self.widget_inputs.append((self.widget, ent))

    def make_radio_btn(self):
        tk.Label(self,
            text=self.widget['name'],
            justify = tk.LEFT,
            padx = 5).pack()
        v = tk.IntVar()
        v.set(1)
        options = self.widget['options']
        for option in options:
            tk.Radiobutton(self,
                text=option['name'],
                padx = 20,
                variable=v,
                value=option['value']).pack(anchor=tk.W)

        self.widget_inputs.append((self.widget, v))


    def make_dropdown(self):
        tk.Label(self,
            text=self.widget['name'],
            justify = tk.LEFT,
            padx = 5).pack()

        clicked = tk.StringVar()
        clicked.set( self.widget['options'][0] )
        tk.OptionMenu(self, clicked , *self.widget['options']).pack()
        self.widget_inputs.append((self.widget, clicked))


# Driver Code
app = tkinterApp()
app.mainloop()
