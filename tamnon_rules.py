# -*- coding: utf-8 -*-
# This file contains the list of rules, function testers for those rules, and
# test data for the rules.

import re
import tamnon_utils as t_utils


# --- helper functions --

# Remove diacritics and past augments from a present or imperfect form
def present_stem_prune(form, tense):
    res = form
    if (tense == "imperf"):
        if (form[0:2] == "e)"):
            res = form[2:]
    return t_utils.remove_diacritics(res)

# return true if this is an alpha contract
def is_a_contract(lemma):
    l = t_utils.remove_diacritics(lemma)
    active_end = l[-2:]
    deponent_end = l[-5:]
    return (active_end == "aw" or deponent_end == "aomai")

# return true if lemma corresponds to a mi verb
def is_mi_verb(lemma):
    # removes diacritics and digits from the text
    clean_form = re.sub(r'\)|\(|/|=|\\|&|\+|\||\'|[\d]', '', lemma)
    if (clean_form[-2:] == "mi"):
        return True
    return False

# return true if the tense uses secondary endings
def is_secondary_endings(tense):
    return (tense == "imperf" or tense == "aor")

# return true if this parse is a participle whose feminine nominative would
# have a long h in attic
def is_long_a_ppl(form_data):
    if (form_data["pos"] == "part" and ("voice" in form_data)):
        voice = form_data["voice"]
        return (voice == "mp" or voice == "mid")

# return true if this parse is a participle whose feminine nominative would
# have a short a in attic
def is_short_a_ppl(form_data):
    if (form_data["pos"] == "part" and ("voice" in form_data) and
      ("tense" in form_data)):
        voice = form_data["voice"]
        tense = form_data["tense"]
        return ((voice == "pass" and tense == "aor") or voice == "act")

# return true if this lemma is not ei)mi/ or one of its compounds.
# we lose compounds of ei)=mi, "to go", as a casualty, but catching less
# is better than getting nothing.
def not_eimi(lemma):
    clean_lemma = re.sub(r'[\d]', '', t_utils.remove_diacritics(lemma))
    if (len(clean_lemma) > 4):
        end = clean_lemma[-4:]
    else:
        end = clean_lemma
    return (not(lemma == "ei)mi/") and not(end == "eimi"))
#--------------------------------------------------
# rule testers

def Rule_SW_1(info):
    form_data = info[0]
    lemma = form_data["lemma"]
    if (lemma == "pou=" or lemma == "o(/pou" or lemma == "au)tou=" or
        lemma == "o(mou=" or lemma == "a(mou=" or lemma == "dh/pou"):
        return t_utils.ATTIC

    return t_utils.EITHER

def Rule_SW_2(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "ei)"):
        if (form == "ei)"):
            return t_utils.ATTIC
        if (form == "ai)"):
            return t_utils.DORIC
    if (lemma == "ei)/qe"):
        if (form == "ei)/qe"):
            return t_utils.ATTIC
        if (form == "ai)/qe"):
            return t_utils.DORIC
    if (lemma == "ai)/qe"):
        return t_utils.DORIC
    if (lemma == "e)a/n"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_3(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "a)/n"):
        if (form == "a)/n"):
            return t_utils.ATTIC
        #ke technically not Doric but I'll count it for now. #EPIC
        if (form == "ka" or form == "ke"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_4(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "i(ero/s"):
        form_start = form[0:3]
        if (form_start == "i(e"):
            return t_utils.ATTIC
        elif (form_start == "i(a"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_5(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "*)/artemis"):
        return t_utils.ATTIC
    if (lemma == "*)/artamis"):
        return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_6a(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "dei/lomai2"):
        return t_utils.DORIC
    if (lemma == "bou/lomai"):
        form_start = form[0:2]
        if (form_start == "bo"):
            return t_utils.ATTIC
        elif (form_start == "dh"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_6b(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if ((lemma == "te/mnw" or lemma == "te/mnw2") and ("tense" in form_data)):
        tense = form_data["tense"]
        if (tense == "pres" or tense == "imperf"):
            form_start = (present_stem_prune(form, tense))[0:2]
            if (form_start == "te"):
                return t_utils.ATTIC
            elif (form_start == "ta"):
                return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_6c(info):
    form_data = info[0]
    lemma = form_data["lemma"]
    if (lemma == "o)bolo/s"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_8(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "su/"):
        form_start = form[0:1]
        if (form_start == "s"):
            return t_utils.ATTIC
        elif (form_start == "t"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_9(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "pra=tos"):
        return t_utils.DORIC
    if (lemma == "prw=tos"):
        return t_utils.ATTIC
    if (lemma == "pro/teros"):
        form_start = form[0:3]
        if (form_start == "pro"):
            return t_utils.ATTIC
        if (form_start == "pra"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_12(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "tessara/konta"):
        form_start = form[0:5]
        if (form_start == "tetta"): #tettara/konta
            return t_utils.ATTIC
        elif (form_start == "tetrw"): #tetrw/konta
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_13(info):
    form_data = info[0]
    lemma = form_data["lemma"]
    if (lemma == "teo/s"):
        return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_14(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "e)gw/" and form == "e)mou="):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_15(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "o("):
        if (form == "oi(/" or form == "ai(/"):
            return t_utils.ATTIC
        elif (form == "toi/" or form == "tai/"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_17(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "e(sti/a"):
        if (form[0] == "i"):
            return t_utils.DORIC
        else:
            return t_utils.ATTIC
    if (lemma == "e(stia/w"):
        if (form[0] == "i"):
            return t_utils.DORIC
        else:
            return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_18(info):
    form_data = info[0]
    lemma = form_data["lemma"]
    if (lemma == "a(/teros"):
        return t_utils.DORIC
    if (lemma == "e(/teros"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_19(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "o)/noma"):
        form_start = t_utils.remove_diacritics(form)[0:3]
        if (form_start == "ono"):
            return t_utils.ATTIC
        elif (form_start == "onu"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_20(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "de/xomai" and ("tense" in form_data)):
        tense = form_data["tense"]
        if (tense == "pres" or tense == "imperf"):
            form_start = (present_stem_prune(form, tense))[0:3]
            if (form_start == "dex"):
                return t_utils.ATTIC
            elif (form_start == "dek"):
                return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_21(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "gi/gnomai" and ("tense" in form_data)):
        tense = form_data["tense"]
        if (tense == "pres" or tense == "imperf"):
            form_start = (present_stem_prune(form, tense))[0:3]
            if (form_start == "gig"): #gignomai
                return t_utils.ATTIC
            elif (form_start == "gin"): #ginomai
                return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_23(info):
    form_data = info[0]
    lemma = form_data["lemma"]
    if (lemma == "i(/kw"):
        return t_utils.DORIC
    if (lemma == "h(/kw"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_24(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "qesmo/s"):
        form_start = form[0]
        if (form_start == "q"):
            return t_utils.ATTIC
        elif (form_start == "t"):
            return t_utils.DORIC
    if (lemma == "teqmo/s"):
        return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_25(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "pron" and (lemma == "e)gw/" or lemma == "su/") and
      ("number" in form_data) and ("case" in form_data)):
        number = form_data["number"]
        case = form_data["case"]
        if (lemma == "e)gw/" and number == "pl"):
            if (case == "nom"):
                if (form == "h(mei=s"):
                    return t_utils.ATTIC
                elif (form == "a(me/s" or form == "a)/mmes"): #a)/mmes is aeolic
                    return t_utils.DORIC
            if (case == "dat"):
                if (form == "h(mi=n"):
                    return t_utils.ATTIC
                elif (form == "a(mi/n" or form == "a)/mmin"): #a)/mmin is aeolic
                    return t_utils.DORIC
            if (case == "acc"):
                if (form == "h(me/as" or form == "h(ma=s"):
                    return t_utils.ATTIC
                elif (form == "a(me/"):
                    return t_utils.DORIC
        if (lemma == "su/" and number == "pl"):
            if (case == "nom"):
                if (form == "u(mei=s"):
                    return t_utils.ATTIC
                elif (form == "u(me/s"):
                    return t_utils.DORIC
            if (case == "dat"):
                if (form == "u(mi=n"):
                    return t_utils.ATTIC
                elif (form == "u(mi/n"):
                    return t_utils.DORIC
            if (case == "acc"):
                if (form == "u(me/as" or form == "u(ma=s"):
                    return t_utils.ATTIC
                elif (form == "u(me/"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_26a(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (lemma == "ei)mi/" and pos == "verb" and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and ("tense" in form_data)
          and ("person" in form_data) and ("number" in form_data)):
            person = form_data["person"]
            number = form_data["number"]
            tense = form_data["tense"]
            if (person == "3rd" and number == "sg" and tense == "imperf" and
              mood == "ind"):
                if (form == "h)=n"):
                    return t_utils.ATTIC
                elif (form == "h)=s"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_26b(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (lemma == "ei)mi/" and pos == "verb" and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("tense" in form_data) and ("person" in form_data) and
          ("number" in form_data)):
            person = form_data["person"]
            number = form_data["number"]
            tense = form_data["tense"]
            if (person == "3rd" and number == "pl" and tense == "imperf" and
              mood == "ind"):
                if (form == "h)=san"):
                    return t_utils.ATTIC
                elif (form == "h)=n"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_27(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "e)gw/" and ("number" in form_data) and
      ("case" in form_data)):
        number = form_data["number"]
        case = form_data["case"]
        if (number == "sg" and case == "dat"):
            if (form == "e)moi/"):
                return t_utils.ATTIC
            elif (form == "e)mi/n"):
                return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_28(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "pei=2"):
        return t_utils.DORIC
    if (lemma == "toutei/"):
        return t_utils.DORIC
    if (lemma == "tau/th|"):
        return t_utils.ATTIC
    if (lemma == "thnei="):
        return t_utils.DORIC
    if (lemma == "e)kei="):
        if (form == "thnei="):
            return t_utils.DORIC
        else:
            return t_utils.ATTIC
    if (lemma == "au)tei="):
        return t_utils.DORIC
    if (lemma == "au)tou="):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_30(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "e)/nqen"):
        return t_utils.ATTIC
    elif (lemma == "e)/swqen"):
        return t_utils.ATTIC
    elif (lemma == "o(/qen"):
        return t_utils.ATTIC
    elif (lemma == "o(po/qen"):
        return t_utils.ATTIC
    elif (lemma == "po/qen"):
        return t_utils.ATTIC
    elif (lemma == "pro/sqen"):
        if (form == "pro/sqen"):
            return t_utils.ATTIC
        elif (form == "pro/sqa"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_31(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "o(/te" or lemma == "o(/te2"):
        return t_utils.ATTIC
    if (lemma == "to/te"):
        if (form == "to/te"):
            return t_utils.ATTIC
        if (form == "to/ka"):
            return t_utils.DORIC
    if (lemma == "tote/" or lemma == "tote/2"):
        return t_utils.ATTIC
    if (lemma == "pote/" or lemma == "pote/2" or lemma == "po/te"):
        stripped_form = t_utils.remove_diacritics(form)
        if (stripped_form == "pote"):
            return t_utils.ATTIC
        if (stripped_form == "poka"):
            return t_utils.DORIC
    if (lemma == "o(po/te"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_33(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "e(/ws"):
        if (form == "e(/ws"):
            return t_utils.ATTIC
        elif (form == "a(=s" or form == "a(/s"): #second from perseus
            return t_utils.DORIC

    return t_utils.EITHER

def Rule_SW_34(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "lao/s"):
        form_start = form[0:2]
        if (form_start == "le"):
            return t_utils.ATTIC
        elif (form_start == "la"):
            return t_utils.DORIC

    return t_utils.EITHER

def Rule_SW_35(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "qewro/s" or lemma == "qearo/s"):
        form_start = form[0:3]
        if (form_start == "qew"):
            return t_utils.ATTIC
        elif (form_start == "qea"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_36(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "koinw/n"):
        form_start = (t_utils.remove_diacritics(form))[0:5]
        if (form_start == "koinw"):
            return t_utils.ATTIC
        elif (form_start == "koina"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_37(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "xre/os" and form == "xre/ws"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_38(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "e)niau/sios"):
        return t_utils.ATTIC
    elif (lemma == "e)niau/tios"):
        return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_39(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "plhsi/os" or lemma == "plh/sios"):
        form_start = (t_utils.remove_diacritics(form))[0:4]
        if (form_start == "plhs"):
            return t_utils.ATTIC
        if (form_start == "plat"):
            return t_utils.DORIC
    return t_utils.EITHER

def Rule_SW_41(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma == "*)afrodi/sios"):
        return t_utils.ATTIC
    return t_utils.EITHER

def Rule_SW_42(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (lemma == "ei)mi/" and pos == "part" and ("tense" in form_data) and
      ("voice" in form_data)):
        tense = form_data["tense"]
        voice = form_data["voice"]
        if (tense == "pres" and voice == "act"):
            first_letter = (t_utils.remove_diacritics(form))[0]
            if (first_letter == "o"  or first_letter == "w"):
                return t_utils.ATTIC
            elif (first_letter == "e"):
                return t_utils.DORIC
    return t_utils.EITHER

# return true if this form should be examined by rule NE_1a
def proper_NE_1a_lemma(form_data, lem_extra):
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (lemma == "o(/s" or lemma == "o("):
        return True
    if (pos == "noun"):
        return (lem_extra == t_utils.H_A_STEM)
    elif (pos == "adj" and lem_extra == t_utils.ADJ_3_TERMINATION):
        ier = t_utils.remove_diacritics(lemma)[-3]
        is_ier = (ier == "e" or ier == "i" or ier == "r")
        return not(is_ier)
    elif (is_long_a_ppl(form_data)):
        return True
    return False


def Rule_NE_1a(info):
    form_data = info[0]
    lemma_info = info[1]
    form = form_data["form"]
    clean_form = t_utils.remove_diacritics(form)
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (proper_NE_1a_lemma(form_data, lemma_info)
      and ("gender" in form_data) and ("number" in form_data)):
        gender = form_data["gender"]
        number = form_data["number"]
        if (gender == "fem" and number == "sg" and ("case" in form_data)):
            case = form_data["case"]
            if (case == "nom"):
                if (clean_form[-1:] == "h"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "a"):
                    return t_utils.DORIC
            elif (case == "gen"):
                if (clean_form[-2:] == "hs"):
                    return t_utils.ATTIC
                elif (clean_form[-2:] == "as"):
                    return t_utils.DORIC
            elif (case == "dat"):
                if (clean_form[-2:] == "hi" or clean_form[-1:] == "h"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "ai" or clean_form[-1:] == "a"):
                    return t_utils.DORIC
            elif (case == "acc"):
                if (clean_form[-2:] == "hn"):
                    return t_utils.ATTIC
                elif (clean_form[-2:] == "an"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_NE_1b(info):
    form_data = info[0]
    lemma_info = info[1]
    form = form_data["form"]
    clean_form = t_utils.remove_diacritics(form)
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (((pos == "noun" and lemma_info == t_utils.SHORT_A_STEM) or
      is_short_a_ppl(form_data)) and ("gender" in form_data) and
      ("number" in form_data)):
        gender = form_data["gender"]
        number = form_data["number"]
        if (gender == "fem" and number == "sg" and ("case" in form_data)):
            case = form_data["case"]
            if (case == "gen"):
                if (clean_form[-2:] == "hs"):
                    return t_utils.ATTIC
                elif (clean_form[-2:] == "as"):
                    return t_utils.DORIC
            elif (case == "dat"):
                if (clean_form[-2:] == "hi" or clean_form[-1:] == "h"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "ai" or clean_form[-1:] == "a"):
                    return t_utils.DORIC
    return t_utils.EITHER


def Rule_NE_2(info):
    form_data = info[0]
    lemma_info = info[1]
    form = form_data["form"]
    clean_form = t_utils.remove_diacritics(form)
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "noun" and lemma_info == t_utils.H_A_STEM
      and ("gender" in form_data) and ("number" in form_data)):
        gender = form_data["gender"]
        number = form_data["number"]
        if (gender == "masc" and number == "sg" and ("case" in form_data)):
            case = form_data["case"]
            if (case == "nom"):
                if (clean_form[-2:] == "hs"):
                    return t_utils.ATTIC
                elif (clean_form[-2:] == "as"):
                    return t_utils.DORIC
            elif (case == "gen"):
                if (clean_form[-2:] == "ou"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "a"):
                    return t_utils.DORIC
            elif (case == "dat"):
                if (clean_form[-2:] == "hi" or clean_form[-1:] == "h"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "ai" or clean_form[-1:] == "a"):
                    return t_utils.DORIC
            elif (case == "acc"):
                if (clean_form[-2:] == "hn"):
                    return t_utils.ATTIC
                elif (clean_form[-2:] == "an"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_NE_3(info):
    form_data = info[0]
    lemma_info = info[1]
    form = form_data["form"]
    clean_form = t_utils.remove_diacritics(form)
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if ((pos == "noun" and (lemma_info == t_utils.H_A_STEM or
      lemma_info == t_utils.EIR_A_STEM or
      lemma_info == t_utils.SHORT_A_STEM)) or (pos == "adj" and
      (lemma_info == t_utils.ADJ_3_TERMINATION)) or (lemma == "o(/s") or
      (pos == "part" and ("gender" in form_data) and form_data["gender"] == "fem")
      and ("case" in form_data) and ("number" in form_data)):
        number = form_data["number"]
        case = form_data["case"]
        if (case == "gen" and number == "pl"):
            if (form[-3:] == "w=n" or clean_form[-2:] == "wn"):
                return t_utils.ATTIC
            elif (form[-3:] == "a=n" or clean_form[-2:] == "an"): #second cuz p. sux
                return t_utils.DORIC
    return t_utils.EITHER

def Rule_NE_4(info):
    form_data = info[0]
    lemma_info = info[1]
    form = form_data["form"]
    clean_form = t_utils.remove_diacritics(form)
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "noun" and lemma_info == t_utils.W_STEM
      and ("case" in form_data) and ("number" in form_data)):
        number = form_data["number"]
        case = form_data["case"]
        if (number == "sg"):
            if (case == "gen"):
                if (clean_form[-3:] == "ews"):
                    return t_utils.ATTIC
                elif (clean_form[-3:] == "eos"):
                    return t_utils.DORIC
                # not from Buck, but we'll count it for now
                elif (clean_form[-3:] == "hos"):
                    return t_utils.DORIC
            elif (case == "acc"):
                if (clean_form[-2:] == "ea"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "h"):
                    return t_utils.DORIC
        elif (number == "pl"):
            if (case == "nom"):
                if (form[-3:] == "h=s"):
                    return t_utils.ATTIC
    return t_utils.EITHER

def Rule_NE_5(info):
    form_data = info[0]
    lemma_info = info[1]
    form = form_data["form"]
    clean_form = t_utils.remove_diacritics(form)
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "noun" and lemma_info == t_utils.I_STEM
      and ("case" in form_data) and ("number" in form_data)):
        number = form_data["number"]
        case = form_data["case"]
        if (number == "sg"):
            if (case == "gen"):
                if (clean_form[-3:] == "ews"):
                    return t_utils.ATTIC
                elif (clean_form[-3:] == "ios"):
                    return t_utils.DORIC
            elif (case == "dat"):
                if (clean_form[-2:] == "ei"):
                    return t_utils.ATTIC
                elif (clean_form[-1:] == "i"):
                    return t_utils.DORIC
        elif (number == "pl"):
            if (case == "nom" or case == "voc"):
                if (clean_form[-3:] == "eis"):
                    return t_utils.ATTIC
                elif (clean_form[-3:] == "ies"):
                    return t_utils.DORIC
            elif (case == "gen"):
                if (clean_form[-3:] == "ewn"):
                    return t_utils.ATTIC
                elif (clean_form[-3:] == "iwn"):
                    return t_utils.DORIC
            elif (case == "dat"):
                if (clean_form[-3:] == "isi" or clean_form[-4:] == "iesi"):
                    return t_utils.DORIC
                elif (clean_form[-3:] == "esi" or clean_form[-4:] == "esin"):
                    return t_utils.ATTIC
                #second from Pindar
            elif (case == "acc"):
                if (clean_form[-3:] == "eis"):
                    return t_utils.ATTIC
                elif (clean_form[-2:] == "is" or clean_form[-3:] == "ias"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_1(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("tense" in form_data) and ("person" in form_data) and
          ("number" in form_data) and ("voice" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            tense = form_data["tense"]
            voice = form_data["voice"]
            if (number == "dual" and person == "3rd" and voice == "act" and
              is_secondary_endings(tense)):
                form_end = form[-3:]
                if (form_end == "thn"):
                    return t_utils.ATTIC
                if (form_end == "tan"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_2(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("tense" in form_data) and ("person" in form_data) and
          ("number" in form_data) and ("voice" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            tense = form_data["tense"]
            voice = form_data["voice"]
            if (number == "sg" and (voice == "mid" or voice == "mp") and
              person == "1st" and is_secondary_endings(tense)):
                form_end = form[-3:]
                if (form_end == "mhn"):
                    return t_utils.ATTIC
                if (form_end == "man"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_3(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and is_a_contract(lemma) and ("mood" in form_data) and
      ("tense" in form_data) and ("voice" in form_data)):
        tense = form_data["tense"]
        mood = form_data["mood"]
        voice = form_data["voice"]
        no_diacritics = t_utils.remove_diacritics(form)
        one_end = no_diacritics[-1:]
        two_end = no_diacritics[-2:]
        three_end = no_diacritics[-3:]
        four_end = no_diacritics[-4:]
        if (tense == "pres" and (mood == "ind" or mood == "subj") and
          ("number" in form_data) and ("person" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            if (voice == "act"):
                if (number == "sg" and person == "2nd"):
                    my_end = two_end
                    if (my_end == "as"):
                        return t_utils.ATTIC
                    elif (my_end == "hs"):
                        return t_utils.DORIC
                elif (number == "sg" and person == "3rd"):
                    my_end = one_end
                    if (my_end == "a"):
                        return t_utils.ATTIC
                    elif (my_end == "h"):
                        return t_utils.DORIC
                elif (number == "pl" and person == "2nd"):
                    my_end = three_end
                    if (my_end == "ate"):
                        return t_utils.ATTIC
                    elif (my_end == "hte"):
                        return t_utils.DORIC
            elif (voice == "mp"):
                if (number == "sg" and person == "2nd"):
                    my_end = one_end
                    if (my_end == "a"):
                        return t_utils.ATTIC
                    elif (my_end == "h"):
                        return t_utils.DORIC
                elif (number == "sg" and person == "3rd"):
                    my_end = four_end
                    if (my_end == "atai"):
                        return t_utils.ATTIC
                    elif (my_end == "htai"):
                        return t_utils.DORIC
                elif (number == "pl" and person == "2nd"):
                    my_end = four_end
                    if (my_end == "asqe"):
                        return t_utils.ATTIC
                    elif (my_end == "hsqe"):
                        return t_utils.DORIC
        if (tense == "imperf" and mood == "ind" and
          ("number" in form_data) and ("person" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            if (voice == "act"):
                if (number == "sg" and person == "2nd"):
                    my_end = two_end
                    if (my_end == "as"):
                        return t_utils.ATTIC
                    elif (my_end == "hs"):
                        return t_utils.DORIC
                elif (number == "sg" and person == "3rd"):
                    my_end = one_end
                    if (my_end == "a"):
                        return t_utils.ATTIC
                    elif (my_end == "h"):
                        return t_utils.DORIC
                elif (number == "pl" and person == "2nd"):
                    my_end = three_end
                    if (my_end == "ate"):
                        return t_utils.ATTIC
                    elif (my_end == "hte"):
                        return t_utils.DORIC
            elif (voice == "mp"):
                if (number == "sg" and person == "3rd"):
                    my_end = three_end
                    if (my_end == "ato"):
                        return t_utils.ATTIC
                    elif (my_end == "hto"):
                        return t_utils.DORIC
                elif (number == "pl" and person == "2nd"):
                    my_end = four_end
                    if (my_end == "asqe"):
                        return t_utils.ATTIC
                    elif (my_end == "hsqe"):
                        return t_utils.DORIC
        if (tense == "pres" and mood == "inf"):
            if (voice == "act"):
                my_end = two_end
                if (my_end == "an"):
                    return t_utils.ATTIC
                elif (my_end == "hn"):
                    return t_utils.DORIC
            elif (voice == "mp"):
                my_end = no_diacritics[-5:]
                if (my_end == "asqai"):
                    return t_utils.ATTIC
                elif (my_end == "hsqai"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_4(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and is_mi_verb(lemma) and not_eimi(lemma)
      and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("tense" in form_data) and ("person" in form_data) and
          ("number" in form_data)):
            tense = form_data["tense"]
            number = form_data["number"]
            person = form_data["person"]
            if (number == "pl" and person == "3rd" and is_secondary_endings(tense)):
                f = t_utils.remove_diacritics(form)
                if (f[-3:] == "san"):
                    return t_utils.ATTIC
                elif (not (f[-5:] == "ousin") and f[-1:] == "n"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_5(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and is_mi_verb(lemma) and ("mood" in form_data) and
      ("voice" in form_data)):
        voice = form_data["voice"]
        mood = form_data["mood"]
        if (mood == "inf"):
            end = t_utils.remove_diacritics(form)[-3:]
            if (end == "nai"):
                return t_utils.ATTIC
            elif (end == "men"):
                return t_utils.DORIC

    return t_utils.EITHER

def Rule_VE_6(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and is_mi_verb(lemma) and not_eimi(lemma) and
      ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("tense" in form_data) and ("person" in form_data) and
          ("number" in form_data) and ("voice" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            tense = form_data["tense"]
            voice = form_data["voice"]
            if (number == "sg" and person == "3rd" and tense == "pres" and
              voice == "act" and mood == "ind"):
                end = t_utils.remove_diacritics(form)[-2:]
                if (end == "si"):
                    return t_utils.ATTIC
                elif (end == "ti"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_7(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and ("mood" in form_data) and not_eimi(lemma)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("tense" in form_data) and ("person" in form_data) and
          ("number" in form_data) and ("voice" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            tense = form_data["tense"]
            voice = form_data["voice"]
            if (number == "pl" and person == "3rd" and tense == "pres" and
              voice == "act"):
                clean_form = t_utils.remove_diacritics(form)
                if (clean_form[-2:] == "si"):
                    return t_utils.ATTIC
                elif (clean_form[-3:] == "nti"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_VE_8(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "verb" and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat") and
          ("person" in form_data) and ("number" in form_data) and
          ("voice" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            voice = form_data["voice"]
            if (number == "pl" and person == "1st" and voice == "act"):
                end = t_utils.remove_diacritics(form)[-3:]
                if (end == "men"):
                    return t_utils.ATTIC
                elif (end == "mes"):
                    return t_utils.DORIC
    return t_utils.EITHER

def Rule_NS_1(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    if (lemma.find("ss") >= 0):
        if (form.find("tt") >= 0):
            return t_utils.ATTIC
        if (form.find("ss") >= 0):
            return t_utils.DORIC

    return t_utils.EITHER

def Rule_NM_1(info):
    form_data = info[0]
    form = form_data["form"]
    lemma = form_data["lemma"]
    pos = form_data["pos"]
    if (pos == "noun" and ("case" in form_data) and ("number" in form_data)):
        case = form_data["case"]
        number = form_data["number"]
        if (case == "dat" and number == "pl"):
            clean_form = t_utils.remove_diacritics(form)
            if (clean_form[-3:] == "sin"):
                return t_utils.ATTIC
    if (pos == "verb" and ("mood" in form_data)):
        mood = form_data["mood"]
        if (not (mood == "inf" or mood == "imperat")  and
          ("person" in form_data) and ("number" in form_data)):
            number = form_data["number"]
            person = form_data["person"]
            clean_form = t_utils.remove_diacritics(form)
            if (person == "3rd" and number == "sg"):
                if (clean_form[-2:] == "en"):
                    return t_utils.ATTIC
            elif (person == "3rd" and number == "pl"):
                if (clean_form[-3:] == "sin"):
                    return t_utils.ATTIC
    return t_utils.EITHER


# list of rules. Each rule contains a function to test for that rule (defined
# above), a rule name, a shorthand for the rule, and a list of forms that
# the rule should categorize as Attic/Doric/Either.

rules_list = [
{"Tester": Rule_SW_1, "Rule_Name": "SW.1: Adverbs ending in -ou", "Short_Name": "SW.1",
  "Attic_Forms": [["pou=", -1], ["o(/pou", -1], ["au)tou=", -1], ["o(mou=", -1], ["a(mou=", -1], ["dh/pou", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_2, "Rule_Name": "SW.2: The conjunction ei)", "Short_Name": "SW.2",
  "Attic_Forms": [["ei)", -1], ["ei)/qe", -1], ["e)/an", -1]],
  "Doric_Forms": [["ai)", -1], ["ai)/qe", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_3, "Rule_Name": "SW.3: The particle a)/n", "Short_Name": "SW.3",
  "Attic_Forms": [["a)/n", -1]],
  "Doric_Forms": [["ka", -1], ["ke", -1]],
  "Either_Forms":  [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_4, "Rule_Name": "SW.4: i(aro/s = i(ero/s", "Short_Name": "SW.4",
  "Attic_Forms": [["i(ero/s", -1], ["i(erou=", -1], ["i(eroi/", -1]],
  "Doric_Forms": [["i(aro/s", -1], ["i(arou=", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_5, "Rule_Name": "SW.5: A)/rtamis = A)/rtemis", "Short_Name": "SW.5",
  "Attic_Forms": [["a)/rtemis", -1], ["a)rte/midi", -1]],
  "Doric_Forms": [["a)/rtamis", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_6a, "Rule_Name": "SW.6a: dei/lomai = bou/lomai", "Short_Name": "SW.6a",
  "Attic_Forms": [["bou/lomai", -1], ["bou/letai", -1]] ,
  "Doric_Forms": [["dei/lomai", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_6b, "Rule_Name": "SW.6b: ta/mnw = te/mnw", "Short_Name": "SW.6b",
  "Attic_Forms": [["te/mnw", -1], ["e)/temnon", -1]] ,
  "Doric_Forms": [["ta/mnw", -1], ["e)/tamnon", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_6c, "Rule_Name": "SW.6c: o)delo/s = o)bolo/s", "Short_Name": "SW.6c",
  "Attic_Forms": [["o)bolou=", -1]] ,
  "Doric_Forms": [] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_8, "Rule_Name": "SW.8: tu/ = su/", "Short_Name": "SW.8",
  "Attic_Forms": [["su/", -1], ["se/", -1]],
  "Doric_Forms": [["tu/", -1], ["te/", -1], ["ti/n", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_9, "Rule_Name": "SW.9: pra=tos = prw=tos", "Short_Name": "SW.9",
  "Attic_Forms": [["prw=tos", -1], ["prw/tou", -1], ["pro/teros", -1], ["pro/terai", -1]],
  "Doric_Forms": [["pra=tos", -1], ["pra/tois", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_12, "Rule_Name": "SW.12: tetrw/konta = tettara/konta", "Short_Name": "SW.12",
  "Attic_Forms": [["tettara/konta", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_13, "Rule_Name": "SW.13: Doric teo/s", "Short_Name": "SW.13",
  "Attic_Forms": [],
  "Doric_Forms": [["teo/s", -1], ["teou=", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_14, "Rule_Name": "SW.14: e)me/os = e)mou=", "Short_Name": "SW.14",
  "Attic_Forms": [["e)mou=", -1]],
  "Doric_Forms": [] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_15, "Rule_Name": "SW.15: toi/, tai/ = oi(/, ai(/", "Short_Name": "SW.15",
  "Attic_Forms": [["oi(/", -1], ["ai(/", -1]],
  "Doric_Forms": [["toi/", -1], ["tai/", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_17, "Rule_Name": "SW.17: i(sti/a = e(sti/a", "Short_Name": "SW.17",
  "Attic_Forms": [["e(sti/a", -1], ["e(sti/an", -1], ["e(stia=te", -1]],
  "Doric_Forms": [["i(sti/a", -1], ["i(sti/an", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_18, "Rule_Name": "SW.18: a(/teros = e(/teros", "Short_Name": "SW.18",
  "Attic_Forms": [["e(/teros", -1], ["e(/teron", -1]],
  "Doric_Forms": [["a(/teros", -1], ["a(/teron", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_19, "Rule_Name": "SW.19: o)/numa = o)/nomai", "Short_Name": "SW.19",
  "Attic_Forms": [["o)/noma", -1], ["o)no/mata", -1]],
  "Doric_Forms": [["o)/numa", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_20, "Rule_Name": "SW.20: de/komai = de/xomai", "Short_Name": "SW.20",
  "Attic_Forms": [["de/xomai", -1], ["e)de/xeto", -1]],
  "Doric_Forms": [["de/komai", -1], ["e)de/keto", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_21, "Rule_Name": "SW.21: gi/nomai = gi/gnomai", "Short_Name": "SW.21",
  "Attic_Forms": [["gi/gnomai", -1], ["gigno/meqa", -1]],
  "Doric_Forms": [["gi/nomai", -1], ["gino/meqa", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_23, "Rule_Name": "SW.23: i(/kw = h(/kw", "Short_Name": "SW.23",
  "Attic_Forms": [["h(/kw", -1], ["h(/cw", -1]],
  "Doric_Forms": [["i(/kw", -1], ["i(/keis", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_24, "Rule_Name": "SW.24: teqmo/s = qesmo/s", "Short_Name": "SW.24",
  "Attic_Forms": [["qesmo/s", -1], ["qesmoi/", -1]],
  "Doric_Forms": [["teqmo/s", -1], ["teqmoi/", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_25, "Rule_Name": "SW.25: Forms of the plural personal pronoun", "Short_Name": "SW.25",
  "Attic_Forms": [["h(mei=s", -1], ["h(mi=n", -1], ["h(me/as", -1], ["h(ma=s", -1], ["u(mei=s", -1], ["u(mi=n", -1], ["u(me/as", -1], ["u(ma=s", -1]],
  "Doric_Forms": [["a(me/s", -1], ["a(mi/n", -1], ["a(me/", -1], ["u(me/s", -1], ["u(mi/n", -1], ["u(me/", -1], ["a)/mmes", -1], ["a)/mmin", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["e)gw/", -1], ["su/", -1]]
},
{"Tester": Rule_SW_26a, "Rule_Name": "SW.26a: 3rd singular imperfect active of ei)mi/", "Short_Name": "SW.26a",
  "Attic_Forms": [["h)=n", -1]],
  "Doric_Forms": [["h)=s", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["ei)mi/", -1]]
},
{"Tester": Rule_SW_26b, "Rule_Name": "SW.26b: 3rd plural imperfect active of ei)/mi", "Short_Name": "SW.26b",
  "Attic_Forms": [["h)=san", -1]],
  "Doric_Forms": [["h)=n", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["h)=s", -1]]
},
{"Tester": Rule_SW_27, "Rule_Name": "SW.27: e)mi/n = e)moi/", "Short_Name": "SW.27",
  "Attic_Forms": [["e)moi/", -1]],
  "Doric_Forms": [["e)mi/n", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["e)gw/", -1]]
},
{"Tester": Rule_SW_28, "Rule_Name": "SW.28: Adverbs ending in -ei", "Short_Name": "SW.28",
  "Attic_Forms": [["tau/th|", -1], ["e)kei=", -1], ["au)tou=", -1]],
  "Doric_Forms": [["pei=", -1], ["toutei/", -1], ["thnei=", -1], ["au)tei=", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_30, "Rule_Name": "SW.30: Adverbs ending in -qen", "Short_Name": "SW.30",
  "Attic_Forms": [["e)/nqen", -1], ["e)/swqen", -1], ["o(/qen", -1], ["o(po/qen", -1], ["po/qen", -1], ["pro/sqen", -1]],
  "Doric_Forms": [["pro/sqa", -1]],
  "Either_Forms":  [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_31, "Rule_Name": "SW.31: Adverbs ending in -ka vs -te", "Short_Name": "SW.31",
  "Attic_Forms": [["to/te", -1], ["tote/", -1], ["po/te", -1], ["pote/", -1], ["o(po/te", -1]],
  "Doric_Forms": [["to/ka", -1], ["po/ka", -1], ["poka/", -1]],
  "Either_Forms":  [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_33, "Rule_Name": "SW.33: a(=s = e(/ws", "Short_Name": "SW.33",
  "Attic_Forms": [["e(/ws", -1]],
  "Doric_Forms": [["a(=s", -1], ["a(/s", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_34, "Rule_Name": "SW.34: lao/s = lew/s", "Short_Name": "SW.34",
  "Attic_Forms": [["lew/s", -1]],
  "Doric_Forms": [["laou=", -1], ["lao/s", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_35, "Rule_Name": "SW.35: qearo/s = qewro/s", "Short_Name": "SW.35",
  "Attic_Forms": [["qewro/s", -1], ["qew/rou", -1]],
  "Doric_Forms": [["qearo/s", -1], ["qearoi/", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_36, "Rule_Name": "SW.36: koina/n = koinw/n", "Short_Name": "SW.36",
  "Attic_Forms": [["koinw=n", -1], ["koinw=nes", -1]],
  "Doric_Forms": [["koina=n", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_37, "Rule_Name": "SW.37: xre/os = xre/ws", "Short_Name": "SW.37",
  "Attic_Forms": [["xre/ws", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_38, "Rule_Name": "SW.38: e)niau/tios = e)niau/sios", "Short_Name": "SW.38",
  "Attic_Forms": [["e)niau/sios", -1], ["e)niausi/ou", -1]],
  "Doric_Forms": [["e)niau/tios", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_39, "Rule_Name": "SW.39: plati/os = plhsi/os", "Short_Name": "SW.39",
  "Attic_Forms": [["plhsi/os", -1], ["plh/sios", -1], ["plhsi/ou", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_41, "Rule_Name": "SW.41: a)frodi/tios = a)frodi/sios", "Short_Name": "SW.41",
  "Attic_Forms": [["a)frodi/sios", -1], ["a)frodisi/ou", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_SW_42, "Rule_Name": "SW.42: The present participle of ei)mi/", "Short_Name": "SW.42",
  "Attic_Forms": [["ou)/shs", -1], ["o)/n", -1], ["o)/ntos", -1]],
  "Doric_Forms": [["e)ou/sas", -1], ["e)o/n", -1], ["e)o/ntos", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1], ["ei)si/n", -1]]
},
{"Tester": Rule_NE_1a, "Rule_Name": "NE.1a: Endings of singular feminine long alpha-stems", "Short_Name": "NE.1a",
  "Attic_Forms": [["gnw/mh", -1], ["gnw/mhs", -1], ["gnw/mh|", -1], ["gnw/mhn", -1], ["paideuome/nh", -1], ["paideuome/nhs", -1], ["pepaideume/nh", -1], ["pepaideume/nhs", -1], ["h(=s", -1], ["h(/n", -1]],
  "Doric_Forms": [["gnw/ma", -1], ["gnw/mas", -1], ["gnw/ma|", -1], ["gnw/man", -1], ["pepaideume/na", -1], ["pepaideume/nas", -1], ["a(=s", -1], ["a(/n", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["xw/ra", -1], ["a)ci/a", -1]]
},
{"Tester": Rule_NE_1b, "Rule_Name": "NE.1b: Endings of singular feminine short alpha-stems", "Short_Name": "NE.1b",
  "Attic_Forms": [["qala/tths", -1], ["qala/tth|", -1], ["paideuou/shs", -1]],
  "Doric_Forms": [["qala/ssas", -1], ["qala/ssa|", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["gefu/ras", -1], ["qa/latta", -1], ["qa/lattan", -1], ["paideuqei=sa", -1]]
},
{"Tester": Rule_NE_2, "Rule_Name": "NE.2: Endings of singular masculine alpha-stems", "Short_Name": "NE.2",
  "Attic_Forms": [["poli/ths", -1], ["poli/tou", -1], ["poli/th|", -1], ["poli/thn", -1]],
  "Doric_Forms": [["poli/tas", -1], ["poli=ta", -1], ["poli/ta|", -1], ["polita=n", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["xw/ra", -1], ["gnw/ma", -1]]
},
{"Tester": Rule_NE_3, "Rule_Name": "NE.3: Genitive plurals of alpha-stems", "Short_Name": "NE.3",
  "Attic_Forms": [["politw=n", -1], ["a)gorw=n", -1], ["mhxanw=n", -1], ["r(htorikw=n", -1], ["qalassw=n", -1], ["moirw=n", -1], ["paideuome/nwn", -1], ["pepaideume/nwn", -1], ["w(=n", -1]],
  "Doric_Forms": [["polita=n", -1], ["a)gora=n", -1], ["maxana/n", -1], ["qa/lassan", -1], ["moira=n", -1], ["lipou=san", -1], ["a(=n", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_NE_4, "Rule_Name": "NE.4: Endings for digamma-stems (e.g. basileu/s)", "Short_Name": "NE.4",
  "Attic_Forms": [["i(ppe/ws", -1], ["i(ppe/a", -1], ["i(pph=s", -1]],
  "Doric_Forms": [["basile/os", -1], ["basilh=", -1]],
  "Either_Forms":  [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["i(ppeu/s", -1]]
},
{"Tester": Rule_NE_5, "Rule_Name": "NE.5: Endings for iota-stems (e.g. po/lis)", "Short_Name": "NE.5",
  "Attic_Forms": [["po/lews", -1], ["po/lei", -1], ["po/leis", -1], ["polei=s", -1], ["po/lewn", -1], ["po/lesi", -1]],
  "Doric_Forms": [["po/lios", -1], ["po/li", -1], ["po/lies", -1], ["poli/wn", -1], ["po/lisi", -1], ["poli/esi", -1], ["po/lis", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1]]
},
{"Tester": Rule_VE_1, "Rule_Name": "VE.1: 3rd dual active secondary ending", "Short_Name": "VE.1",
  "Attic_Forms": [["e)fa/thn", -1], ["e)dido/thn", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1]]
},
{"Tester": Rule_VE_2, "Rule_Name": "VE.2: 1st singular middle secondary ending", "Short_Name": "VE.2",
  "Attic_Forms": [["i)do/mhn", -1], ["genoi/mhn", -1]],
  "Doric_Forms": [["i)do/man", -1], ["genoi/man", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1]]
},
{"Tester": Rule_VE_3, "Rule_Name": "VE.3: Alpha-contract endings", "Short_Name": "VE.3",
  "Attic_Forms": [["tima=|s", -1], ["tima=|", -1], ["tima=te", -1], ["tima=|", -1], ["tima=tai", -1], ["tima=sqe", -1], ["e)ti/mas", -1], ["e)ti/ma", -1], ["e)tima=te", -1], ["e)tima=to", -1], ["tima=n", -1], ["tima=sqai", -1], ["te/xna|", -1], ["e)texna=to", -1]],
  "Doric_Forms": [["timh=|s", -1], ["timh=|", -1], ["timh=|", -1], ["timhtai/", -1], ["timh=n", -1], ["te/xnh|", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1], ["timw=men", -1]]
},
{"Tester": Rule_VE_4, "Rule_Name": "VE.4: Athematic 3rd plural secondary ending", "Short_Name": "VE.4",
  "Attic_Forms": [["e)/dosan", -1], ["i(/stasan", -1]],
  "Doric_Forms": [["e)/don", -1], ["i(/stan", -1]] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1], ["di/dwmi", -1], ["'n", -1], ["en", -1], ["e)/peisin", -1], ["e)kpeta/sousin", -1]]
},
{"Tester": Rule_VE_5, "Rule_Name": "VE.5: Active infinitive -men vs -nai", "Short_Name": "VE.5",
  "Attic_Forms": [["dido/nai", -1], ["tiqe/nai", -1]],
  "Doric_Forms": [["dido/men", -1], ["ti/qemen", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1], ["di/dwmi", -1]]
},
{"Tester": Rule_VE_6, "Rule_Name": "VE.6: athematic 3rd singular present active ending.", "Short_Name": "VE.6",
  "Attic_Forms": [["di/dwsi", -1], ["ti/qhsi", -1]],
  "Doric_Forms": [["di/dwti", -1], ["ti/qhti", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1], ["di/dwmi", -1]]
},
{"Tester": Rule_VE_7, "Rule_Name": "VE.7: 3rd plural present active endings", "Short_Name": "VE.7",
  "Attic_Forms": [["paideu/ousi", -1]],
  "Doric_Forms": [["paideu/onti", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1], ["a)/peisi", -1]]
},
{"Tester": Rule_VE_8, "Rule_Name": "VE.8: 1st plural active ending", "Short_Name": "VE.8",
  "Attic_Forms": [["ti/qemen", -1], ["paideu/omen", -1]],
  "Doric_Forms": [] ,
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1]]
},
{"Tester": Rule_NS_1, "Rule_Name": "NS.1: Doric ss = Attic tt", "Short_Name": "NS.1",
  "Attic_Forms": [["qa/latta", -1], ["te/ttara", -1]],
  "Doric_Forms": [["qa/lassa", -1], ["te/ssara", -1]],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1]]
},
{"Tester": Rule_NM_1, "Rule_Name": "NM.1: Nu Movable (simple)", "Short_Name": "NM.1",
  "Attic_Forms": [["paideu/ousin", -1], ["po/lisin", -1], ["e)pai/deusen", -1]],
  "Doric_Forms": [],
  "Either_Forms": [["xe/ras", -1], ["paideu/w", -1], ["paideu/ete", -1], ["po/lin", -1], ["u(po/", -1], ["po/lis", -1]]
}
]

# information in an individual parse.
# parse:
# "dialect" : dialect
# "form" : the form as it appears
# "pos": part of speech
# "expanded form": ??
# "feature": ???
# "lemma": the actual lemma

# pos = verb:
# "mood", "number" "person" "tense" "voice"

# pos = adjective:
# "case" "gender" "number"

# pos = noun:
# "case" "gender" "number"
