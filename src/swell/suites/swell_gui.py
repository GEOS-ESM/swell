import tkinter as tk
from tkinter import messagebox
import yaml

with open('hofx/suite_page_hofx.yaml', 'r') as yml:
    widget_dict = yaml.safe_load(yml)

# Main Application/GUI class


class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        master.title('Experiment Setup')
        # Width height
        master.geometry("700x350")
        # Create widgets/grid
        self.entry_list = []
        self.dropdown_list = []
        self.radio_btn_list = []
        self.check_btn_list = []
        for widget in widget_dict['elements']:
            self.check_widget_type(widget)
        # Make entries
        self.make_entries()
        # Make radio buttons
        self.make_radio_btns()
        # Make drop downs
        self.make_dropdowns()
        # Make check buttons
        self.make_check_btns()

        # Create Final Buttons
        b1 = tk.Button(root, text='Generate YAML', command=self.send_to_file)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(root, text='Quit', command=root.quit)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

    def send_to_file(self):
        for entry in self.entries:
            field = entry[0]
            text = entry[1].get()
            print('%s: "%s"' % (field, text))
        for radio_btn in self.radio_btns:
            field = radio_btn[0]
            value = radio_btn[1].get()
            print('%s: "%s"' % (field, value))
        for dropdown in self.dropdowns:
            field = dropdown[0]
            value = dropdown[1].get()
            print('%s: "%s"' % (field, value))

    def check_widget_type(self, widget):
        self.widget = widget
        if widget['widget type'] == 'entry':
            self.entry_list.append(self.widget)
        elif widget['widget type'] == 'radio button':
            self.radio_btn_list.append(self.widget)
        elif widget['widget type'] == 'dropdown':
            self.dropdown_list.append(self.widget)
        elif widget['widget type'] == 'check button':
            self.check_btn_list.append(self.widget)
        else:
            print('Widget not defined')

    def make_entries(self):
        self.entries = []
        for entry in self.entry_list:
            row = tk.Frame(root)
            lab = tk.Label(row, width=15, text=entry['name'], anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries.append((entry['name'], ent))

    def make_radio_btns(self):
        self.radio_btns = []
        for radio_btn in self.radio_btn_list:
            tk.Label(root,
                text=radio_btn['name'],
                justify = tk.LEFT,
                padx = 5).pack()
            v = tk.IntVar()
            v.set(1)
            options = radio_btn['options']
            print(options)
            for option in options:
                tk.Radiobutton(root,
                    text=option['name'],
                    padx = 20,
                    variable=v,
                    value=option['value']).pack(anchor=tk.W)

            self.radio_btns.append((radio_btn['name'], v))

    def make_dropdowns(self):
        self.dropdowns = []
        for dropdown in self.dropdown_list:
            tk.Label(root,
                text=dropdown['name'],
                justify = tk.LEFT,
                padx = 5).pack()

            clicked = tk.StringVar()
            clicked.set( dropdown['options'][0] )
            tk.OptionMenu(root , clicked , *dropdown['options']).pack()

            self.dropdowns.append((dropdown['name'], clicked))

    def make_check_btns(self):
        self.check_btns = []




root = tk.Tk()
app = Application(master=root)
app.mainloop()
