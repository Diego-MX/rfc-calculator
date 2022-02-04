#!/usr/bin/env python3

import datetime as dt 
from functools import partial
from re import sub as str_sub

from typing import List, Optional, Union, Literal
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from dataclasses import field

from enum import Enum
#%% Herramientas auxiliares. 

from src.utilities.basic import compose_ls, str_iconv, arg0_to_end, str_multisub


#%% Variables auxiliares 

# Estas llaves se definen en el manual de cálculo del RFC. 
# Los espacios y tildes son placeholders para ajustar los índices que se solicitan.

# RFC
LLAVES_1 = " 123456789&ABCDEFGHI~JKLMNOPQR~~STUVWXYZÑ" 
LLAVES_2 = "123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
LLAVES_3 = "0123456789ABCDEFGHIJKLMN&OPQRSTUVWXYZ Ñ"  
LLAVES_4 = "0A987654321"  
# CURP
LLAVES_5 = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
LLAVES_6 = "0987654321"


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

NAZARENOS = ["MARIA", "JOSE"]

estados_str = ("Aguascalientes:AS, Baja California:BC, Baja California Sur:BS, " + 
    "Campeche:CC, Chiapas:CS, Chihuahua:CH, Ciudad de México:DF, Coahuila:CL, " + 
    "Colima:CM, Durango:DG, Guanajuato:GT, Guerrero:GR, Hidalgo:HG, Jalisco:JC, " + 
    "Edo. México:MC, Morelos:MS, Nayarit:NT, Nuevo León:NL, Oaxaca:OC, Puebla:PL, " + 
    "Querétaro:QO, Quintana Roo:QR, San Luis Potosí:SP, Sinaloa:SL, Sonora:SR, " + 
    "Tabasco:TC, Tamaulipas:TS, Tlaxcala:TL, Veracruz:VZ, Yucatán:YN, Zacatecas:ZS")
ESTADOS = dict(estado.split(":") for estado in estados_str.split(", "))


#%% 

regex_ignorar = dict( (rf"\b{palabra}\b", " ") for palabra in IGNORAR_NOMBRE)
dict_chars    = dict( (c_char, "") for c_char in IGNORAR_CHARS["fisica"])

str_normaliza = partial( arg0_to_end(str_iconv), "ÁÉÍÓÚ", "AEIOU")
str_chars     = partial( str_multisub, sub_dict=dict_chars, escape=True)
str_palabras  = partial( str_multisub, sub_dict=regex_ignorar, escape=False)
str_espacios  = compose_ls([partial( str_sub, " +", " "), str.strip])

compose_apply = lambda x, fn_ls: list(map(compose_ls(fn_ls), x))

#%%

class Gender(str, Enum): 
    HOMBRE = "H"
    MUJER  = "F"


class PhysicalPerson(BaseModel): 
    person_type:    Literal["physical"]
    names_list:     List[str]
    date_of_birth:  dt.date
    state_of_birth: Optional[str]
    gender:         Optional[Gender] 

    def prepare_names(self): 
        names_0   = compose_apply(self.names_list, [str_chars, str.upper, str_normaliza])
        names_str = str_espacios(" ".join(names_0))
        # No se puede juntar COMPOSE_APPLY porque STR_PALABRAS quita preposiciones que se usan. 
        names_1   = compose_apply(names_0, [str_palabras, str_espacios])
        
        firstnames_ls = names_1[2].split(" ")
        use_first = (len(firstnames_ls) == 1) | (firstnames_ls[0] not in NAZARENOS)
        
        one_firstname = firstnames_ls[0] if use_first else firstnames_ls[1]
        one_lastname  = "".join(names_1[:2]) if ("" in names_1[:2]) else None
        
        self.helpers = {
            "names"         : names_1, 
            "names_str"     : names_str, 
            "firstnames"    : firstnames_ls, 
            "use_first"     : use_first, 
            "one_firstname" : one_firstname, 
            "one_lastname"  : one_lastname}


    def get_rfc(self):
        rfc_0 = self.get_initials(mode="RFC")
        rfc_1 = rfc_0 + self.date_of_birth.strftime("%y%m%d")
        rfc_2 = rfc_1 + self.get_homoclave(  rfc_1, mode="RFC")
        rfc_3 = rfc_2 + self.get_verificator(rfc_2, mode="RFC") 
        return rfc_3

    def get_curp(self): 
        curp_0 = self.get_initials(mode="CURP")
        curp_1 = curp_0 + self.date_of_birth.strftime("%y%m%d")
        curp_2 = curp_1 + self.gender.value + ESTADOS[self.state] 
        curp_3 = curp_2 + self.second_consonants()
        curp_4 = curp_3 + self.get_homoclave(  curp_3, mode="CURP")
        curp_5 = curp_4 + self.get_verificator(curp_4, mode="CURP") 
        return curp_5
    

    def get_initials(self, mode): 
        
        if mode == "RFC": 
            p_lastname = self.helpers["names"][0]
            p_vocals   = list(filter(lambda letra: letra in "AEIOU", p_lastname[1:]))
                        
            if self.un_apellido:
                iniciales = self.un_apellido[:2] + self.nombre_base[:2]
            elif len(self.p_lastname) < 3 | len(p_vocals) < 1:
                iniciales = self.p_lastname[0] + self.m_lastname[0] + self.nombre_base[:2]
            else: 
                iniciales= (self.p_lastname[0] + p_vocals[0] + 
                            self.m_lastname[0] + self.nombre_base[0])
            
            if iniciales in INCONVENIENTES: 
                iniciales = iniciales[0:3] + "X"

        elif mode == "CURP": 
            pass
        
        return iniciales

    
    def get_homoclave(self, base, mode): 
        if mode == "RFC": 
            idx_list  = [LLAVES_1.index(c_char) for c_char in list(base)] 
            idx_seq   = ["0"] + [f"{c_pos:02}"  for c_pos  in idx_list]
            int_list  = [int(c_char) for c_char in "".join(idx_seq)]
            sum_terms = [10*int_list[i]*c_i + c_i**2 for i, c_i in enumerate(int_list[1:])]
            # Nótese que c_i = cadena[i + 1] para i = 0... len(cadena-2)
            sum_1000  = sum(sum_terms) % 1000
            
            (cociente, residuo) = (sum_1000 // 34, sum_1000 % 34)
            homoclave = (LLAVES_2[cociente] + LLAVES_2[residuo ])

        elif mode == "CURP": 
            pass

        return homoclave

    def get_verificator(self, base, mode): 
        parameters = {
            "RFC" : (LLAVES_3, LLAVES_4, 12, 11), 
            "CURP": (LLAVES_5, LLAVES_6, 17, 10)}
        if mode not in parameters: 
            raise f"MODE must be one of {str(parameters.keys())}"
        llaves_in, llaves_out, k_in, k_out = parameters[mode]
        if len(base) != k_in: 
            raise f"LEN of BASE must be {k_in}"

        seq_idx    = [llaves_in.index(c_char) for c_char in base]
        calc_sum   = sum(seq_idx[i]*(k_in+1 - i) for i in range(k_in))
        vrfy_digit = llaves_out[calc_sum % k_out]
        return vrfy_digit

    def second_consonants(self): 
        pass


            
class MoralPerson(BaseModel): 
    person_type:    Literal["moral"]
    names_list:     str
    date_of_issue:  dt.date


Person = Annotated[ Union[PhysicalPerson, MoralPerson], 
        Field(discriminator="person_type")]


class PersonaFisica:
    def __init__(self, nombres_ls):
        nombres_0 = compose_apply(nombres_ls, [str_chars, str.upper, str_normaliza])

        self.la_cadena = str_espacios(" ".join(nombres_0))
        self.la_lista  = compose_apply(nombres_0, [str_palabras, str_espacios])
        
        self.identificar_elementos()
        

    def identificar_elementos(self):
        la_lista     = self.la_lista

        apellidos    = la_lista[:2]
        los_nombres  = la_lista[ 2].split(" ")
        usar_primero = (len(los_nombres) == 1) | (los_nombres[0] not in NAZARENOS)
        
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

        elif modo == "CURP": 
            pass
            
        self.iniciales = iniciales

        return iniciales


def rfc_completo(tipo: str, nombres_ls: list, f_inicio: dt.datetime) -> str:  
    # TIPO: "fisica" o "moral"
    # NOMBRES_LS tiene: 
    #   - 3 elementos: apellido_p, apellido_m, nombres_juntos; en persona física.
    #   - 1 elemento con espacios en persona moral. 
    # F_INICIO: tiene formato de fecha. 
    
    nombres_obj = PersonaFisica(nombres_ls)

    rfc_0       = rfc_inicial(tipo, nombres_obj)
    rfc_1       = (rfc_0 + f_inicio.strftime("%y%m%d"))
    
    homoclave_1 = homoclave(nombres_obj.la_cadena)
    rfc_2       = rfc_1 + homoclave_1
    
    verificador_2 = verificador(rfc_2)
    rfc_final     = rfc_2 + verificador_2 

    return rfc_final


#%% Componentes secundarios
def rfc_inicial(tipo: str, nombres_obj: PersonaFisica) -> str:
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
    # En realidad la homoclave consta de dos caracteres, el tercero es el digito verificador. 
    char_posiciones = [LLAVES_1.index(c_char) for c_char in list(nombres)  ] 
    posiciones_str  = ["0"] + [f"{c_pos:02}"  for c_pos  in char_posiciones]

    # Nótese que c_i = cadena[i + 1] para i = 0... len(cadena-2)
    cadena = [int(c_char) for c_char in "".join(posiciones_str)]
    terms  = [10*cadena[i]*c_i + c_i**2 for i, c_i in enumerate(cadena[1:])]
    calc_trippy = sum(terms) % 1000
    
    (cociente, residuo) = (calc_trippy // 34, calc_trippy % 34)
    homo_1 = LLAVES_2[cociente]
    homo_2 = LLAVES_2[residuo ]
    return (homo_1 + homo_2) 


def verificador(pre_id: str, tipo=None) -> str:  
    # El verificador es el tercero de la homoclave. 
    
    parametros = {
        "RFC" : (LLAVES_3, LLAVES_4, 12, 11), 
        "CURP": (LLAVES_5, LLAVES_6, 17, 10)
    }
    if tipo not in parametros: 
        tipo = "RFC"

    llaves_in, llaves_out, k_in, k_out = parametros[tipo]
    
    seq_idx    = [llaves_in.index(c_char) for c_char in pre_id]
    calc_suma  = sum(seq_idx[i]*(k_in+1 - i) for i in range(k_in))
    digito_ver = llaves_out[calc_suma % k_out]
        
    return digito_ver





if __name__ == "__main__":
    ## Imports preparation.
    
    import src.utilities.parsers as parsers
    
    ## Setup the parsers.
    the_parser = parsers.rfc_parser()
    the_args   = the_parser.parse_args()

    el_rfc = rfc_completo("fisica",  
        nombres_ls = [the_args.apellido_p, the_args.apellido_m, the_args.nombres], 
        f_inicio   = dt.datetime.strptime(the_args.f_inicio, "%Y-%m-%d"))

    print(f"\tEl RFC es: {el_rfc}")
    
