# -*- coding: utf-8 -*-
from urllib2 import Request, urlopen, build_opener, URLError, HTTPError
from socket import error as socket_error
import xml.etree.ElementTree as ET
import os
import re
import json
import sys
import copy
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# whether or not to include evaluation info
INCLUDE_EVAL = True

# whether or not to print every token that is run through Perseus' Morpheus
VERBOSE_PERSEUS = False

# count threshold to include in the "count detail" graphs
GRAPH_THRESHOLD = 100

# whether to include results with no forms in the graphs.
INCLUDE_EMPTIES_IN_GRAPH = False

# enumeration for dialect types.
EITHER = 0
ATTIC = 1
DORIC = 2

# enumeration for stem types.
ADJ_3_TERMINATION = "type_1_2_os/a/on_adjective"
H_A_STEM = "alpha_stem_-h"
SHORT_A_STEM = "alpha_stem_short_-a"
EIR_A_STEM = "alpha_stem_-a"
W_STEM = "digamma_stem"
I_STEM = "iota_stem"
NO_TYPE = "no_special_type"

# get the filename containing the uncleaned text of a text given the text's name
def get_text_fn(text_name):
    return "texts/" + text_name + ".txt"
# get the filename containing the cleaned text of a text given the text's name
def get_text_clean_fn(text_name):
    return "intermediate_files/" + text_name + "/clean_text.txt"
# get the filename containing the form info of a text given the text's name
def get_text_form_data_fn(text_name):
    return "intermediate_files/" + text_name + "/form_data.json"
# get the filename containing the lemma data of a text given the text's name
def get_text_lemma_data_fn(text_name):
    return "intermediate_files/" + text_name + "/lemma_data.json"

# get the filename containing the overall results of a text given the text's name
def get_text_overall_results_fn(text_name):
    return "results/" + text_name + "/overall.txt"
# get the filename containing the dialect results of a text given the text's name
def get_text_dialect_results_fn(text_name):
    return "results/" + text_name + "/dialects.txt"
# get the filename containing the rules results of a text given the text's name
def get_text_rule_results_fn(text_name):
    return "results/" + text_name + "/rules.txt"
# get the filename containing the token results of a text given the text's name
def get_text_token_results_fn(text_name):
    return "results/" + text_name + "/tokens.txt"
# get the filename containing the evaluation results of a text given the text's name
def get_text_evaluation_results_fn(text_name):
    return "results/" + text_name + "/evaluation.txt"
# get the filename containing all the results of a text given the text's name
def get_text_all_results_fn(text_name):
    return "results/" + text_name + "/all.txt"
# get the filename containing all the results of a text given the text's name
def get_text_graph_fn(text_name, pct_or_count, max_or_min, sortd):
    return "results/%s/graphs/%s_%s_%s_rule_results_pct_graph.pdf" % (text_name, pct_or_count, sortd, max_or_min)


# check if the given file path exists, and if not create it.
# based on Krumelur's answer to
# http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
def check_and_create_path(filename):
    if (not os.path.exists(os.path.dirname(filename))):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

# write content to the file at filename. Make the directory path to the given
# file if it does not exist.
def safe_write(filename, content):
    check_and_create_path(filename)
    out_file = open(filename, "w")
    out_file.write(content)
    out_file.close()

# switch a capitalized token to lowercase
def decapitalize_token(w):
    token_lc = w.lower()
    # Beta code has a fun quirk where diacritic marks are added to the *
    # if the first letter is capitalized, so A)/lkhstis is *)/alkhstis.
    # So if we naively remove the *, we end up with improperly formatted
    # forms and must instead be a bit clever.
    if (len(token_lc) >= 2 and token_lc[0] == '*' and re.match(r'\)|\(|/|=|\\|&|\+|\||\'', token_lc[1])):
        # split into star, first diacritic marks, rest of string
        split = re.split(r'((\)|\(|/|=|\\|&|\+|\||\')+)', token_lc, 1)
        return split[3][0] + split[1] + split[3][1:]
    else:
        return re.sub(r'\*', "", token_lc)

# Morpheus converts the \ accent to an / automatically, so for proper
# recognition of original forms we must also do so. We also want all
# capitals in beta code to be switched to lower case.
# Morpheus also automatically removes the second accent on tokens who have
# an accent added due to following enclitics, so we should remove those as well.
def fix_token (w) :
    lower_beta = decapitalize_token(w)
    # if there are two accents and the second is /, remove it. Unless it is
    # dia/doxa/, which as to be recognized with both, because that is how
    # Morpheus sees it.
    if (lower_beta == "dia/doxa/"):
        one_accent = lower_beta
    else:
        split = re.split(r'(/|=)', lower_beta)
        if (len(split) > 3 and split[3] == "/"):
            one_accent = split[0] + split[1] + split[2] + split[4]
        else:
            one_accent = lower_beta
    return re.sub(r'\\', '/', one_accent)

# Clean up the input data (that has been copied from Perseus)
def clean_up_data (d) :
    # remove extra fluff from my notation, like line numbers and section names.
    no_fluff = re.sub(r'\?|(\d+\-(\d+|ff|fin).*?\n)|\d', "", d)
    # remove notation of which character is speaking
    no_actors = re.sub(r'(\n\*[^\s]*([ ]*|([ ]+(a|b|\*a|\*b)))\n)', "\n", no_fluff)
    # take "--" and turn it into " --" to make sure we don't accidently
    # treat them as wrapping token.
    no_extra_wrap = re.sub(r'\-\-', " --", no_actors)
    # recombine tokens that have been wrapped
    fix_wrapping = re.sub(r'\-[ ]*\n', "", no_extra_wrap)
    # remove newlines
    no_newlines = re.sub(r'\n', " ", fix_wrapping)
    # remove various "non-original" text.
    # Text in daggers generally makes no sense and is assumed to have been
    # transmitted poorly. Text in square brackets is assumed to have been
    # added from another location in the text or a later actor.
    # Text in angle brackets contain a token that is presumed to have existed in
    # the original text but is not present.
    no_dubious = re.sub(r'(†.*?†)|(\[.*?\])|(<.*?>)', "", no_newlines)
    # remove non-beta-code characters and punctuation.
    all_beta_code = re.sub(r'[^A-Za-z)(/=\\+|&\'\s*]', " ", no_dubious)
    # take groups of spaces and convert them to a single space
    group_spaces = re.sub(r'\s+', " ", all_beta_code)
    # removes spaces at the start and end of the text
    no_start_space = re.sub(r'^\s+', "", group_spaces)
    no_end_space = re.sub(r'\s+$', "", no_start_space)
    final = no_end_space
    return final

# Given input text, clean it up, fix all the tokens, and return a list of the
# tokens and a sorted set of the unique tokens
def clean_and_fix(text):
    clean_text = clean_up_data(text)
    tokens = clean_text.split(" ")

    standardized_tokens = map(fix_token, tokens)

    sorted_uniq_tokens = sorted(set(standardized_tokens))

    return (standardized_tokens, sorted_uniq_tokens)


# The Perseus XML requests cannot properly read diacritics, so we filter them
# out and only accept responses that match our original token with its
# diacritics.
def remove_diacritics (w) :
    return re.sub(r'\)|\(|/|=|\\|&|\+|\||\'', '', w)

# given a dictionary to store lemmas, return a function that can be
# used with map to find parses for each token and store extra info about lemmas.
def get_Perseus_data (lemma_dict):
    # given a token, return a tuple with the base token and a list of the lemma
    # results returned by Perseus with their data in a dictionary
    def fun (base_token):
        if (VERBOSE_PERSEUS):
            print base_token
        noDiacritics = remove_diacritics(base_token)
        baseURL = "http://www.perseus.tufts.edu/hopper/xmlmorph?lang=greek&lookup="
        url = baseURL + noDiacritics
        opener = build_opener()
        # we have to include this cookie so that we get results in betacode
        # (which is easy to parse) rather than unicode greek (harder to parse).
        opener.addheaders.append(("Cookie", "disp.prefs=\"greek.display=PerseusBetaCode\""))
        tries = 0
        max_tries = 5

        # we make a large number of calls, so often one or two will not go
        # through; to make sure this doesn't break everything, we try
        # multiple times before quitting.
        while tries < max_tries:
            if (tries != 0):
                print "~~~~~TRYING AGAIN~~~~~"
            try:
                response = opener.open(url)
                xml = response.read()
                analyses = ET.fromstring(xml)
                results = []
                num_analyses = 0
                # given the response, convert it into a python dictionary
                # and store the lemmas found in the list of lemmas.
                for analysis in analyses:
                    num_analyses += 1
                    if (analysis[0].text == base_token):
                        sub_dict = {}
                        for child in analysis:
                            sub_dict[child.tag] = child.text
                        lem = sub_dict["lemma"]
                        if (lem in lemma_dict):
                            lemma_dict[sub_dict["lemma"]].append(sub_dict["pos"])
                        else:
                            lemma_dict[sub_dict["lemma"]] = [sub_dict["pos"]]

                        results.append(sub_dict)
                if (num_analyses == 0):
                    print ("No results for \"" + base_token + "\"")
                elif (len(results) == 0):
                    print num_analyses, (" results but no matches for \"" + base_token + "\"")
                return (base_token, results)
            except HTTPError as e:
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            except URLError as e:
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            except socket_error as e:
                print "Socket Error: failed to reach server:"
                print sys.exc_info()[0]
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            tries += 1
        print "~~~~~Gave Up~~~~~"
        return (base_token, [])

    return fun

# given a list of lemmas, run through them to determine stem-type information
# by running additional queries to Morpheus to determine whether the form
# is of a given stem type or not.
def get_lemma_info(lemmas):
    sorted_lemmas = sorted(lemmas.keys())

    lemma_results = {}
    for lemma in sorted_lemmas:
        no_caps_lem = decapitalize_token(lemma)
        val = lemmas[lemma]
        pos = sorted(set(val))
        clean_lem = remove_diacritics(lemma)
        my_type = NO_TYPE
        get_P_data = get_Perseus_data({})

        # is this a feminine long-alpha stem?
        if (clean_lem[-1] == "h" and "noun" in pos): #fem alpha stripped_form
            genitive_form = ""
            if (lemma[-1] == "h"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-1]) + "hs"
            elif (lemma[-2:] == "h/"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-2]) + "h=s"
            if (not(genitive_form == "")):
                (_, forms) = get_P_data(genitive_form)
                for form in forms:
                    if (form["lemma"] == lemma and ("gender" in form) and
                      ("case" in form) and ("number" in form) and
                      form["gender"] == "fem" and form["case"] == "gen" and
                      form["number"] == "sg"):
                        my_type = H_A_STEM
        # is this a feminine long-alpha stem with e/i/r before the alpha?
        elif ((clean_lem[-2:] == "ra" or clean_lem[-2:] == "ia" or
          clean_lem[-2:] == "ea") and "noun" in pos): #fem alpha stripped_form
            plural_form = ""
            if (lemma[-1] == "a"):
                plural_form = re.sub(r'\*', '', no_caps_lem[0:-1]) + "ai"
            elif (lemma[-2:] == "a/"):
                plural_form = re.sub(r'\*', '', no_caps_lem[0:-2]) + "ai/"
            if (not(plural_form == "")):
                (_, forms) = get_P_data(plural_form)
                for form in forms:
                    if (form["lemma"] == lemma and ("gender" in form) and
                      ("case" in form) and ("number" in form) and
                      form["gender"] == "fem" and form["case"] == "nom" and
                      form["number"] == "pl"):
                        my_type = EIR_A_STEM
        # is this a feminine short alpha stem?
        elif (clean_lem[-1:] == "a" and "noun" in pos): #fem short alpha
            plural_form = re.sub(r'\*', '', no_caps_lem[0:-1]) + "ai"
            (_, forms) = get_P_data(plural_form)
            for form in forms:
                if (form["lemma"] == lemma and form["gender"] == "fem" and
                  form["case"] == "nom" and form["number"] == "pl"):
                    my_type = SHORT_A_STEM
        # is this a masculine alpha stem?
        elif (clean_lem[-2:] == "hs" and "noun" in pos): #masc alpha stem
            genitive_form = ""
            if (lemma[-2:] == "hs"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-2]) + "ou"
            elif (lemma[-3:] == "h/s"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-3]) + "ou="
            if (not(genitive_form == "")):
                (_, forms) = get_P_data(genitive_form)
                for form in forms:
                    if (form["lemma"] == lemma and ("gender" in form) and
                      ("case" in form) and ("number" in form) and
                      form["gender"] == "masc" and form["case"] == "gen" and
                      form["number"] == "sg"):
                        my_type = H_A_STEM
        # is this a masculine alpha stem with e/i/r before the ending?
        elif ((len(clean_lem) >= 3) and (clean_lem[-3:] == "ras" or
          clean_lem[-3:] == "ias" or clean_lem[-3:] == "eas") and "noun" in pos):
            genitive_form = ""
            if (lemma[-2:] == "as"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-2]) + "ou"
            elif (lemma[-3:] == "a/s"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-3]) + "ou="
            if (not(genitive_form == "")):
                (_, forms) = get_P_data(genitive_form)
                for form in forms:
                    if (form["lemma"] == lemma and ("gender" in form) and
                      ("case" in form) and ("number" in form) and
                      form["gender"] == "masc" and form["case"] == "gen" and
                      form["number"] == "sg"):
                        my_type = EIR_A_STEM
        # is this a digamma stem? (basileus type)
        elif (clean_lem[-3:] == "eus" and "noun" in pos):
            genitive_form = re.sub(r'\*', '', lemma[0:-4]) + "e/ws"
            (_, forms) = get_P_data(genitive_form)
            for form in forms:
                if (form["lemma"] == lemma and ("case" in form) and
                  ("number" in form) and form["number"] == "sg" and
                  form["case"] == "gen"):
                    my_type = W_STEM
        # is this a iota stem? (polis type)
        elif (clean_lem[-2:] == "is" and "noun" in pos):
            genitive_form = ""
            if (lemma[-2:] == "is"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-2]) + "ews"
            elif (lemma[-3:] == "i/s"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-3]) + "e/ws"
            if (not(genitive_form == "")):
                (_, forms) = get_P_data(genitive_form)
                for form in forms:
                    if (form["lemma"] == lemma and ("case" in form) and
                      ("number" in form) and form["number"] == "sg" and
                      form["case"] == "gen"):
                        my_type = I_STEM
        # is this a 3-termination adjective?
        elif (clean_lem[-2:] == "os" and "adj" in pos):
            fem_form = ""
            if (lemma[-2:] == "os"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-2]) + "ai"
            elif (lemma[-3:] == "o/s"):
                genitive_form = re.sub(r'\*', '', no_caps_lem[0:-3]) + "ai/"
            if (not(genitive_form == "")):
                (_, forms) = get_P_data(genitive_form)
                for form in forms:
                    if (form["lemma"] == lemma and ("gender" in form) and
                      ("case" in form) and ("number" in form) and
                      form["number"] == "pl" and form["case"] == "nom" and
                      form["gender"] == "fem"):
                        my_type = ADJ_3_TERMINATION
        # set the type.
        lemma_results[lemma] = my_type
    return lemma_results

# get the form and lemma data for the given set of (unique) tokens
# include whether to get the information from perseus or from files
# and the filenames to get the form and lemma data
def get_form_and_lemma_data(token_list, from_perseus, form_data_fn, lemma_data_fn):
    # if we get it from Perseus' Morpheus, just run queries for each token
    if (from_perseus):
        lemmas = {}
        form_data = map(get_Perseus_data(lemmas), token_list)
        lemma_data = get_lemma_info(lemmas)
    # if we have preprocessed, get the information from the given files.
    else:
        form_data_file = open(form_data_fn, 'r')
        form_data_contents = form_data_file.read()
        form_data_file.close()
        form_data = json.loads(form_data_contents)

        lemma_data_file = open(lemma_data_fn, 'r')
        lemma_data_contents = lemma_data_file.read()
        lemma_data_file.close()
        lemma_data = json.loads(lemma_data_contents)

    # reconstruct the form data dictionary (which is corrupted by the
    # conversion to json and back)
    form_data_dict = {}
    for fi in form_data:
        form = fi[0]
        form_info = fi[1]
        if (form in token_list):
            form_data_dict[form] = form_info
    return (form_data_dict, lemma_data)

# evaluate the program's dialect decision on the given token when compared to
# Morpheus'. Takes information about the token, the list of rules, the info
# for lemmas, and the datastructure that will contain the results of the
# evaluation.
def eval_token(token, token_info, rules, lemma_data, evaluation_results):
    parse_info = token_info[0]

    if(len(parse_info) == 0):
        return False

    # get the evaluation results for the token.
    tab = "    "
    for i in range(len(parse_info)):
        parse = parse_info[i]
        info = [parse, lemma_data[parse["lemma"]]]

        attic_reasons = []
        doric_reasons = []

        # get tamnon's dialect information
        parse_some_Doric = False
        parse_some_Attic = False
        for rule in rules:
            # testing function returns ATTIC, DORIC, or EITHER
            tester = rule["Tester"]
            r_name = rule["Rule_Name"]


            res = tester(info)
            if (res == ATTIC):
                parse_some_Attic = True
                attic_reasons.append(r_name)
            elif (res == DORIC):
                parse_some_Doric = True
                doric_reasons.append(r_name)

        # get Morpheus' dialect information
        morpheus_attic = False
        morpheus_doric = False
        if (parse["dialect"]):
            morpheus_dialects = parse["dialect"].split(" ")
            for m_dialect in morpheus_dialects:
                if (m_dialect == "attic"):
                    morpheus_attic = True
                if (m_dialect == "doric"):
                    morpheus_doric = True


        # get form text
        t_dialect = "Neither"
        if (parse_some_Attic):
            t_dialect = "Attic"
        if (parse_some_Doric):
            t_dialect = "Doric"
        if (parse_some_Doric and parse_some_Attic):
            t_dialect = "Attic & Doric"

        m_dialect = "Neither"
        if (morpheus_attic):
            m_dialect = "Attic"
        if (morpheus_doric):
            m_dialect = "Doric"
        if (morpheus_doric and morpheus_attic):
            m_dialect = "Attic & Doric"


        text = "%s Parse %d: %s:\n" %(token, (i+1), parse["lemma"])
        text += "%sTamnon evaluation: %s\n" % (tab, t_dialect)
        text += "%sMorpheus evaluation: %s\n" % (tab, m_dialect)
        att_rsn = attic_reasons
        dor_rsn = doric_reasons
        if (len(att_rsn) >= 1):
            text += tab
            text += "Tamnon reasons for Attic: "
            for rsn in att_rsn:
                text += rsn + ", "
            text += "\n"
        if (len(dor_rsn) >= 1):
            text += tab
            text += "Tamnon reasons for Doric: "
            for rsn in dor_rsn:
                text += rsn + ", "
            text += "\n"
        text += tab + "--\n"


        # determine whether the evaluation was correct or not and
        # add the result to the proper section.
        if (parse_some_Doric):
            if (morpheus_doric):
                evaluation_results["both_doric"].append(text)
            else:
                evaluation_results["t_doric_m_not"].append(text)
        if (parse_some_Attic):
            if (morpheus_attic):
                evaluation_results["both_attic"].append(text)
            else:
                evaluation_results["t_attic_m_not"].append(text)
        if (not (parse_some_Attic) and not(parse_some_Doric)):
            if (morpheus_attic or morpheus_doric):
                evaluation_results["t_neither_m_not"].append(text)
            else:
                evaluation_results["both_neither"].append(text)

        evaluation_results["total_count"] += 1



# given a token, information about the tokens parses, the list of rules,
# the count data for tokens ("c"), the data for each lemma, and the data
# structure containing the list of tokens of each dialect.
def analyze_token(token, token_info, rules, lemma_data, c, divided_tokens):
    parse_info = token_info[0]
    text = "%s:\n" % (token)

    if(len(parse_info) == 0):
        text += "No form matches.\n"
        return text

    # set up a list of the dialects and reasons for those dialects for each
    # parse.
    parse_dialects = []
    for i in range(len(parse_info)):
        parse_dialects.append({"attic": False, "doric": False, "att_rsn": [], "dor_rsn": []})

    # for each rule
    for rule in rules:
        # testing function returns ATTIC, DORIC, or EITHER
        tester = rule["Tester"]
        r_name = rule["Rule_Name"]

        r_some_Doric = False
        r_some_Attic = False
        r_all_Doric = True
        r_all_Attic = True
        r_all_judged = True

        rule_matches = []

        # determine the dialect of each parse by this rule
        for i in range(len(parse_info)):
            parse = parse_info[i]

            info = [parse, lemma_data[parse["lemma"]]]
            res = tester(info)
            if (res == ATTIC):
                rule_matches.append([i, parse["lemma"], "Attic"])
                r_some_Attic = True
                r_all_Doric = False
                parse_dialects[i]["attic"] = True
                parse_dialects[i]["att_rsn"].append(r_name)
            elif (res == DORIC):
                rule_matches.append([i, parse["lemma"], "Doric"])
                r_some_Doric = True
                r_all_Attic = False
                parse_dialects[i]["doric"] = True
                parse_dialects[i]["dor_rsn"].append(r_name)
            else:
                r_all_Doric = False
                r_all_Attic = False
                r_all_judged = False

        # store the results for this token and rule.
        if (len(rule_matches) > 0):
            rule["rule_decisions"].append([token, rule_matches])
        if (r_some_Doric):
            rule["max_occ"] += 1
        if (r_some_Doric or r_some_Attic):
            rule["max_psbl_occ"] += 1
        if (r_all_Doric):
            rule["min_occ"] += 1
        if (r_all_judged):
            rule["min_psbl_occ"] += 1


    t_some_Doric = False
    t_some_Attic = False
    t_some_Both = False
    t_some_Neither = False
    t_all_Doric = True
    t_all_Attic = True


    # create the text specifying the information about this token.
    tab = "    "

    for i in range(len(parse_info)):
        parse = parse_info[i]
        parse_ds = parse_dialects[i]

        parse_dialect = "Neither"

        is_att = parse_ds["attic"]
        is_dor = parse_ds["doric"]
        if (is_att):
            t_some_Attic = True
            parse_dialect = "Attic"
        else:
            t_all_Attic = False
        if (is_dor):
            t_some_Doric = True
            parse_dialect = "Doric"
        else:
            t_all_Doric = False

        if (is_dor and is_att):
            t_some_Both = True
            parse_dialect = "Attic & Doric"

        if (not(is_dor) and not(is_att)):
            t_some_Neither = True

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


    # store the token in the appropriate dialect list and update
    # the dialect counts appropriately.

    # if all parses are doric
    if (t_all_Doric):
        divided_tokens["doric_tokens"].append("Definitely Doric: " + text)
        c["doric"]["min"] += 1
        c["doric"]["max"] += 1
    # if any parse is doric
    elif (t_some_Doric):
        divided_tokens["doric_tokens"].append("Maybe Doric: " + text)
        c["doric"]["max"] += 1
    # if all parses are attic
    if (t_all_Attic):
        divided_tokens["attic_tokens"].append("Definitely Attic: " + text)
        c["attic"]["min"] += 1
        c["attic"]["max"] += 1
    # if any parse is attic
    elif (t_some_Attic):
        divided_tokens["attic_tokens"].append("Maybe Attic: " + text)
        c["attic"]["max"] += 1
    # if some parses are attic and some are doric
    if (t_some_Attic and t_some_Doric):
        divided_tokens["xor_tokens"].append(text)
        c["either"] += 1
    # if all parses are attic and doric
    if (t_all_Attic and t_all_Doric):
        divided_tokens["both_tokens"].append("Definitely Both: " + text)
        c["both"]["min"] += 1
        c["both"]["max"] += 1
    # if any parse is attic and doric
    elif (t_some_Both):
        divided_tokens["both_tokens"].append("Maybe Both: " + text)
        c["both"]["max"] += 1
    # if all parses have no preference
    if (not(t_some_Attic) and not(t_some_Doric)):
        divided_tokens["unclear_tokens"].append("Definitely Neither: " + text)
        c["neither"]["min"] += 1
        c["neither"]["max"] += 1
    # if any parse has no preference
    elif (t_some_Neither):
        divided_tokens["unclear_tokens"].append("Maybe Neither: " + text)
        c["neither"]["max"] += 1

    # return the information about the token.
    return text

# Given a list of rules, the specifications for the nondoric and doric bars,
# the file to save the graph in, the x and y labels, the tile and
# whether the bars are horizontal or vertical, create a barchart with
# the specified bars and save it at the filename location.
def make_and_save_plot(r_names, non_dor, dor, filename, xlabel, ylabel, title, is_horiz):

    rule_names = copy.copy(r_names)
    rule_names.reverse()
    non_dor.reverse()
    dor.reverse()

    # set up the plot size
    plt.clf()
    fig = plt.figure()
    fig.set_size_inches((8.5), (11.))

    n_groups = len(rule_names)
    index = np.arange(n_groups)

    bar_width = .6

    # set up the plotting function based on whether these bars are horizontal
    # or vertical.
    if (is_horiz):
        plot_fun = plt.barh
    else:
        plot_fun = plt.bar

    # put the data on the graph.
    full_bars = plot_fun(index, non_dor, bar_width, color='skyblue')
    doric_bars = plot_fun(index, dor, bar_width, color='royalblue')

    # set the proper labels and the title
    if (is_horiz):
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
    else:
        plt.ylabel(xlabel)
        plt.xlabel(ylabel)

    plt.title(title)
    plt.tick_params(labelsize=10)

    # set up the ticks and limits of the graph
    if (is_horiz):
        plt.yticks(index + bar_width/2, rule_names)
        plt.tick_params(axis="x", direction="out", top="off")
        plt.tick_params(axis="y", direction="out", right="off")
        plt.ylim(-0.5, n_groups*(100.0/95) + 0.5)
    else:
        plt.xticks(index + bar_width/2, rule_names, rotation="vertical")
        plt.xlim(-0.5, n_groups + 0.5)
        plt.tick_params(axis="x", direction="out", top="off")
        plt.tick_params(axis="y", direction="out")

    # create the legend
    labels = ('Doric', 'Non-Doric')
    plt.legend((doric_bars[0], full_bars[0]), labels,
      loc="upper center", ncol=2)

    # save the graph
    check_and_create_path(filename)
    pp = PdfPages(filename)
    pp.savefig()
    pp.close()

# given input text, rules, a filename containing information about each form, a
# file containing information about each lemma, the list of graph filenames, and
# whether to get data straight from Perseus' Morpheus, determine all the
# necessary information about the input text and return a series of textual
# reports. If graph_fns is non-empty, store the result graphs at the filenames
# specified in graph_fns.
def generate_results(input_text, rules, form_fn, lemma_fn, graph_fns, from_perseus):
    (standardized_tokens, sorted_uniq_tokens) = input_text

    # get the form and lemma info
    (form_data, lemma_data) = get_form_and_lemma_data(sorted_uniq_tokens,
      from_perseus, form_fn, lemma_fn)

    # initialize the many storage variables
    overall_results = []
    dialect_pre = []
    dialect_results = []
    rule_pre = []
    rule_results = []
    token_results = []
    eval_title = "~~ Evaluation Results ~~"
    evaluation_info = [eval_title, "Evaluation Information Disabled."]
    overall_results.append("OVERALL INFO:")
    token_by_token = []
    doric_forms = 0
    attic_forms = 0
    mixed_forms = 0
    dorics = {"min": 0, "max": 0}
    attics = {"min": 0, "max": 0}
    boths  = {"min": 0, "max": 0}
    neithers  = {"min": 0, "max": 0}
    counts = {"doric": dorics, "attic": attics, "both": boths, "neither": neithers, "either": 0}
    for rule in rules:
        rule["max_occ"] = 0
        rule["min_occ"] = 0
        rule["max_psbl_occ"] = 0
        rule["min_psbl_occ"] = 0
        rule["rule_decisions"] = []

    divided_tokens = {}
    divided_tokens["doric_tokens"] = []
    divided_tokens["attic_tokens"] = []
    divided_tokens["both_tokens"] = []
    divided_tokens["unclear_tokens"] = []
    divided_tokens["xor_tokens"] = []

    # run the analysis on each token.
    for token in standardized_tokens:
        if (token in form_data):
            token_info = [form_data[token]]
            # need to calculate count data, rule data, individual token data
            w = analyze_token(token, token_info, rules, lemma_data, counts, divided_tokens)
            token_by_token.append(w)
        else:
            token_by_token.append("No form information for %s\n" % token)

    # if we want to evaluate tamnon against morpheus, initialize the variables
    # and run the analysis.
    if (INCLUDE_EVAL):
        evaluation_info = [eval_title]
        evaluation_results = {}
        evaluation_results["both_doric"] = []
        evaluation_results["both_attic"] = []
        evaluation_results["both_neither"] = []
        evaluation_results["t_doric_m_not"] = []
        evaluation_results["t_attic_m_not"] = []
        evaluation_results["t_neither_m_not"] = []
        evaluation_results["total_count"] = 0

        for token in sorted_uniq_tokens:
            if (token in form_data):
                token_info = [form_data[token]]
                # evaluate the tool's analysis of the dialect based on perseus'
                # result.
                eval_token(token, token_info, rules, lemma_data, evaluation_results)

        both_doric_count = len(evaluation_results["both_doric"])
        both_attic_count = len(evaluation_results["both_attic"])
        both_neither_count = len(evaluation_results["both_neither"])
        t_doric_count = len(evaluation_results["t_doric_m_not"])
        t_attic_count = len(evaluation_results["t_attic_m_not"])
        t_neither_count = len(evaluation_results["t_neither_m_not"])
        total_count = evaluation_results["total_count"]

        # create the evaluation text report.
        evaluation_info.append("sum: %d; total count: %d" % ((both_doric_count + both_attic_count + both_neither_count + t_doric_count + t_attic_count + t_neither_count), total_count))
        if (not (total_count == 0)):
            evaluation_info.append("Both Doric: %d, %.2f%%" % (both_doric_count, (100*float(both_doric_count)/total_count)))
            evaluation_info.append("Both Attic: %d, %.2f%%" % (both_attic_count, (100*float(both_attic_count)/total_count)))
            evaluation_info.append("Both Neither: %d, %.2f%%" % (both_neither_count, (100*float(both_neither_count)/total_count)))
            evaluation_info.append("Tamnon Doric, Morpheus not: %d, %.2f%%" % (t_doric_count, (100*float(t_doric_count)/total_count)))
            evaluation_info.append("Tamnon Attic, Morpheus not: %d, %.2f%%" % (t_attic_count, (100*float(t_attic_count)/total_count)))
            evaluation_info.append("Tamnon Neither, Morpheus not: %d, %.2f%%" % (t_neither_count, (100*float(t_neither_count)/total_count)))
        evaluation_info.append("~~~~~~~~~~~~~")
        evaluation_info.append("Both Doric:")
        evaluation_info.extend(evaluation_results["both_doric"])
        evaluation_info.append("---------")
        evaluation_info.append("Both Attic:")
        evaluation_info.extend(evaluation_results["both_attic"])
        evaluation_info.append("---------")
        evaluation_info.append("Both Neither:")
        evaluation_info.extend(evaluation_results["both_neither"])
        evaluation_info.append("---------")
        evaluation_info.append("Tamnon Doric, Morpheus not:")
        evaluation_info.extend(evaluation_results["t_doric_m_not"])
        evaluation_info.append("---------")
        evaluation_info.append("Tamnon Attic, Morpheus not:")
        evaluation_info.extend(evaluation_results["t_attic_m_not"])
        evaluation_info.append("---------")
        evaluation_info.append("Tamnon Neither, Morpheus not:")
        evaluation_info.extend(evaluation_results["t_neither_m_not"])
        evaluation_info.append("---------")


    # generate the various text and graph reports.
    doric_tokens = divided_tokens["doric_tokens"]
    attic_tokens = divided_tokens["attic_tokens"]
    both_features_tokens = divided_tokens["both_tokens"]
    unclear_tokens = divided_tokens["unclear_tokens"]
    xor_tokens = divided_tokens["xor_tokens"]

    # store the dialect information
    dialect_pre.append(["~~ Token Counts ~~"])
    dialect_pre.append(["Number of Tokens: %d" % len(standardized_tokens)])
    dialect_pre.append(["Number of Unique Tokens: %d" % len(sorted_uniq_tokens)])
    dialect_pre.append(["Doric Tokens:\n  Max: %d\n  Min: %d" % (counts["doric"]["max"], counts["doric"]["min"]), doric_tokens])
    dialect_pre.append(["Attic Tokens:\n  Max: %d\n  Min: %d" % (counts["attic"]["max"], counts["attic"]["min"]), attic_tokens])
    dialect_pre.append(["Tokens with Doric and Attic Features:\n  Max: %d\n  Min: %d" % (counts["both"]["max"], counts["both"]["min"]), both_features_tokens])
    dialect_pre.append(["Tokens that have no clear dialect:\n  Max: %d\n  Min: %d" % (counts["neither"]["max"], counts["neither"]["min"]), unclear_tokens])
    dialect_pre.append(["Tokens that are potentially Attic and potentially Doric: %d" % counts["either"], xor_tokens])

    # append the overall dialect information to the overall results and all
    # dialect information to the dialect results
    for pre in dialect_pre:
        overall_results.append(pre[0])
        dialect_results.append(pre[0])
        if (len(pre) >= 2):
            dialect_results.extend(pre[1])

    # store general rules text
    rule_pre.append("~~ Rule Results ~~")
    rule_pre.append("- Rule Name, Max number of tokens Doric form does/could occur in, Min number of tokens Doric form does/could occur in.")

    # add the general rules text to the overall and rule reports
    for pre in rule_pre:
        overall_results.append(pre)
        rule_results.append(pre)


    # generate the rules text as well as the information necessary for
    # the graphs of the rule results.
    tab = "  "
    n_a = "N/A"

    short_rule_names_unsorted = []
    bg_maxes_pct_unsorted = []
    dor_maxes_pct_unsorted = []
    bg_mins_pct_unsorted = []
    dor_mins_pct_unsorted = []

    bg_maxes_count_unsorted = []
    dor_maxes_count_unsorted = []
    bg_mins_count_unsorted = []
    dor_mins_count_unsorted = []
    for rule in rules:

        # get the numeric information for this rule
        max_occ = rule["max_occ"]
        max_psbl = rule["max_psbl_occ"]
        min_occ = rule["min_occ"]
        min_psbl = rule["min_psbl_occ"]

        short_rule_names_unsorted.append(rule["Short_Name"])

        if (max_psbl > 0):
            fraction = float(max_occ)/max_psbl
            bg_maxes_pct_unsorted.append(1)
            dor_maxes_pct_unsorted.append(fraction)

            max_pct = "%.2f%%" % (100 *fraction)
        else:
            max_pct = n_a
            bg_maxes_pct_unsorted.append(0)
            dor_maxes_pct_unsorted.append(0)

        bg_maxes_count_unsorted.append(max_psbl)
        dor_maxes_count_unsorted.append(max_occ)

        if (min_psbl > 0):
            fraction = float(min_occ)/min_psbl
            bg_mins_pct_unsorted.append(1)
            dor_mins_pct_unsorted.append(fraction)
            min_pct = "%.2f%%" % (100 * fraction)
        else:
            min_pct = n_a
            bg_mins_pct_unsorted.append(0)
            dor_mins_pct_unsorted.append(0)

        bg_mins_count_unsorted.append(min_psbl)
        dor_mins_count_unsorted.append(min_occ)

        # generate the text for this rule
        s = "%s: %s/%s = %s, %s/%s = %s" % (rule["Rule_Name"], max_occ, max_psbl, max_pct, min_occ, min_psbl, min_pct)
        overall_results.append(s)
        rule_results.append(s)
        for token_info in rule["rule_decisions"]:
            token = token_info[0]
            notable_parses = token_info[1]
            rule_results.append("%s%s:" % (tab, token))
            for parse in notable_parses:
                s = "%s%sParse %d: %s. " % (tab, tab, parse[0], parse[1])
                s += "Dialect: %s" % parse[2]
                rule_results.append(s)

    # if we have the graph filenames, create the graphs.
    if (len(graph_fns) >= 8):
        # zip the max/min percent/count information for unified sorting.
        max_pct_zipped = zip(short_rule_names_unsorted, bg_maxes_pct_unsorted, dor_maxes_pct_unsorted)
        min_pct_zipped = zip(short_rule_names_unsorted, bg_mins_pct_unsorted, dor_mins_pct_unsorted)

        max_count_zipped = zip(short_rule_names_unsorted, bg_maxes_count_unsorted, dor_maxes_count_unsorted)
        min_count_zipped = zip(short_rule_names_unsorted, bg_mins_count_unsorted, dor_mins_count_unsorted)

        # if we are not including the empty items, filter them out.
        if (not(INCLUDE_EMPTIES_IN_GRAPH)):
            max_pct_zipped = filter(lambda x: (x[1] > 0), max_pct_zipped)
            min_pct_zipped = filter(lambda x: (x[1] > 0), min_pct_zipped)
            max_count_zipped = filter(lambda x: (x[1] > 0), max_count_zipped)
            min_count_zipped = filter(lambda x: (x[1] > 0), min_count_zipped)

        # get the unsorted percent information for max and min cases
        zr1, zr2, zr3 = zip(*max_pct_zipped)
        short_rule_names_max_pct_unsorted = list(zr1)
        bg_maxes_pct_unsorted = list(zr2)
        dor_maxes_pct_unsorted = list(zr3)

        zr1, zr2, zr3 = zip(*min_pct_zipped)
        short_rule_names_min_pct_unsorted = list(zr1)
        bg_mins_pct_unsorted = list(zr2)
        dor_mins_pct_unsorted = list(zr3)

        # get the sorted percent information for max and min cases
        sorted_zipped = sorted(max_pct_zipped, cmp=lambda x, y: cmp(x[2], y[2]))
        zr1, zr2, zr3 = zip(*sorted_zipped)
        short_rule_names_max_pct_sorted = list(zr1)
        bg_maxes_pct_sorted = list(zr2)
        dor_maxes_pct_sorted = list(zr3)

        sorted_zipped = sorted(min_pct_zipped, cmp=lambda x, y: cmp(x[2], y[2]))
        zr1, zr2, zr3 = zip(*sorted_zipped)
        short_rule_names_min_pct_sorted = list(zr1)
        bg_mins_pct_sorted = list(zr2)
        dor_mins_pct_sorted = list(zr3)

        # get the sorted count information (generating two sets: all rules and
        # only those with counts below GRAPH_THRESHOLD) for the max and min cases.
        sorted_zipped = sorted(max_count_zipped, cmp=lambda x, y: cmp(x[1], y[1]))
        zr1, zr2, zr3 = zip(*sorted_zipped)
        short_rule_names_max_count_sorted = list(zr1)
        bg_maxes_count_sorted = list(zr2)
        dor_maxes_count_sorted = list(zr3)
        filtered = filter(lambda x: (x[1] <= GRAPH_THRESHOLD), sorted_zipped)
        zr1, zr2, zr3 = zip(*filtered)
        short_rule_names_max_count_small_sorted = list(zr1)
        bg_maxes_count_small_sorted = list(zr2)
        dor_maxes_count_small_sorted = list(zr3)

        sorted_zipped = sorted(min_count_zipped, cmp=lambda x, y: cmp(x[1], y[1]))
        zr1, zr2, zr3 = zip(*sorted_zipped)
        short_rule_names_min_count_sorted = list(zr1)
        bg_mins_count_sorted = list(zr2)
        dor_mins_count_sorted = list(zr3)
        filtered = filter(lambda x: (x[1] <= GRAPH_THRESHOLD), sorted_zipped)
        zr1, zr2, zr3 = zip(*filtered)
        short_rule_names_min_count_small_sorted = list(zr1)
        bg_mins_count_small_sorted = list(zr2)
        dor_mins_count_small_sorted = list(zr3)

        # get the filenames for each graph

        max_pct_unsorted_fname = graph_fns[0]
        min_pct_unsorted_fname = graph_fns[1]
        max_pct_sorted_fname = graph_fns[2]
        min_pct_sorted_fname = graph_fns[3]
        max_count_sorted_fname = graph_fns[4]
        min_count_sorted_fname = graph_fns[5]
        max_count_small_sorted_fname = graph_fns[6]
        min_count_small_sorted_fname = graph_fns[7]


        # get the labels and titles tha will be used in various graphs.
        ylabel = "Rule"

        xlabel_pct = "Fraction of Occurrences That Are Doric"
        title_pct_min = "Fractions of Definite Occurrences of Each Rule That Are Doric"
        title_pct_max = "Fractions of Possible Occurrences of Each Rule That Are Doric"

        xlabel_count = "Number of Occurrences"
        title_count_min = "Number of Definite Doric and Total Occurrences of Each Rule"
        title_count_max = "Number of Possible Doric and Total Occurrences of Each Rule"

        title_count_small_min = "Number of Definite Doric and Total Occurrences of Each Rule\n (for rules with < %d occurences)" % GRAPH_THRESHOLD
        title_count_small_max = "Number of Possible Doric and Total Occurrences of Each Rule\n (for rules with < %d occurences)" % GRAPH_THRESHOLD

        # create all of the graphs.
        make_and_save_plot(short_rule_names_max_pct_unsorted,
          bg_maxes_pct_unsorted, dor_maxes_pct_unsorted, max_pct_unsorted_fname,
          xlabel_pct, ylabel, title_pct_max, True)

        make_and_save_plot(short_rule_names_min_pct_unsorted, bg_mins_pct_unsorted,
          dor_mins_pct_unsorted, min_pct_unsorted_fname, xlabel_pct, ylabel,
          title_pct_min, True)

        make_and_save_plot(short_rule_names_max_pct_sorted, bg_maxes_pct_sorted,
          dor_maxes_pct_sorted, max_pct_sorted_fname, xlabel_pct, ylabel,
          title_pct_max, True)

        make_and_save_plot(short_rule_names_min_pct_sorted, bg_mins_pct_sorted,
          dor_mins_pct_sorted, min_pct_sorted_fname, xlabel_pct, ylabel,
          title_pct_min, True)

        make_and_save_plot(short_rule_names_max_count_sorted, bg_maxes_count_sorted,
          dor_maxes_count_sorted, max_count_sorted_fname, xlabel_count, ylabel,
          title_count_max, False)

        make_and_save_plot(short_rule_names_min_count_sorted, bg_mins_count_sorted,
          dor_mins_count_sorted, min_count_sorted_fname, xlabel_count, ylabel,
          title_count_min, False)

        make_and_save_plot(short_rule_names_max_count_small_sorted,
          bg_maxes_count_small_sorted, dor_maxes_count_small_sorted,
          max_count_small_sorted_fname, xlabel_count, ylabel,
          title_count_small_max, False)

        make_and_save_plot(short_rule_names_min_count_small_sorted,
          bg_mins_count_small_sorted, dor_mins_count_small_sorted,
          min_count_small_sorted_fname, xlabel_count, ylabel,
          title_count_small_min, False)



    # put together the individual token results
    token_results.append("~~ Individual Token Results ~~")
    token_results.append("\n".join(token_by_token))

    # create all the result text
    overall_result_text = "\n".join(overall_results)
    dialect_result_text = "\n".join(dialect_results)
    rule_result_text = "\n".join(rule_results)
    token_result_text = "\n".join(token_results)
    evaluation_result_text = "\n".join(evaluation_info)
    return (overall_result_text, dialect_result_text, rule_result_text, token_result_text, evaluation_result_text)

# given the individual pieces from generate_results, not including the accuracy
# evaluation results, combine them into a single piece of text
def combine_results(overall, dialect, rule, token):
    s = "-------OVERALL RESULTS:-------\n" + overall
    s += "\n-------SPECIFIC RESULTS:-------\n"
    s += dialect + "\n" + rule + "\n" + token
    return s

# given the individual pieces from generate_results, including the accuracy
# evaluation results, combine them into a single piece of text
def combine_results_eval(overall, dialect, rule, token, evaluation):
    s = "-------OVERALL RESULTS:-------\n" + overall
    s += "\n-------SPECIFIC RESULTS:-------\n"
    s += dialect + "\n" + rule + "\n" + token + "\n" + evaluation
    return s
