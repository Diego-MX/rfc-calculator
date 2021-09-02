# Diego Villamil, CDMX
# Epic, 31 de agosto de 2021


from pathlib import Path
from regex import sub as str_sub


def copy_env(in_file=".env", out_file=None): 
    
    in_file = Path(in_file)
    if not in_file.is_file():
        raise Exception("IN_FILE must be a file.")

    if out_file is None:
        the_dir  = in_file.absolute().parent
        out_base = f"template_{in_file.name}" if in_file.suffix else f"template{in_file.name}"
        out_file = the_dir / out_base

    with in_file.open("r") as _in:
        the_lines = _in.readlines()
     
    mod_lines = [ str_sub( r'(.*)=( *)(\"?).*\3', r'\1=\2"<value for key>"', 
        each_line) for each_line in the_lines]

    with out_file.open("w") as _out:
        _out.writelines(mod_lines)    
    

#%% Main Function. 
if  __name__ == "__main__": 

    from parsers import copyenv_parser

    the_parser = copyenv_parser()
    the_args   = the_parser.parse_args()

    copy_env(the_args.in_file, the_args.out_file)
    
    print(f"Copia de archivo {the_args.in_file} se realizó con éxito en:\n" + 
          f"\t{the_args.out_file}")
    