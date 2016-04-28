# -*- coding: utf-8 -*-
# This file is used to get all of the form and lemma info for forms used
# to test the various rules.

import json
import tamnon_utils as t_utils
import tamnon_rules as rules


out_file_name = "tests/tests_form_data.txt"
out_file_2_name = "tests/tests_lemma_data.txt"

# get all of the tokens required for test rules
test_tokens_duplicates = []
for test_rule in rules.rules_list:
    for item in test_rule["Attic_Forms"]:
        #print "attic: %s" % item[0]
        test_tokens_duplicates.append(item[0])
    for item in test_rule["Doric_Forms"]:
        #print "doric: %s" % item[0]
        test_tokens_duplicates.append(item[0])
    for item in test_rule["Either_Forms"]:
        #print "either: %s" % item[0]
        test_tokens_duplicates.append(item[0])

# get the unique tokens
sorted_uniq_tokens = sorted(set(test_tokens_duplicates))

# get the form and lemma information
lemmas = {}
results = map(t_utils.get_Perseus_data(lemmas), sorted_uniq_tokens)
print "----- Got Forms! -----"
lemma_results = t_utils.get_lemma_info(lemmas)

# save the form and lemma information
json_dump = json.dumps(results)
t_utils.safe_write(out_file_name, json_dump)

json_dump_2 = json.dumps(lemma_results)
t_utils.safe_write(out_file_2_name, json_dump_2)
