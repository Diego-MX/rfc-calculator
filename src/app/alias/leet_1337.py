
from functools import reduce
from operator import add 
import re
from typing import Tuple

import numpy as np
import pandas as pd
from toolz import itemmap
from src.utilities.basic import str_delatinize
from src.app.models import OffensiveResponse

# Changes all to lower. 
ALL_LOWER = True

def str_standard(word:str) -> str: 
    word_1 = word.lower() if ALL_LOWER else word
    word_2 = str_delatinize(word_1)
    return word_2

LEET_ONE = {
    "A": "4, @, ∆", 	"B": "8, |3, 13", 	"C": "(, [", 		    "D": "|), |>", 		
    "E": "3, €", 	    "F": "#, |=", 		"G": "6, 9, &, (_+", 	"H": "#, |-|", 		
    "I": "1, |, !", 	"J": "_|, ;, ]", 	"K": "|<, |{", 		    "L": "1, |_, 7", 		
    "M": "//, |/|, ^^",	"N": "||, //, []", 	"O": "0, (), Ø", 		"P": "|D, |>", 		
    "Q": "0_, (,)", 	"R": "|2, /2", 		"S": "5, $, §", 		"T": "7, +, †", 		
    "U": "|, ()", 		"V": "/, |/", 		"W": "//, ^/, \V/", 	"X": "><, }{, *", 		
    "Y": "`/, ¥", 		"Z": "2, >_" }

# Convertir diccionario: 
# 0. Por ejemplo wikipedia: copy-paste
# 1. Convertir a diccionario:  [VIM] :25,52s/([A-Z]): (.*)/'\1': "\2",
# 2. Escapar comillas:  [VIM] :25,52s/\"(?!,$)/\\"/g
#       [VIM]: 25,52s/: \\"/: "/g
# 3. Cambiar comas sin espacios (verificando):  [VIM]: :25,52s/,(?![ $\}])/, /g  # Verificar cambios. 

LEET_TWO = {
    "A": "∆, 4, /-\, /_\, @, /\, Д, а",
    "B": "8, |3, 13, |}, |:, |8, 18, 6, |B, |8, lo, |o, j3, ß, в, ь", 
    "C": "<, {, [, (, ©, ¢, с", 
    "D": "|), |}, |], |>", 
    "E": "3, £, ₤, €, е", 
    "F": "7, |=, ph, |#, |\", ƒ", 
    "G": "9, [, -, [+, 6, C-", 
    "H": "#, 4, |-|, [-], {-}, }-{, }{, |=|, [=], {=}, /-/, (-), )-(, :-:, I+I, н", 
    "I": "1, |, !, 9", 
    "J": "√, _|, _/, _7, 9,[1] _), _], _}",
    "K": "|<, 1<, l<, |{, l{", 
    "L": "|_, |, 1, ][", 
    "M": "44, |\/|, ^^, /\/\, /X\, []\/][, []V[], ][\\//][, (V), //., .\\, N\, м", 
    "N": "|\|, /\/, /V, ][\\][, И, и, п", 
    "O": "0, (), [], {}, <>, Ø, oh, Θ, о, ө", 
    "P": "|o, |O, |>, |*, |°, |D, /o, []D, |7, р", 
    "Q": "O_, 9, (,), 0, kw",
    "R": "|2, 12, .-, |^, l2, Я, ®", 
    "S": "5, $, §", 
    "T": "7, +, 7`, '|', `|`, ~|~, -|-, '][', т", 
    "U": "|_|, \_\, /_/, \_/, (_), [_], {_}", 
    "V": "\/", 
    "W": "\/\/, (/\), \^/, |/\|, \X/, \\', '//, VV, \_|_/, \\//\\//, Ш, 2u, \V/", 
    "X": "×, %, *, ><, }{, )(, Ж",
    "Y": "`/, ¥, \|/, Ч, ү, у", 
    "Z": "5, 7_, >_, (/)"}


def leet_prepare(char_dict:dict) -> dict:
    def one_leet(kkvv):
        key, val = map(str_standard, kkvv)
        joined = "|".join(map(re.escape, val.split(', ')))
        return (key, rf"({key}|{joined})")
    leeted = itemmap(one_leet, char_dict)
    return leeted

@np.vectorize
def word_2_leet(word:str, base_dict:dict=None) -> str:
    base_dict = base_dict or leet_prepare(LEET_ONE)
    char_2_reg = lambda cc: base_dict.get(cc, re.escape(cc))
    word = str_standard(word)
    to_plural = (' ' not in word) and (not word.endswith('s'))
    leet_1 = reduce(add, map(char_2_reg, word))
    leet_s = f"{char_2_reg('s')}?" if to_plural else ""
    return rf"\b{leet_1}{leet_s}\b"


offensive_df = (pd.read_feather('refs/temp/offensive-words.feather')
    .assign(w_regex = lambda df: word_2_leet(df['Phrase'])))


def offensive_alias(an_alias:str) -> OffensiveResponse:
    an_alias = str_standard(an_alias)
    for w_row in offensive_df.itertuples():
        if re.search(w_row.w_regex, an_alias): 
            pre_tuple = (an_alias, w_row.Phrase, w_row.Type)
            break
    else: 
        pre_tuple = (an_alias, None, None)
    return OffensiveResponse.from_gen(pre_tuple)


if __name__ == '__main__': 

    pruebas = ["VERGA", "VeRgA", "Don Vergas", "Señor Vergara", 
        "Senior vergara", "V3rG4", "Té de vergamota", "bergamota sí ok", "Vergüenza", 
        "Ano Cumpleaños", "Emiliano", "Super Ano", "4ñ05", ]
    
    for pp in pruebas: 
        none_to_empty = lambda ss: ss or ''
        print(f"{pp:16}: {offensive_alias(pp).fprint()}")

