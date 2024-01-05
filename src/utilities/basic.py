
from functools import reduce, partial, wraps
from re import sub as str_sub, escape as re_escape
from unidecode import unidecode 


def constant(yy): 
    return lambda xx: yy


def move_args(func, k): 
    """Change k argument to last position."""
    @wraps(func)
    def new_func(*new_args): 
        args = list(new_args)
        args.insert(k, args.pop())
        return func(*args)
    return new_func

 
def eval_func(func, *args, **kwargs): 
    return func(*args, **kwargs)


arg0_to_end = partial(move_args, k=0)



def str_multisub(x_str, sub_dict, escape=False): 
    if escape: 
        f_reducer = lambda x, k_v: str_sub(re_escape(k_v[0]), k_v[1], x)
    else: 
        f_reducer = lambda x, k_v: str_sub(k_v[0], k_v[1], x)
    
    str_subed = reduce(f_reducer, sub_dict.items(), x_str)
    return str_subed


def str_iconv(x_str, chars_in, chars_out): 
    if len(chars_in) == len(chars_out):
        sub_dict  = dict(zip(chars_in[:], chars_out[:]))
        str_subed = str_multisub(x_str, sub_dict)
    else: 
        raise ValueError("CHARS_IN and CHARS_OUT must have the same length.")
    return str_subed


class partial2(partial):    # pylint: disable=invalid-name,too-few-public-methods
    """An improved version of partial which accepts Ellipsis (...) as a placeholder."""
    __module__ = 'epic_py'

    def __call__(self, *args, **keywords):
        keywords = {**self.keywords, **keywords}
        iargs = iter(args)
        args = (next(iargs) if arg is ... else arg for arg in self.args)
        return self.func(*args, *iargs, **keywords)


str_delatinize = unidecode
