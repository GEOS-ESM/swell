import tkinter as tk
from tkinter import messagebox
import yaml

with open('setup.yaml', 'r') as yml:
    widget_dict = yaml.safe_load(yml)

# Main Application/GUI class

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        master.title('Part Manager')
        # Width height
        master.geometry("700x350")
        # Create widgets/grid
        self.entry_list = []
        self.drop_down_list = []
        for widget in widget_dict['elements']:
            self.check_widget_type(widget)
        # Make entries
        self.make_entry()
        # Create Final Buttons
        b1 = tk.Button(root, text='Generate YAML', command=self.send_to_file)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(root, text='Quit', command=root.quit)
        b2.pack(side=tk.LEFT, padx=5, pady=5)

    def send_to_file(self):
        for entry in self.entries:
            field = entry[0]
            text  = entry[1].get()
            print('%s: "%s"' % (field, text))
            
    def check_widget_type(self, widget):
        self.widget = widget['name']
        if widget['widget type'] == 'entry':
            print(self.widget)
            self.entry_list.append(self.widget)

    def make_entry(self):
        self.entries = []
        for entry in self.entry_list:
            row = tk.Frame(root)
            lab = tk.Label(row, width=15, text=entry, anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries.append((entry, ent))
        
        
    
            
root = tk.Tk()
app = Application(master=root)
app.mainloop()
