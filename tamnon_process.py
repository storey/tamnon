# -*- coding: utf-8 -*-
# given a name such the file with that name has been preprocessed, run the
# tamnon process step on the associated files (cleaned text, form info, lemma
# info), analyzing the dialect of each token and outputing graphs an text
# files with results for overall dialect counts, rule-by-rule information,
# token-by-token results, and potentially information to evaluate tamnon
# against Perseus' Morpheus.

import sys
import tamnon_utils as t_utils
import tamnon_rules as t_rules

# ensure that the user has provided the text name and store it
if (len(sys.argv) <= 1):
    raise Exception("Please include the name of the text to use as a command line argument.")

text_name = sys.argv[1]

# get the variety of filenames to be used: first the input data, then
# the many text output files, and finally the graph files
clean_file_name = t_utils.get_text_clean_fn(text_name)
form_data_fn = t_utils.get_text_form_data_fn(text_name)
lemma_data_fn = t_utils.get_text_lemma_data_fn(text_name)

overall_results_fn = t_utils.get_text_overall_results_fn(text_name)
dialect_results_fn = t_utils.get_text_dialect_results_fn(text_name)
rule_results_fn = t_utils.get_text_rule_results_fn(text_name)
token_results_fn = t_utils.get_text_token_results_fn(text_name)
evaluation_results_fn = t_utils.get_text_evaluation_results_fn(text_name)
all_results_fn = t_utils.get_text_all_results_fn(text_name)

graph_1_fname = t_utils.get_text_graph_fn(text_name, "pct", "max", "unsorted")
graph_2_fname = t_utils.get_text_graph_fn(text_name, "pct", "min", "unsorted")
graph_3_fname = t_utils.get_text_graph_fn(text_name, "pct", "max", "sorted")
graph_4_fname = t_utils.get_text_graph_fn(text_name, "pct", "min", "sorted")
graph_5_fname = t_utils.get_text_graph_fn(text_name, "count", "max", "sorted")
graph_6_fname = t_utils.get_text_graph_fn(text_name, "count", "min", "sorted")
graph_7_fname = t_utils.get_text_graph_fn(text_name, "count_small", "max", "sorted")
graph_8_fname = t_utils.get_text_graph_fn(text_name, "count_small", "min", "sorted")
graph_fns = [graph_1_fname, graph_2_fname, graph_3_fname, graph_4_fname,
  graph_5_fname, graph_6_fname, graph_7_fname, graph_8_fname]

# get the cleaned input data
in_file = open(clean_file_name, 'r')
in_contents = in_file.read()
in_file.close()

# get the list of all tokens and unique tokens
standardized_tokens = in_contents.split(" ")
sorted_uniq_tokens = sorted(set(standardized_tokens))

input_text = (standardized_tokens, sorted_uniq_tokens)

# generate the results for the given input text, rules list, form data and lemma
# data files, and graph filenames, and telling the results generator to use the
# given files and not go directly to Morpheus for parsing, .
(overall, dialect, rule, token, evaluation) = t_utils.generate_results(input_text,
    t_rules.rules_list, form_data_fn, lemma_data_fn, graph_fns, False)

# stitch the results together for a unified output.
all_result_text = t_utils.combine_results(overall, dialect, rule, token)

# print the results to their individual files.
t_utils.safe_write(overall_results_fn, overall)
t_utils.safe_write(dialect_results_fn, dialect)
t_utils.safe_write(rule_results_fn, rule)
t_utils.safe_write(token_results_fn, token)
if (t_utils.INCLUDE_EVAL):
    t_utils.safe_write(evaluation_results_fn, evaluation)
t_utils.safe_write(all_results_fn, all_result_text)
