import argparse

def rfc_parser():
    parser  = argparse.ArgumentParser(prog="obtener_rfc",
        description = "Obtener el RFC de una persona física o moral.", 
        formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument("apellido_p", type=str, 
        help = "apellido paterno del individuo")
    parser.add_argument("apellido_m", type=str, 
        help = "apellido materno de la individua")
    parser.add_argument("nombres",    type=str, 
        help = "nombre(s) del individuo")
    
    parser.add_argument("f_inicio", type=str,
        help = "fecha de inicio o nacimiento en formato YYYY-MM-DD")
    return parser


def copyenv_parser():
    parser = argparse.ArgumentParser(
        prog = "copy_env", 
        description = "Copies DOTENV file", 
        formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument("in_file",  type=str, 
            help="Archivo de lectura de variables de ambiente usadas.")
    parser.add_argument("--out_file", type=str, required=False,
            help="Archivo de escritura de variables requeridas.")
    return parser

