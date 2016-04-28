# -*- coding: utf-8 -*-
# This file runs the tests for each of the rules. Make sure to run
# tamnon_get_test_forms.py first.

import json
import tamnon_utils as t_utils
import tamnon_rules as rules

# get the form and lemma data for the given set of (unique) tokens
def get_form_data(token_list):
    form_info_file_name = "tests/tests_form_data.txt"
    form_info_file = open(form_info_file_name, 'r')
    form_info_contents = form_info_file.read()
    form_info_file.close()
    form_info = json.loads(form_info_contents)

    lemma_info_file_name = "tests/tests_lemma_data.txt"
    lemma_info_file = open(lemma_info_file_name, 'r')
    lemma_info_contents = lemma_info_file.read()
    lemma_info_file.close()
    lemma_info = json.loads(lemma_info_contents)

    form_info_dict = {}
    for fi in form_info:
        form = fi[0]
        parses = fi[1]
        if (form in token_list):
            form_info_dict[form] = parses
    return (form_info_dict, lemma_info)

# given a token, information about the token, information about the lemmas,
# the index of the parse to examine (-1 for all of them), the function that
# tests for whether a rule applies to the given token, the name of the rule,
# and the dialect that the tester should return, make sure that the rule
# tester returns the correct result.
def test_token(token, token_info, lemma_info, index, tester, rule_name, target_dialect):
    # get the parses we are examining; if index is -1, all of them, otherwise
    # just the parse at index index.
    if (index == -1):
        form_info = token_info[0]
    else:
        form_info = [token_info[0][index]]

    # store the dialects and reasons for each parse.
    parse_dialects = []
    for i in range(len(form_info)):
        parse_dialects.append({"attic": False, "doric": False, "att_rsn": [], "dor_rsn": []})

    r_some_Doric = False
    r_some_Attic = False
    r_all_Doric = True
    r_all_Attic = True
    r_all_judged = True

    # for each parse, determine what dialects the tester thinks the parse is.
    for i in range(len(form_info)):
        parse = form_info[i]
        info = [parse, lemma_info[parse["lemma"]]]
        res = tester(info)
        if (res == t_utils.ATTIC):
            r_some_Attic = True
            r_all_Doric = False
            parse_dialects[i]["attic"] = True
            parse_dialects[i]["att_rsn"].append(rule_name)
        elif (res == t_utils.DORIC):
            r_some_Doric = True
            r_all_Attic = False
            parse_dialects[i]["doric"] = True
            parse_dialects[i]["dor_rsn"].append(rule_name)
        else:
            r_all_Doric = False
            r_all_Attic = False
            r_all_judged = False

    text = "%s:\n" % (token)
    tab = "    "

    # create the string with information about the parse.
    for i in range(len(form_info)):
        parse = form_info[i]
        parse_ds = parse_dialects[i]

        parse_dialect = "Neither"

        is_att = parse_ds["attic"]
        is_dor = parse_ds["doric"]
        if (is_att):
            parse_dialect = "Attic"
        if (is_dor):
            parse_dialect = "Doric"
        if (is_dor and is_att):
            parse_dialect = "Attic & Doric"

        text += tab
        text += "Parse %d: %s: %s\n" %((i+1), parse["lemma"], parse_dialect)
        att_rsn = parse_ds["att_rsn"]
        dor_rsn = parse_ds["dor_rsn"]
        if (len(att_rsn) >= 1):
            text += tab
            text += "Reasons for Attic: "
            for rsn in att_rsn:
                text += rsn + ", "
            text += "\n"
        if (len(dor_rsn) >= 1):
            text += tab
            text += "Reasons for Doric: "
            for rsn in dor_rsn:
                text += rsn + ", "
            text += "\n"
        text += tab + "--\n"

    # Return whether the tester returned the proper result and some associated
    # text about the results.
    correct_string = "%s: Correct.\n" % (token)
    if(target_dialect == t_utils.ATTIC):
        if (r_some_Attic and not(r_some_Doric)):
            return (True, correct_string)
        else:
            return (False, text)
    elif(target_dialect == t_utils.DORIC):
        if (r_some_Doric and not(r_some_Attic)):
            return (True, correct_string)
        else:
            return (False, text)
    elif(target_dialect == t_utils.EITHER):
        if (not(r_some_Attic) and not(r_some_Doric)):
            return (True, correct_string)
        else:
            return (False, text)
    return (False, "%s: ERROR! NO MATCH AT ALL!\n" % (token))

# get the rules list
rules_list = rules.rules_list

# get the list of unique tokens
test_tokens_duplicates = []
for test_rule in rules_list:
    for item in test_rule["Attic_Forms"]:
        #print "attic: %s" % item[0]
        test_tokens_duplicates.append(item[0])
    for item in test_rule["Doric_Forms"]:
        #print "doric: %s" % item[0]
        test_tokens_duplicates.append(item[0])
    for item in test_rule["Either_Forms"]:
        #print "either: %s" % item[0]
        test_tokens_duplicates.append(item[0])
test_tokens_list = sorted(set(test_tokens_duplicates))

# get the form and lemma info from the tokens.
(form_data, lemma_info) = get_form_data(test_tokens_list)

rules_to_test = rules_list
# to test an individual rule, use
# rules_to_test = [rules_list[36]]

# test the attic, doric, and either forms for each of the rules,
# and print out any errors.
for i in range(len(rules_to_test)):
    test_rule = rules_to_test[i]
    tester = test_rule["Tester"]
    rule_name = test_rule["Rule_Name"]
    print "~~~~~~%d: RULE: %s~~~~~~" % (i, rule_name)
    for item in test_rule["Attic_Forms"]:
        token = item[0]
        index = item[1]
        token_info = [form_data[token]]
        # need to calculate count data, rule data, individual token data
        (correct, txt) = test_token(token, token_info, lemma_info, index,
          tester, rule_name, t_utils.ATTIC)
        if (not(correct)):
            print "  ~~~ATTIC:~~~"
            print txt
    for item in test_rule["Doric_Forms"]:
        token = item[0]
        index = item[1]
        token_info = [form_data[token]]
        # need to calculate count data, rule data, individual token data
        (correct, txt) = test_token(token, token_info, lemma_info, index,
          tester, rule_name, t_utils.DORIC)
        if (not(correct)):
            print "  ~~~DORIC:~~~"
            print txt

    for item in test_rule["Either_Forms"]:
        token = item[0]
        index = item[1]
        token_info = [form_data[token]]
        # need to calculate count data, rule data, individual token data
        (correct, txt) = test_token(token, token_info, lemma_info, index,
          tester, rule_name, t_utils.EITHER)
        if (not(correct)):
            print "  ~~~EITHER:~~~"
            print txt
