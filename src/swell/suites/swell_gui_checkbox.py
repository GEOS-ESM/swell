import tkinter as tk
from tkinter import messagebox
import yaml

with open('setup.yaml', 'r') as yml:
    widget_dict = yaml.safe_load(yml)

# Main Application/GUI class


class WidgetManager(tk.Frame):

    def __init__(self, title, master=None):

        if master is None: master = tk.Tk()
        self.master = master
        root = master

        super().__init__(root)

        self.root.title(title)
        self.root.geometry("700x350")
        
        self.entries = []

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

    def make_entry(self, widget):
        root = self.master
        name = widget['name']
        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=name, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        self.widgets.append((name, ent))

    def make_checkbox(self, widget):

        root = self.master
        name = widget.get('name', '')
        options = widget.get('options', [])
        default = widget.get('default', [])

        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=name, anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)

        for option in options:
            v = tk.IntVar()
            if option in default: v.set(1)
            w = tk.Checkbutton(root, text=option, variable=v)
            w.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            self.widgets.append((name, w))

    def create_widget(self, widget):

        widget_type = widget.get('widget type', 'entry')

        if widget_type == 'entry':
            self.make_entry(widget)
        elif widget_type == 'checkbox':
            self.make_checkbox(widget)

with open('setup.yaml', 'r') as yml:
    widget_dict = yaml.safe_load(yml)

root = tk.Tk()
atmos_page = WidgetManager('Atmosphere', master=root)

for widget in widget_dict['elements']:
    atmos_page.create_widget(widget)

atmos_page.mainloop()
