# -*- coding: utf-8 -*-
# given a name such that there is a file texts/[name].txt, run the tamnon
# preprocess step on the input file, cleaning up the data to produce the
# cleaned text, then running the Perseus Project's Morpheus morphological parser
# on each unique token and storing the form and lemma results in appropriate
# files.

import json
import tamnon_utils as t_utils
import tamnon_rules as rules
import sys

# ensure that the user has provided the text name and store it
if (len(sys.argv) <= 1):
    raise Exception("Please include the name of the text to use as a command line argument.")

text_name = sys.argv[1]

# get the necessary filenames
in_file_name = t_utils.get_text_fn(text_name)
clean_file_name = t_utils.get_text_clean_fn(text_name)
out_file_name = t_utils.get_text_form_data_fn(text_name)
out_file_2_name = t_utils.get_text_lemma_data_fn(text_name)

# read the input data
in_file = open(in_file_name, 'r')
in_contents = in_file.read()
in_file.close()

# get the list of all cleaned tokens and unique cleaned tokens
(fixed_tokens, sorted_uniq_tokens) = t_utils.clean_and_fix(in_contents)

# save the cleaned data
clean_text = " ".join(fixed_tokens)
t_utils.safe_write(clean_file_name, clean_text)


# print general information about the tokens.
print "Number of Tokens: ", len(fixed_tokens)
print "Number of Unique Tokens: ", len(sorted_uniq_tokens)


# run the morphological parse to get info for each unique token
lemmas = {}
results = map(t_utils.get_Perseus_data(lemmas), sorted_uniq_tokens)
print "----- Got Forms! -----"

# get stem information about each of the unique lemmas
lemma_results = t_utils.get_lemma_info(lemmas)

# save the form and lemma data in output files.
json_dump = json.dumps(results)
t_utils.safe_write(out_file_name, json_dump)

json_dump_2 = json.dumps(lemma_results)
t_utils.safe_write(out_file_2_name, json_dump_2)
