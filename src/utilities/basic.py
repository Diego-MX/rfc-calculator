
from functools import reduce, partial, wraps
from re import sub as str_sub, escape as re_escape

def move_args(func, k): 
    """Change k argument to last position."""
    @wraps(func)
    def new_func(*new_args): 
        args = list(new_args)
        args.insert(k, args.pop())
        return func(*args)
    return new_func


def identity(x): return x
 
def eval_func(func, *args, **kwargs): return func(*args, **kwargs)

def compose_2(inner, outer): return lambda x: outer(inner(x))


compose_ls = partial(move_args(reduce, 1), compose_2, identity)
# compose_ls = lambda fn_ls: reduce(compose_2, fn_ls, identity)

arg0_to_end = partial(move_args, k=0)
arg0_to_end = partial(move_args, k=0)


def method_as_func(method, *args):
    '''Change the order of the arguments: 
    For an object X with method M its evaluation 
    X.M(*args) is called as METHOD_AS_FUNC(M, *args)(X)
    '''
    # Pretty challenge to resolve this with functionals, instead of lambdas.
    # the_function = lambda x: x.method(*args)
    the_function = compose_2(
        partial(arg0_to_end(getattr), method), 
        partial(arg0_to_end(eval_func), *args))
    return the_function


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
        raise Exception("CHARS_IN and CHARS_OUT must have the same length.")
    return str_subed



