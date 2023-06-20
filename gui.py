import recommender

import tkinter as tk
from tkinter import filedialog, ttk
import pickle
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path
import re
from anki import collection
import os



def unpickle(): # attempt to load frequencies, knowledge, dictionary, and content from local file
    path = Path(__file__).parent
    global frequencies, knowledge, extra_knowledge, dictionary

    try: # load frequencies file
        filename = "freq.pkl"
        pickle_file = open(path/"freq.pkl", "rb")
        frequencies = pickle.load(pickle_file)
    except FileNotFoundError:
        b_import_frequencies.config(fg="red")

    try: # load knowledge file
        pickle_file = open(path/"know.pkl", "rb")
        knowledge = pickle.load(pickle_file)
    except FileNotFoundError:
        b_import_knowledge.config(fg="red")

    try: # load extra knowledge file
        pickle_file = open(path/"extra_know.pkl", "rb")
        extra_knowledge = pickle.load(pickle_file)
    except FileNotFoundError:
        extra_knowledge = []

    combine_knowledge()

    try: # load dictionary file
        pickle_file = open(path/"dict.pkl", "rb")
        dictionary = pickle.load(pickle_file)
    except FileNotFoundError:
        b_import_dictionary.config(fg="red")

    try: # load content file
        pickle_file = open(path/"cont.pkl", "rb")
        tabs = pickle.load(pickle_file)
        for content in tabs:
            add_tab(content)
    except FileNotFoundError:
        add_tab()


def add_tab(content=None):
    global tab_control

    tab = tk.Text(tab_control, font=("arial","10","normal"), height=0, width=48) # create input text widget for new tab
    tab.drop_target_register(DND_FILES)
    tab.dnd_bind("<<Drop>>", drop)

    if(content!=None):
        tab.insert("end", content)
    else:
        tab.insert("end", default_string)
    
    tab.bind("<Button-1>", on_click)
    tab.bind("<<Modified>>", on_modify_input)
    tab.pack(expand=True,fill="both")

    tab_control.add(tab, text="New Tab")

    tab_control.select(tab)

def remove_tab():
    tab = tab_control.index(tab_control.select())

    tab_control.forget(tab)
    if(len(tab_control.tabs())==0):
        add_tab()
    
    save_content()


def open_freq_file():
    global freq_window
    freq_window.attributes("-topmost", 0)
    global freq_file
    freq_file = filedialog.askopenfilename()
    freq_window.attributes("-topmost", 1)

    preview_freq_file()

def preview_freq_file(*args):
    global freq_preview
    freq_preview["state"] = "normal"
    freq_preview.delete(1.0, "end")

    global freq_col # column value must be an integer- otherwise 0
    try:
        freq = int(freq_col.get())
    except:
        freq = 0
    global word_col
    try: # column value must be an integer- otherwise 0
        word = int(word_col.get())
    except:
        word = 0
    global freq_separator
    if(freq_separator.get()!=""): # separator must not be empty- otherwise space
        separator = freq_separator.get()
    else:
        separator = " "
    global freq_start_line
    try: # start line value must be an integer- otherwise 0
        start = int(freq_start_line.get())
    except:
        start = 0
    
    try:
        file = open(freq_file, "r", encoding="utf8")
        for l, line in enumerate(file,1):
            if(l<100): # only preview first 100 lines
                if(l<start):
                    freq_preview.insert("end", line, "pre_start")
                else:
                    split = re.findall(fr'[^{separator}]+|{separator}', line) # split line by separator while keeping separator as separate entries
                    for c,col in enumerate(split):
                        if(c/2==freq):
                            freq_preview.insert("end", col, "freq_col")
                        elif(c/2==word):
                            freq_preview.insert("end", col, "word_col")
                        elif(col==separator):
                            freq_preview.insert("end", col, "freq_separator")
                        else:
                            freq_preview.insert("end", col)
        freq_preview.insert("end", "Preview truncated to first 100 lines.")
    except NameError:
        return
    
    freq_preview.tag_config("pre_start", foreground="gray80")
    freq_preview.tag_config("freq_col", foreground="blue")
    freq_preview.tag_config("word_col", foreground="red")
    freq_preview.tag_config("freq_separator", background="green")

    freq_preview["state"] = "disabled"

def submit_import_frequencies(freq_filename,word_col,freq_col,separator,freq_start_line,ascending):
    global frequencies
    frequencies = recommender.import_frequencies(freq_filename, word_col, freq_col, separator, freq_start_line, ascending)
    global freq_window
    freq_window.destroy()

    b_import_frequencies.config(fg="black")

    path = Path(__file__).parent
    pickle_file = open(path/"freq.pkl", 'wb') # pickle and write to file
    pickle.dump(frequencies, pickle_file)

def import_frequencies():
    global freq_window
    freq_window = tk.Toplevel(root)
    freq_window.title("Manage Frequencies")
    freq_window.minsize(340, 293)

    tk.Button(freq_window, text="Select File", command=open_freq_file).pack(fill="x")

    global freq_preview
    freq_preview = tk.Text(freq_window, font=("arial","10","normal"), height=8, width=48)
    freq_preview.pack(expand=True, fill="both")
    freq_preview["state"] = "disabled"

    order = tk.Frame(freq_window)
    order.grid_columnconfigure(0, weight=1)
    order.grid_columnconfigure(1, weight=1)
    order.grid_columnconfigure(2, weight=1)
    global freq_ascending
    freq_ascending = tk.BooleanVar()
    tk.Label(order, text="Frequency Order:").grid(row=0,column=0)
    tk.Radiobutton(order, text="Ascending", variable=freq_ascending, value=1).grid(row=0,column=1)
    tk.Radiobutton(order, text="Descending", variable=freq_ascending, value=0).grid(row=0,column=2)

    properties = tk.Frame(freq_window)
    properties.grid_columnconfigure(0, weight=1)
    properties.grid_columnconfigure(1, weight=1)

    global freq_start_line
    freq_start_line = tk.IntVar()
    freq_start_line.set(1)
    freq_start_line.trace_add('write', preview_freq_file)
    tk.Label(properties, text="Start Line:").grid(row=0,column=0, sticky="e")
    tk.Entry(properties, textvariable=freq_start_line, width=16).grid(row=0,column=1, sticky="nsew")
    
    global freq_separator
    freq_separator = tk.StringVar()
    freq_separator.set(",")
    freq_separator.trace_add('write', preview_freq_file)
    tk.Label(properties, text="Separator:", fg="green").grid(row=1,column=0, sticky="e")
    tk.Entry(properties, textvariable=freq_separator, width=16).grid(row=1,column=1, sticky="nsew")

    global freq_col
    freq_col = tk.IntVar()
    freq_col.set(0)
    freq_col.trace_add('write', preview_freq_file)
    tk.Label(properties, text="Frequency Column:", fg="blue").grid(row=2,column=0, sticky="e")
    tk.Entry(properties, textvariable=freq_col, width=16).grid(row=2,column=1, sticky="nsew")

    global word_col
    word_col = tk.IntVar()
    word_col.set(1)
    word_col.trace_add('write', preview_freq_file)
    tk.Label(properties, text="Word Column:", fg="red").grid(row=3,column=0, sticky="e")
    tk.Entry(properties, textvariable=word_col, width=16).grid(row=3,column=1, sticky="nsew")

    global freq_file
    tk.Button(freq_window, text="Import Frequencies", command=lambda:submit_import_frequencies(freq_file,word_col.get(),freq_col.get(),freq_separator.get(),freq_start_line.get(),freq_ascending.get())).pack(fill="x",side="bottom")
    
    properties.pack(fill="x", side="bottom")
    order.pack(fill="x", side="bottom")

def save_content():
    tabs = []
    for tab in tab_control.tabs(): # create list of tab contents
        tab_widget = root.nametowidget(tab)
        tabs.append(tab_widget.get("1.0","end-1c"))
    
    path = Path(__file__).parent
    pickle_file = open(path/"cont.pkl", 'wb') # pickle and write to file
    pickle.dump(tabs, pickle_file)

def open_know_file():
    global know_window
    know_window.attributes("-topmost", 0)
    global know_file
    know_file = filedialog.askopenfilename()
    know_window.attributes("-topmost", 1)

    if(know_format.get()=="anki"): # duplicates collection file to avoid interference
        path = Path(__file__).parent
        with open(know_file, "rb") as f_src:
            data = f_src.read()
        know_file = str(path/"collection.anki2")
        with open(know_file, "wb") as f_dst:
            f_dst.write(data)

        anki_knowledge() # unlock property menus upon collection import

    preview_know_file()

def preview_know_file(*args):
    global know_preview
    know_preview["state"] = "normal"
    know_preview.delete(1.0, "end")

    try: # know_col and know_separator only exist if tabular
        global know_col # column value must be an integer- otherwise 0
        try:
            know = int(know_col.get())
        except:
            know = 0
        global know_separator
        if(know_separator.get()!=""): # separator must not be empty- otherwise space
            separator = know_separator.get()
        else:
            separator = " "
    except:
        pass
    global know_start_line
    try: # start line value must be an integer- otherwise 0
        start = int(know_start_line.get())
    except:
        start = 0
    
    try:
        if(know_file.split(".")[-1]=="anki2"): # preview anki file
            col = collection.Collection(know_file)
            note_ids = col.find_notes(f"deck:{anki_deck.get()}") # gets note ids of deck
            i=0
            for note_id in note_ids:
                note = col.get_note(note_id) # get note of note id
                if anki_field.get() in note:
                    if(i<100):
                        know_preview.insert("end", note[anki_field.get()]+"\n", "know_col")
                        i+=1
            if(i==100):
                know_preview.insert("end", "Preview truncated to first 100 entries.")

        else: # preview standard data
            file = open(know_file, "r", encoding="utf8")
            for l, line in enumerate(file,1):
                if(l<100): # only preview first 100 lines
                    if(l<start): # grey out lines before start line
                        know_preview.insert("end", line, "pre_start")
                    else:
                        if(know_format.get()=="tabular"): # selectively highlight sections of tabular data
                            split = re.findall(fr'[^{separator}]+|{separator}', line) # split line by separator while keeping separator as separate entries
                            for c,col in enumerate(split):
                                if(c/2==know):
                                    know_preview.insert("end", col, "know_col")
                                elif(col==separator):
                                    know_preview.insert("end", col, "know_separator")
                                else:
                                    know_preview.insert("end", col)
                        elif(know_format.get()=="full"): # highlight all text
                            know_preview.insert("end", line, "know_col")
            know_preview.insert("end", "Preview truncated to first 100 lines.")
    except NameError:
        return

    know_preview.tag_config("pre_start", foreground="gray80")
    know_preview.tag_config("know_col", foreground="blue")
    know_preview.tag_config("know_separator", background="green")

    know_preview["state"] = "disabled"

def submit_import_knowledge(filename, format, start_line=None, col=None, separator=None, deck=None, field=None):
    global knowledge
    knowledge = recommender.import_knowledge(filename, format, start_line=start_line, col=col, separator=separator, deck=deck, field=field)
    if(format=="anki"): # removes the copied anki collection file after import
        os.remove(know_file)
    combine_knowledge()
    generate_recommendations()

    global know_window
    know_window.destroy()
    b_import_knowledge.config(fg="black")

    path = Path(__file__).parent
    pickle_file = open(path/"know.pkl", 'wb') # pickle and write to file
    pickle.dump(knowledge, pickle_file)

def full_knowledge():
    global know_properties
    for child in know_properties.winfo_children(): # reinstantiate properties frame
        child.destroy()

    global know_start_line
    tk.Label(know_properties, text="Start Line:").grid(row=0,column=0, sticky="e")
    tk.Entry(know_properties, textvariable=know_start_line, width=16).grid(row=0,column=1, sticky="nsew")

    preview_know_file()

def tabular_knowledge():
    global know_properties
    for child in know_properties.winfo_children(): # reinstantiate properties frame
        child.destroy()
    
    global know_start_line
    tk.Label(know_properties, text="Start Line:").grid(row=0,column=0, sticky="e")
    tk.Entry(know_properties, textvariable=know_start_line, width=16).grid(row=0,column=1, sticky="nsew")

    global know_separator
    tk.Label(know_properties, text="Separator:", fg="green").grid(row=1,column=0, sticky="e")
    tk.Entry(know_properties, textvariable=know_separator, width=16).grid(row=1,column=1, sticky="nsew")

    global know_col
    tk.Label(know_properties, text="Knowledge Column:", fg="blue").grid(row=2,column=0, sticky="e")
    tk.Entry(know_properties, textvariable=know_col, width=16).grid(row=2,column=1, sticky="nsew")

    preview_know_file()

def anki_knowledge_field(event):
    global anki_deck
    field_choices = []

    anki_field.set("") # initialise field menu as disabled incase no fields exist within deck
    global field_menu
    field_menu.config(state="disabled")

    col = collection.Collection(know_file)
    note_ids = col.find_notes(f"deck:{anki_deck.get()}") # gets note ids of deck
    for note_id in note_ids:
        note = col.get_note(note_id) # get note of note id
        field_names = [field['name'] for field in col.models.get(note.mid)['flds']] # get field names of note
        for name in field_names: # get all potential field names of deck
            if(name not in field_choices):
                field_choices.append(name)
    
    if(field_choices!=[]): # keep field menu disabled if no fields in deck
        # fill menu with deck fields
        field_menu.destroy()
        field_menu = tk.OptionMenu(know_properties, anki_field, *field_choices, command=preview_know_file)
        field_menu.grid(row=1,column=1, sticky="nsew")


def anki_knowledge():
    global know_properties
    for child in know_properties.winfo_children(): # reinstantiate properties frame
        child.destroy()
    
    tk.Label(know_properties, text="Deck:").grid(row=0,column=0, sticky="e")
    tk.Label(know_properties, text="Field:").grid(row=1,column=0, sticky="e")

    try: # fill menu with decks in collection
        deck_choices = []

        col = collection.Collection(know_file)
        decks = col.decks.all_ids()
        for deck in decks:
            deck_choices.append(col.decks.get(deck)["name"])
        
        global anki_deck
        deck_menu = tk.OptionMenu(know_properties, anki_deck, *deck_choices, command=anki_knowledge_field)
        deck_menu.grid(row=0,column=1, sticky="nsew")

    except: # disabled deck menu if no file
        deck_menu = tk.OptionMenu(know_properties, None, [""])
        deck_menu.grid(row=0,column=1, sticky="nsew")
        deck_menu.config(state="disabled")
    
    global anki_field # field menu disabled until deck selection made
    global field_menu
    field_menu = tk.OptionMenu(know_properties, anki_field, [""])
    field_menu.grid(row=1,column=1, sticky="nsew")
    field_menu.config(state="disabled")

def import_knowledge():
    global know_start_line
    know_start_line = tk.IntVar()
    know_start_line.set(1)
    know_start_line.trace_add('write', preview_know_file)
    global know_col
    know_col = tk.IntVar()
    know_col.set(0)
    know_col.trace_add('write', preview_know_file)
    global know_separator
    know_separator = tk.StringVar()
    know_separator.set("	")
    know_separator.trace_add('write', preview_know_file)
    global anki_deck
    anki_deck = tk.StringVar()
    global anki_field
    anki_field = tk.StringVar()
    
    global know_window
    know_window = tk.Toplevel(root)
    know_window.title("Manage Knowledge")
    know_window.minsize(340, 273)
    
    tk.Button(know_window, text="Select File", command=open_know_file).pack(fill="x")

    global know_preview
    know_preview = tk.Text(know_window, font=("arial","10","normal"), height=8, width=48)
    know_preview.pack(expand=True, fill="both")
    know_preview["state"] = "disabled"
    
    format = tk.Frame(know_window)
    format.grid_columnconfigure(0, weight=1)
    format.grid_columnconfigure(1, weight=1)
    format.grid_columnconfigure(2, weight=1)
    format.grid_columnconfigure(3, weight=1)

    global know_format
    know_format = tk.StringVar()
    know_format.set("full")
    tk.Label(format, text="Knowledge Format:").grid(row=0,column=0)
    tk.Radiobutton(format, text="Full", variable=know_format, value="full", command=full_knowledge).grid(row=0,column=1)
    tk.Radiobutton(format, text="Tabular", variable=know_format, value="tabular", command=tabular_knowledge).grid(row=0,column=2)
    tk.Radiobutton(format, text="Anki", variable=know_format, value="anki", command=anki_knowledge).grid(row=0,column=3)

    global know_properties
    know_properties = tk.Frame(know_window)
    know_properties.grid_columnconfigure(0, weight=1)
    know_properties.grid_columnconfigure(1, weight=1)

    global know_file
    tk.Button(know_window, text="Import Knowledge", command=lambda:submit_import_knowledge(know_file, know_format.get(), know_start_line.get(), know_col.get(), know_separator.get(), anki_deck.get(), anki_field.get())).pack(fill="x",side="bottom")
    know_properties.pack(fill="x", side="bottom")
    format.pack(fill="x", side="bottom")

    full_knowledge()

def import_dictionary():
    dict_file = filedialog.askopenfilename()
    global dictionary
    dictionary = recommender.import_dictionary(dict_file)

    b_import_dictionary.config(fg="black")

    path = Path(__file__).parent
    pickle_file = open(path/"dict.pkl", 'wb') # pickle and write to file
    pickle.dump(dictionary, pickle_file)

def set_tab_name(widget):
    content = widget.get("1.0","end-1c")
    if(content!="" and content!=default_string):
        tab_control.tab(widget, text=content.split("\n")[0][0:4]) # title is first 4 characters of first line
    else:
        tab_control.tab(widget, text="New Tab")



def drop(event):
    file_path = event.data

    input = root.nametowidget(tab_control.select())

    input.delete(1.0, "end")

    file = open(file_path, "r", encoding="utf8")
    text = file.read()
    input.insert("end", text)
    
    set_tab_name(event.widget)
    save_content()
    generate_recommendations()

def on_click(event):
    input = root.nametowidget(tab_control.select())
    if(input.get("1.0","end-1c")==default_string):
        input.delete(1.0, "end")

def on_modify_input(event):
    event.widget.edit_modified(False)

    set_tab_name(event.widget)
    save_content()
    generate_recommendations()

def on_modify_pos(event):
    event.widget.edit_modified(False)

    generate_recommendations()

def reset_pos():
    global default_pos

    pos_filter_input.delete(1.0, "end")
    pos_filter_input.insert("end", default_pos)

def generate_recommendations(event=None):
    global recommendations

    global frequencies
    global knowledge
    global dictionary

    pos_filter = pos_filter_input.get("1.0","end-1c").split("\n")

    if(global_gen.get()==True): # combine content of every tab
        input_text = ""
        for tab in tab_control.tabs():
            tab_widget = root.nametowidget(tab)
            if(tab_widget.get("1.0","end-1c")!=default_string):
                input_text += tab_widget.get("1.0","end-1c") + "\n"
        content = recommender.import_content(content_string=input_text)
    
    else: # pull content from current tab
        input_text = root.nametowidget(tab_control.select()).get("1.0","end-1c")
        content = recommender.import_content(content_string=input_text)

    try:
        recommendations = recommender.generate_recommendations(filter_katakana.get(), pos_filter, frequencies, knowledge, content, dictionary)
        print(recommendations)
        output_recommendations()
    except NameError:
        return

def combine_knowledge():
    for item in extra_knowledge:
        knowledge.append(item)
    return

def add_knowledge(selection):
    if(selection not in knowledge):
        extra_knowledge.append(selection)

        path = Path(__file__).parent
        pickle_file = open(path/"extra_know.pkl", 'wb') # pickle and write to file
        pickle.dump(extra_knowledge, pickle_file)

        combine_knowledge()
        position = output.yview()[0]
        generate_recommendations()
        output.yview("moveto", position)

def show_menu(event):
    try:
        start = output.index("sel.first")
        end = output.index("sel.last")
        selection = output.get(start,end)
        if(selection in dictionary):
            popup = tk.Menu(root, tearoff=0)
            popup.add_command(label="Add  '"+selection+"'", command=lambda: add_knowledge(selection))
            popup.post(event.x_root, event.y_root)
    except:
        pass

def output_recommendations():
    global recommendations

    display = {
    "Frequency Ranking":display_freq.get(),
    "Part of Speech":display_pos.get(),
    "Source Sentences":display_sentences.get(),
    "Definition":display_definition.get(),
    }

    output["state"] = "normal"
    output.delete(1.0, "end")

    for r, rec in enumerate(recommendations.items(),1):
        output.insert("end", str(r) + " ", "standard")
        output.insert("end", rec[0] + "\n", "title")

        if(display["Frequency Ranking"]):
            output.insert("end", "Frequency Ranking: ", "bold")
            output.insert("end", str(format(rec[1]["freq"],".3f")) + "\n", "standard")

        if(display["Part of Speech"]):
            output.insert("end", "Part of Speech: ", "bold")
            output.insert("end", rec[1]["pos"] + "\n", "standard")

        if(display["Definition"]):
            output.insert("end", "Definition: " + "\n", "bold")
            for d, definition in enumerate(rec[1]["def"],1):
                if(definition["reading"]!=""):
                    reading = "(" + definition["reading"] + ")  "
                else:
                    reading = ""
                
                output.insert("end", "  " + str(d) + "  " + reading + ", ".join(definition["content"]) + "\n", "standard")

        if(display["Source Sentences"]):
            output.insert("end", "Source Sentences: " + "\n", "bold")

            for s, sentence in enumerate(rec[1]["sent"],1):
                output.insert("end", "  " + str(s) + "  ", "standard")
                string_index = 0
                for word_indices in rec[1]["sent"][sentence]:
                    output.insert("end",sentence[string_index:word_indices[0]], "standard")
                    output.insert("end",sentence[word_indices[0]:word_indices[1]], "word")
                    string_index = word_indices[1]
                output.insert("end",sentence[string_index:] + "\n", "standard")


        output.insert("end", "\n")

    if(len(recommendations.items())==0):
        output.insert("end", default_output)

    output.tag_config("standard", font=("arial","10","normal"))
    output.tag_config("title", font=("arial","14","bold"))
    output.tag_config("bold", font=("arial","10","bold"))
    output.tag_config("word", font=("arial","10","normal"), background="yellow")
    
    output["state"] = "disabled"



root = TkinterDnD.Tk()
root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.title("TangoRec")
root.minsize(root.winfo_width(), 335)


toolbar = tk.Frame(root)
toolbar.grid(row=0, column=0, sticky="nsew")

display_frame = tk.LabelFrame(toolbar, text="Display")
display_frame.pack(fill="x")

display_freq = tk.IntVar(value=1)
tk.Checkbutton(display_frame, text="Frequency Ranking", variable=display_freq, command=output_recommendations).pack(anchor="w")
display_pos = tk.IntVar(value=0)
tk.Checkbutton(display_frame, text="Part of Speech", variable=display_pos, command=output_recommendations).pack(anchor="w")
display_definition = tk.IntVar(value=1)
tk.Checkbutton(display_frame, text="Definition", variable=display_definition, command=output_recommendations).pack(anchor="w")
display_sentences = tk.IntVar(value=1)
tk.Checkbutton(display_frame, text="Source Sentences", variable=display_sentences, command=output_recommendations).pack(anchor="w")
filter_katakana = tk.IntVar(value=0)
tk.Checkbutton(toolbar, text="Filter Katakana", variable=filter_katakana, command=generate_recommendations).pack(anchor="w")

default_pos = "感動詞\n補助記号\n助詞\n記号"
pos_frame = tk.LabelFrame(toolbar, text="Part-of-Speech Filter")
pos_frame.pack(expand=True,fill="both")
b_default_pos = tk.Button(pos_frame,text="Default",command=reset_pos)
b_default_pos.pack(fill="x")
pos_filter_input = tk.Text(pos_frame, width=0, height=4)
pos_filter_input.insert("end", default_pos)
pos_filter_input.pack(expand=True,fill="both")
pos_filter_input.bind("<<Modified>>", on_modify_pos)



input_output = tk.PanedWindow(root, orient="horizontal")
input_output.grid(row=0, column=1, sticky="nsew")

input = tk.Frame(input_output)
default_string = "Write text or drop a file here."
default_output = "Generated recommendations will appear here.\nSelect and right click a word to add it to your knowledge."

tab_option = tk.Frame(input)
tab_option.grid_columnconfigure(0, weight=1)
tab_option.grid_columnconfigure(1, weight=1)
tab_option.grid_columnconfigure(2, weight=0)
tab_option.grid_columnconfigure(3, weight=0)
tab_option.grid_columnconfigure(4, weight=0)
tab_option.pack(fill="x")


new_tab = tk.Button(tab_option, text="New Tab", command=add_tab).grid(row=0,column=0, sticky="ew")
remove_tab = tk.Button(tab_option, text="Remove Tab", command=remove_tab).grid(row=0,column=1, sticky="ew")
tk.Label(tab_option, text="Generation:").grid(row=0,column=2)
global_gen = tk.BooleanVar()
tk.Radiobutton(tab_option, text="Tab-specific", variable=global_gen, value=0, command=generate_recommendations).grid(row=0,column=3)
tk.Radiobutton(tab_option, text="Global", variable=global_gen, value=1, command=generate_recommendations).grid(row=0,column=4)

output = tk.Text(input_output, font=("arial","10","normal"), height=0, width=96)
output["state"] = "disabled"
output.bind("<Button-3>", show_menu)

input_output.add(input)
input_output.add(output)

tab_control = ttk.Notebook(input)
tab_control.pack(expand=True,fill="both")
tab_control.bind("<<NotebookTabChanged>>", generate_recommendations)

b_import_frequencies = tk.Button(toolbar, text="Manage Frequencies", command=import_frequencies)
b_import_frequencies.pack(fill="x")

b_import_knowledge = tk.Button(toolbar, text="Manage Knowledge", command=import_knowledge)
b_import_knowledge.pack(fill="x")

b_import_dictionary = tk.Button(toolbar, text="Manage Dictionary", command=import_dictionary)
b_import_dictionary.pack(fill="x")

unpickle()

root.mainloop()