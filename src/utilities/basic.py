
# pylint: disable=invalid-name,too-few-public-methods
from functools import reduce, partial
from re import sub as str_sub, escape as re_escape
from unidecode import unidecode 
 

def str_multisub(x_str, sub_dict, escape=False): 
    keyer = lambda k_v: re_escape(k_v[0]) if escape else k_v[0]
    f_reducer = lambda x, k_v: str_sub(keyer(k_v), k_v[1], x)
    return reduce(f_reducer, sub_dict.items(), x_str)


def str_iconv(x_str, chars_in, chars_out): 
    if len(chars_in) == len(chars_out):
        sub_dict  = dict(zip(chars_in[:], chars_out[:]))
        str_subed = str_multisub(x_str, sub_dict)
    else: 
        raise ValueError("CHARS_IN and CHARS_OUT must have the same length.")
    return str_subed


class partial2(partial):    
    """An improved version of partial with Ellipsis (...) as a placeholder."""
    def __call__(self, *args, **keywords):
        keywords = {**self.keywords, **keywords}
        iargs = iter(args)
        args = (next(iargs) if arg is ... else arg for arg in self.args)
        return self.func(*args, *iargs, **keywords)


def thread(val, *forms): 
    eval_ff = (lambda vv, ff: 
        partial2(*ff)(vv) if isinstance(ff, tuple) else ff(vv))
    return reduce(eval_ff, forms, val)    


str_delatinize = unidecode
