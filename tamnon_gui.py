# -*- coding: utf-8 -*-
# this file defines the GUI form of tamnon, which allows a user to place
# input text in the top textarea and see the results in the bottom textarea.
# it optionally takes a commandline argument specifying the name of a
# preprocessed input text (for example, if a user wants to look at specific
# parts of the work of Pindar and has already run a preprocess for her entire
# corpus).
import ttk
import tamnon_utils as t_utils
import tamnon_rules as t_rules
import sys

# if the user has provided preprocessed information, use that information,
# otherwise note that we will be getting data straight from perseus.
if (len(sys.argv) > 1):
    FROM_PERSEUS = False
    text_name = sys.argv[1]
    form_fn = t_utils.get_text_form_data_fn(text_name)
    lemma_fn = t_utils.get_text_lemma_data_fn(text_name)
else:
    FROM_PERSEUS = True
    form_fn = ""
    lemma_fn = ""


class App:
    # this function takes the input text from the top textarea and runs a
    # tamnon analysis of it, outputting the result in the bottom textarea.
    def handle_text(self):
        user_text = self.in_text.get('1.0', ttk.Tkinter.END)
        cleaned_text = t_utils.clean_and_fix(user_text)
        (overall, dialect, rule, token, evaluation) = t_utils.generate_results(cleaned_text,
            t_rules.rules_list, form_fn, lemma_fn, [], FROM_PERSEUS)
        if (t_utils.INCLUDE_EVAL):
            result_text = t_utils.combine_results_eval(overall, dialect, rule, token, evaluation)
        else:
            result_text = t_utils.combine_results(overall, dialect, rule, token)
        self.out_text.delete('1.0', ttk.Tkinter.END)
        self.out_text.insert("1.0", result_text)

    # this function clears the text
    def clear_text(self):
        self.in_text.delete('1.0', ttk.Tkinter.END)

    # create the GUI with the two different textareas and appropriate buttons.
    def __init__(self, master):
        if (True):
            out_padding = 20
            in_padding = 5

            top_frame = ttk.Frame(master)
            top_frame.pack()

            frame = ttk.Frame(top_frame)
            frame.pack(padx=out_padding, pady=out_padding)

            self.result_string = ttk.Tkinter.StringVar()

            self.in_text_yscroll = ttk.Scrollbar(frame)
            self.in_text_yscroll.grid(column=3, row=1, sticky=ttk.Tkinter.N+ttk.Tkinter.S)

            self.in_text = ttk.Tkinter.Text(frame, wrap=ttk.Tkinter.WORD, yscrollcommand=self.in_text_yscroll.set)
            self.in_text.grid(column=1, columnspan=2, row=1)

            self.in_text_yscroll.config(command=self.in_text.yview)
            #text_widget.configure(state="disabled")

            self.hi_there = ttk.Button(frame, text="Clear", command=self.clear_text)
            self.hi_there.grid(column=1, row=2, pady=in_padding)

            self.hi_there = ttk.Button(frame, text="Analyze", command=self.handle_text)
            self.hi_there.grid(column=2, columnspan=2, row=2, pady=in_padding)

            #self.result_text = Label(frame, textvariable=self.result_string)
            #self.result_text.grid(column=1, columnspan=2, row=3, pady=in_padding)
            self.out_text_yscroll = ttk.Scrollbar(frame)
            self.out_text_yscroll.grid(column=3, row=3, sticky=ttk.Tkinter.N+ttk.Tkinter.S)

            self.out_text = ttk.Tkinter.Text(frame, wrap=ttk.Tkinter.WORD, yscrollcommand=self.out_text_yscroll.set)
            self.out_text.grid(column=1, columnspan=2, row=3)

            self.out_text_yscroll.config(command=self.out_text.yview)


# main app initialization
root = ttk.Tkinter.Tk()

app = App(root)
root.mainloop()
