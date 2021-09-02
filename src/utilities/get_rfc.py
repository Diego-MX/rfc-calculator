#!/usr/bin/env python3

from datetime import datetime as dt
from functools import partial
from unicodedata import normalize 
from re import sub as str_sub

#%% Herramientas auxiliares. 

from .basic_utils import compose_ls, str_iconv, arg0_to_end, str_multisub


#%% Variables auxiliares 

# Estas llaves se definen en el manual de cálculo del RFC. 
# Los espacios y tildes son placeholders para ajustar los índices que se solicitan.

LLAVES_1 = " 123456789&ABCDEFGHI~JKLMNOPQR~~STUVWXYZÑ" 
LLAVES_2 = "123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
LLAVES_3 = "0123456789ABCDEFGHIJKLMN&OPQRSTUVWXYZ Ñ"  
LLAVES_4 = "0A987654321"  
    
INCONVENIENTES  = ( "BUEI, BUEY, CACA, CACO, CAGA, CAGO, CAKA, COGE, " +  
        "COJA, COJI, COJO, CULO, FETO, GUEY, JOTO, KACA, KACO, KAGA, " + 
        "KAGO, KOGE, KOJO, KAKA, KULO, MAME, MAMO, MEAR, MEON, MION, " + 
        "MOCO, MULA, PEDA, PEDO, PENE, PUTA, PUTO, QULO, RATA, RUIN" ).split(", ")

IGNORAR_NOMBRE  = ("EL, LA, DE, S DE RL, SA DE CV, DE, LOS, LAS, " + 
        "Y, MC, DEL, SA, VON, COMPAÑIA, CIA, SOCIEDAD, SOC, " + 
        "COOPERATIVA, COOP, S EN C POR A, A EN P, MAC, S EN NC, S EN C, " +
        "VAN, PARA, EN, MI, POR, CON, AL, SUS, E, SC, SCL, " + 
        "SCS, SNC, THE, OF, AND, COMPANY, CO, MC, MI, A, SRL CV, " + 
        "SA DE CV MI, SA MI, COMPA&IA, SRL CV MI, SRL MI").split(", ")

IGNORAR_CHARS   = {
        "moral"     : "@'´%#!.$\"-/+()", 
        "fisica"    : "´'." }

NOMBRES_NAZARENOS = ["MARIA", "JOSE"]


#%% Función principal... MAIN  

# Tratar de eliminar las lambdas. 

dict_palabras = dict( (f"\b{palabra}\b", " ") for palabra in IGNORAR_NOMBRE)
dict_chars    = dict( (c_char, "") for c_char in IGNORAR_CHARS["fisica"])

str_chars     = partial( str_multisub, sub_dict=dict_chars)
str_normaliza = partial( arg0_to_end(str_iconv), "ÁÉÍÓÚ", "AEIOU")
str_palabras  = partial( str_multisub, sub_dict=dict_palabras)
str_espacios  = compose_ls([partial( str_sub, " +", " "), str.strip])


class Nombres:

    def __init__(self, nombres_ls):

        nombres_0 = list( map( compose_ls(
            [str_chars, str.upper, str_normaliza]), 
            nombres_ls))
        self.la_cadena  = str_espacios(" ".join(nombres_0))
        self.la_lista   = list(map(compose_ls(
            [str_palabras, str_espacios]),          
            nombres_0 ))
        
        self.identificar_elementos()
        

    def identificar_elementos(self):
        la_lista     = self.la_lista
        apellidos    = la_lista[:2]
        los_nombres  = la_lista[ 2].split(" ")
        usar_primero = (len(los_nombres) == 1) | (los_nombres[0] not in NOMBRES_NAZARENOS)
        
        self.apellido_p  = la_lista[0]
        self.apellido_m  = la_lista[1]
        self.nombres     = la_lista[2]
        
        self.k_nombres   = len(los_nombres)
        self.nombre_base = los_nombres[0] if usar_primero else los_nombres[1]
        self.un_apellido = "".join(apellidos) if ("" in apellidos) else None


    def obtener_iniciales(self, modo="estandar"):
        if   modo == "estandar":
            iniciales = list(map(lambda x: x[0], self.la_lista))

        elif modo == "RFC":
            vocales_p = list(filter(lambda letra: letra in "AEIOU", self.apellido_p[1:]))
                        
            if self.un_apellido:
                iniciales = self.un_apellido[:2] + self.nombre_base[:2]

            elif len(self.apellido_p) < 3 | len(vocales_p) < 1:
                iniciales = self.apellido_p[0] + self.apellido_m[0] + self.nombre_base[:2]
            
            else: 
                iniciales= (self.apellido_p[0] + vocales_p[0] + 
                            self.apellido_m[0] + self.nombre_base[0])
            
            if iniciales in INCONVENIENTES: 
                iniciales = iniciales[0:3] + "X"
            
        self.iniciales = iniciales

        return iniciales



def rfc_completo(tipo: str, nombres_ls: list, f_inicio: dt) -> str:  
    # TIPO: "fisica" o "moral"
    # NOMBRES_LS tiene: 
    #   - 3 elementos: apellido_p, apellido_m, nombres_juntos; en persona física.
    #   - 1 elemento con espacios en persona moral. 
    # F_INICIO: tiene formato de fecha. 
    
    nombres_obj = Nombres(nombres_ls)

    rfc_0       = rfc_inicial(tipo, nombres_obj)
    rfc_1       = (rfc_0 + f_inicio.strftime("%y%m%d"))
    
    homoclave_1 = homoclave(nombres_obj.la_cadena)
    rfc_2       = rfc_1 + homoclave_1
    
    verificador_2   = verificador(rfc_2)
    rfc_final       = rfc_2 + verificador_2 

    return rfc_final


#%% Componentes secundarios
def rfc_inicial(tipo: str, nombres_obj: Nombres) -> str:
    # INPUTS como arriba; 
    # -> INICIALES   : cuatro letras
    # -> NOMBRES_STR : nombres concatenados

    nombres_obj
    if tipo == "fisica":  
        iniciales = nombres_obj.obtener_iniciales(modo="RFC")

    elif tipo == "moral":
        # Quitar caracteres y palabras no usadas.
        pass
    else:
        print("ERROR")
    
    return iniciales


def homoclave(nombres: str) -> str:
    # En realidad la homoclave consta de dos caracteres. 
    char_posiciones = [LLAVES_1.index(c_char) for c_char in list(nombres)] 
    posiciones_str  = ["0"] + [f"{c_pos:02}" for c_pos in char_posiciones]

    cadena      = [int(c_char) for c_char in "".join(posiciones_str)] 
    calc_trippy = sum(10*cadena[i]*cadena[i+1] + cadena[i+1]**2
                       for i in range(len(cadena) - 1)) % 1000
    
    cociente, residuo = calc_trippy // 34, calc_trippy % 34
    
    homo_1      = LLAVES_2[cociente]
    homo_2      = LLAVES_2[residuo ]

    return (homo_1 + homo_2)


def verificador(rfc_12: str) -> str:  
    # El verificador es el tercero de la homoclave. 
    seq_idx   = [LLAVES_3.index(c_char) for c_char in rfc_12]
    calc_suma = sum(seq_idx[i]*(13 - i) for i in range(12))

    el_verificador = LLAVES_4[calc_suma % 11]
    return (el_verificador)



if __name__ == "__main__":
    ## Imports preparation.
    
    import parsers 
    
    ## Setup the parsers.
    the_parser = parsers.rfc_parser()
    the_args   = the_parser.parse_args()

    el_rfc = rfc_completo("fisica",  
        nombres_ls = [the_args.apellido_p, the_args.apellido_m, the_args.nombres], 
        f_inicio   = dt.strptime(the_args.f_inicio, "%Y-%m-%d"))

    print(f"\tEl RFC es: {el_rfc}")
    
        
        
        