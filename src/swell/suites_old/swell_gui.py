import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yaml

with open('hofx/suite_page_hofx.yaml', 'r') as yml:
    widget_dict = yaml.safe_load(yml)

with open('hofx/experiment.yaml', 'r') as yml:
    default_exp_dict = yaml.safe_load(yml)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=500, width=550)
        scrollbar = ttk.Scrollbar(self,
                                  orient="vertical",
                                  command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class tkinterApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # Set aesthetics

        self.geometry("600x500")
        self.LARGEFONT = 18
        self.XL_FONT = 22

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


# Landing Page
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Button to go to HofX Model
        label = ttk.Label(self, text="Welcome to SWELL\n",
                          font=('Arial', controller.XL_FONT)).pack()
        label = ttk.Label(self, text="Choose a model",
                          font=('Arial', controller.LARGEFONT)).pack()
        button1 = ttk.Button(self, text="HofX",
                             command=lambda:
                             controller.show_frame(Model)).pack()


# Main Application for Model Component
class Model(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.frame = ScrollableFrame(self, width=600)

        self.widget_inputs = []
        for widget in widget_dict['elements']:
            self.check_widget_type(widget)

        # Submit Button
        submit = ttk.Button(self.frame.scrollable_frame, text='Generate YAML',
                            command=self.send_to_file)
        submit.pack(side=tk.LEFT, padx=5, pady=5)
        # Back Button
        backbutton = ttk.Button(self.frame.scrollable_frame, text="Back",
                                command=lambda:
                                controller.show_frame(StartPage))
        backbutton.pack(side=tk.LEFT, padx=5, pady=5)

        self.frame.pack()

    def send_to_file(self):
        self.yaml_dict = {}
        self.cb_dict = {}
        for widget in self.widget_inputs:
            field = widget[0]['name']
            if widget[0]['widget type'] == 'check button':
                self.check_checks(widget)
                value = self.cb_dict
            else:
                value = widget[1].get()
                self.yaml_dict[field] = value
            self.yaml_dict[field] = value
        with open('gui_experiment.yaml', 'w') as outfile:
            yaml.dump(self.yaml_dict, outfile, default_flow_style=False)

    def check_widget_type(self, widget):
        self.get_defaults(widget)
        self.widget = widget
        if widget['widget type'] == 'entry':
            self.make_entry()
        elif widget['widget type'] == 'radio button':
            self.make_radio_btn()
        elif widget['widget type'] == 'dropdown':
            self.make_dropdown()
        elif widget['widget type'] == 'check button':
            self.make_check_button()
        else:
            print('Widget not defined')

    def make_entry(self):
        row = tk.Frame(self.frame.scrollable_frame)
        lab = tk.Label(row, width=20, text=self.widget['name'], anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, self.default)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self.widget_inputs.append((self.widget, ent))

    def make_radio_btn(self):
        tk.Label(self.frame.scrollable_frame, text=self.widget['name'],
                 justify=tk.LEFT, padx=5).pack()
        v = tk.IntVar()
        v.set(1)
        options = self.widget['options']
        for option in options:
            tk.Radiobutton(self.frame.scrollable_frame,
                           text=option['name'],
                           padx=20,
                           variable=v,
                           value=option['value']).pack(anchor=tk.W)

        self.widget_inputs.append((self.widget, v))

    def make_dropdown(self):
        tk.Label(self.frame.scrollable_frame,
                 text=self.widget['name'],
                 justify=tk.LEFT,
                 padx=5).pack()
        clicked = tk.StringVar()
        clicked.set(self.widget['options'][0])
        tk.OptionMenu(self.frame.scrollable_frame,
                      clicked,
                      *self.widget['options']).pack()
        self.widget_inputs.append((self.widget, clicked))

    def make_check_button(self):
        name = self.widget.get('name', '')
        options = self.widget.get('options', [])

        lab = tk.Label(self.frame.scrollable_frame,
                       text=name,
                       justify=tk.LEFT,
                       padx=5)
        lab.pack(side=tk.TOP, anchor=tk.W)

        vlist = []
        for option in options:
            v = tk.IntVar()
            option_val = 0
            for default in self.default:
                if option in default:
                    option_val = 1
                    break
                else:
                    pass
            v.set(option_val)
            w = tk.Checkbutton(self.frame.scrollable_frame,
                               text=option,
                               variable=v)
            w.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
            vlist.append(v)

        self.widget_inputs.append((self.widget, vlist))

    def check_checks(self, check_button):
        for i, opt in enumerate(check_button[0]['options']):
            self.cb_dict[opt] = check_button[1][i].get()

    def get_defaults(self, widget):
        w_val = widget['key']
        self.default = ''
        if isinstance(w_val, dict):
            default_check = default_exp_dict
            while isinstance(w_val, dict):
                w_key = list(w_val.keys())[0]
                w_val = w_val[w_key]
                default_check = default_check[w_key]
            if isinstance(default_check, list):
                for item in default_check:
                    if w_val in item:
                        default_check = item
                        break
            self.default = default_check[w_val]
        else:
            default_check = default_exp_dict[w_val]
            self.default = default_check


# Driver Code
app = tkinterApp()
app.mainloop()
