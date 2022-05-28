import re
from clldutils.text import split_text_with_context

languages = sorted(set([
            "P", "PI", "Tn", "Ts", "OE", "O", "En",
            "Yb", "Va", "TA", "TR", "Y MA", "Y MA",
            "Vb Va TA", "Va TA", "Y MA", "Va T",
            "O", "Es", "MA", "Vb", "TR", "TA", "VA",
            "TEP", "P", "PI", "P.PI",
            "Ma", "E", "Vb Va", "Va Vb",
            "Va", "Vb", "TA", "Va TA",
            "MA",
            "Vb Va", "Va TA",
            "TA", "MA",
            "V",
            "VB", "YMA", 
            "Y.MA",
            "Y MA", "Y", "En"
            ]))


def parse_word(word):
    words = [w.strip() for w in word.split(";")]
    out = []
    for word in words:
        forms, concept = [], []
        for entry in split_text_with_context(word, brackets={'"': '"'},
                separators=",;"):
            entry = entry.strip()
            if entry.startswith('"') and entry.endswith('"'):
                concept += [entry[1:-1].strip()]
            else:
                forms += [entry.strip()]
        if len(concept) == 1:
            for f in forms:
                out += [(f, concept[0])]
        else:
            for f in forms:
                out += [(f, "")]

    return out

def parse_languages(rowx):
    row = rowx.replace(', "', ' "')
    languages = sorted(set([
            "P", "PI", "Tn", "Ts", "OE", "O", "En",
            "Yb", "Va", "TA", "TR", "Y MA", "Y MA",
            "Vb Va TA", "Va TA", "Y MA", "Va T",
            "O", "Es", "MA", "Vb", "TR", "TA", "VA",
            "TEP", "P", "PI", "P.PI",
            "Ma", "E", "Vb Va", "Va Vb",
            "Va", "Vb", "TA", "Va TA",
            "MA",
            "Vb Va", "Va TA",
            "TA", "MA",
            "V", "P PI",
            "VB", "YMA", 
            "Y.MA",
            "Y MA", "Y", "En"
            ]))
    for lng in languages:
        row = row.replace(", "+lng+" ", "; "+lng+" ")
    out = []
    for itm in row.split("; "):
        first = itm[:itm.index(" ")].strip()
        rest = itm[itm.index(" "):].strip().replace(' "', ', "')
        forms = parse_word(rest)
        out += [(first, forms)]
    return out


def parse_entry(line):
    head = line[:line.index(" ")]
    rest = line[line.index(" "):]
    proto = parse_word(rest[:rest.index(". -")])
    rest = rest[rest.index(". -")+4:]
    
    return head, proto, parse_languages(rest)

def clean(text):
    chars = {
        "3": "3",
        ";": ";",
        "Y МА": "Y MA",
        "Y": "Y", "М": "M", "А": "A",
        "4": "4",
        "О": "O",
        "Т": "T",
        "*": "*",
        "8": "8",
        "о": "o",
        "А": "A",
        "é": "é",
        "0": "0",
        "ü": "ü",
        "1": "1",
        "ú": "ú",
        "г": "r",
        "7": "7",
        "á": "á",
        "Р": "P",
        "9": "9",
        "5": "5",
        "2": "2",
        "-": "-",
        "е": "e",
        "р": "p",
        ",": ",",
        "ñ": "ñ",
        '"': '"',
        "6": "6",
        "т": "t",
        " ": " ",
        "í": "í",
        "~": "-",
        "а": "a",
        "'": "'",
        "ɨ": "ɨ",
        "с": "c",
        "Е": "E",
        ")": ")",
        "(": "(",
        "?": "?",
        ".": ".",
        "М": "M",
        "ó": "ó"}

    return "".join([chars.get(t, t) for t in text])

data = [r.strip() for r in open("lionnet-new.txt").readlines()]
D = {0: ["doculect", "concept", "concept_in_source", "value", "form", "entry", "cog"]}
idx = 1
errs = set()
for i, row in enumerate(data):
    try:
        head, forms, rest = parse_entry(clean(row))
        for form, concept in forms:
            D[idx] = ["Proto", concept, "", form, form, row, head]
            idx += 1
        for lngs, frms in rest:
            for lng in lngs.split("."):
                for frm, cnc in frms:
                    if not cnc.strip():
                        cnc = concept
                    if '_"' in frm:
                        frm, cis = frm.split('_"')
                        cis = cis.strip(".").strip('"')
                    else:
                        frm, cis = frm, ""
                    if frm[0].upper() == frm[0] and frm[0] not in "'-"+'"1':
                        lngs = {"Vb": "Vb",
                                "Es": "Es",
                                "Ma": "Ma", "TA": "TA","MA": "MA","En": "En","On": "On",
                                "TR": "TR","T": "T","PM": "PM","Va": "Va","PI": "PI"
                                }
                        D[idx] = [lngs[frm.split(" ")[0]], cnc, cis, frm,
                            " ".join(frm.split(" ")[1:]), row, head]
                        idx += 1
                    D[idx] = [lng, cnc, cis, frm, frm, row, head]
                    idx += 1

    except:
        print(row)
for err in errs:
    print(err)
from lingpy import *
wl = Wordlist(D)
wl.output("tsv", filename="yotonahua", ignore="all", prettify=False)
