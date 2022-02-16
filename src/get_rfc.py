#!/usr/bin/env python3

import datetime as dt 
from functools import partial
from operator import itemgetter
from re import sub as str_sub

from typing import List, Optional, Union, Literal
from typing_extensions import Annotated
from pydantic import BaseModel, Field
# from dataclasses import field

from enum import Enum
#%% Herramientas auxiliares. 

from src.utilities.basic import compose_ls, arg0_to_end, str_iconv, str_multisub

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


INCONVENIENTES = {
    "RFC" : ( "BUEI, BUEY, CACA, CACO, CAGA, CAGO, CAKA, COGE, COJA, " + 
        "COJI, COJO, CULO, FETO, GUEY, JOTO, KACA, KACO, KAGA, KAGO, " + 
        "KOGE, KOJO, KAKA, KULO, MAME, MAMO, MEAR, MEON, MION, MOCO, " + 
        "MULA, PEDA, PEDO, PENE, PUTA, PUTO, QULO, RATA, RUIN").split(", "), 
    "CURP": ( "BACA, BAKA, BUEI, BUEY, CACA, CACO, CAGA, CAGO, CAKA, " +  
        "CAKO, COGE, COGI, COJA, COJE, COJI, COJO, COLA, CULO, FALO, " +  
        "FETO, GETA, GUEI, GUEY, JETA, JOTO, KACA, KACO, KAGA, KAGO, " +  
        "KAKA, KAKO, KOGE, KOGI, KOJA, KOJE, KOJI, KOJO, KOLA, KULO, " +  
        "LILO, LOCA, LOCO, LOKA, LOKO, MAME, MAMO, MEAR, MEAS, MEON, " +  
        "MIAR, MION, MOCO, MOKO, MULA, MULO, NACA, NACO, PEDA, PEDO, " +  
        "PENE, PIPI, PITO, POPO, PUTA, PUTO, QULO, RATA, ROBA, ROBE, " +  
        "ROBO, RUIN, SENO, TETA, VACA, VAGA, VAGO, VAKA, VUEI, VUEY, " +  
        "WUEI, WUEY").split(", ") }

IGNORAR = {
    "RFC": ("EL, LA, DE, S DE RL, SA DE CV, DE, LOS, LAS, " + 
        "Y, MC, DEL, SA, VON, COMPAÑIA, CIA, SOCIEDAD, SOC, " + 
        "COOPERATIVA, COOP, S EN C POR A, A EN P, MAC, S EN NC, S EN C, " +
        "VAN, PARA, EN, MI, POR, CON, AL, SUS, E, SC, SCL, " + 
        "SCS, SNC, THE, OF, AND, COMPANY, CO, MC, MI, A, SRL CV, " + 
        "SA DE CV MI, SA MI, COMPA.IA, SRL CV MI, SRL MI").split(", "), 
    "CURP" : ("DA, DAS, DE, DEL, DER, DI, DIE, DD, EL, LA, " +
        "LOS, LAS, LE, LES, MAC, MC, VAN, VON, Y").split(", ") }

IGNORAR_CHARS   = {
    "RFC"   : "´'.", 
    "CURP"  : "/-.", 
    "moral" : "@'´%#!.$\"-/+()"}

NAZARENOS = ["MARIA", "JOSE", "MA", "MAXX"]  # Equivale a 'MA.' pero se modifica por las reglas. 


estados_str = ("Aguascalientes:AS, Baja California:BC, Baja California Sur:BS, " + 
    "Campeche:CC, Chiapas:CS, Chihuahua:CH, Ciudad de México:DF, Coahuila:CL, " + 
    "Colima:CM, Durango:DG, Guanajuato:GT, Guerrero:GR, Hidalgo:HG, Jalisco:JC, " + 
    "Edo. México:MC, Morelos:MS, Nayarit:NT, Nuevo León:NL, Oaxaca:OC, Puebla:PL, " + 
    "Querétaro:QO, Quintana Roo:QR, San Luis Potosí:SP, Sinaloa:SL, Sonora:SR, " + 
    "Tabasco:TC, Tamaulipas:TS, Tlaxcala:TL, Veracruz:VZ, Yucatán:YN, Zacatecas:ZS")

ESTADOS = dict(estado.split(":") for estado in estados_str.split(", "))


#%% 

compose_apply = lambda x, fn_ls: list(map(compose_ls(fn_ls), x))

str_normalize = partial( arg0_to_end(str_iconv), "ÁÉÍÓÚÜ", "AEIOUU")
str_spacing   = compose_ls([partial( str_sub, " +", " "), str.strip])


#%%

class Gender(str, Enum): 
    HOMBRE = "H"
    MUJER  = "M"


class PhysicalPerson(BaseModel): 
    person_type:    Literal["physical"]
    names_list:     List[str]
    date_of_birth:  dt.date
    state_of_birth: Optional[str]
    gender:         Optional[Gender] 

    def get_rfc(self):
        extras = self.get_helpers(mode="RFC")
        rfc_0 = self.get_initials(extras, mode="RFC")
        rfc_1 = rfc_0 + self.date_of_birth.strftime("%y%m%d")
        rfc_2 = rfc_1 + self.get_homoclave(extras, mode="RFC")
        rfc_3 = rfc_2 + self.get_verificator(rfc_2, mode="RFC") 
        return rfc_3

    def get_curp(self): 
        extras = self.get_helpers(mode="CURP")
        curp_0 = self.get_initials(extras, mode="CURP")
        curp_1 = self.date_of_birth.strftime("%y%m%d")
        curp_2 = self.gender.value + ESTADOS[self.state_of_birth] 
        curp_3 = self.get_second_consonants(extras)
        curp_4 = curp_0 + curp_1 + curp_2 + curp_3
        curp_5 = curp_4 + self.get_homoclave(extras, mode="CURP")
        curp_6 = curp_5 + self.get_verificator(curp_5, mode="CURP") 
        return curp_6


    def get_helpers(self, mode):
        sub_chars  = {"RFC": "", "CURP": "XX"} 
        # La sustitución por X a secas crea una confusión entre 'MA.' y 'MAX'. 
        dict_chars = dict( (c_char, sub_chars[mode]) for c_char in IGNORAR_CHARS[mode])
        str_chars  = partial( str_multisub, sub_dict=dict_chars, escape=True)
        
        reg_stopwds = dict( (rf"\b{palabra}\b", " ") for palabra in IGNORAR[mode])
        str_stopwds = partial( str_multisub, sub_dict=reg_stopwds, escape=False)
        
        names_0   = compose_apply(self.names_list, [str.upper, str_chars, str_normalize])
        names_1   = [ str_sub(r"^(MA?C|VAN)", r"\1 ", e_name) for e_name in names_0 ]
        names_str = str_spacing(" ".join(names_1))
        names_2   = compose_apply(names_1, [str_stopwds, str_spacing])
        # Se quedan separados los COMPOSE_APPLY ya que NAMES_STR se ocupa solito. 

            
        firstnames_ls = names_2[2].split(" ")
        use_first     = (len(firstnames_ls) == 1) | (firstnames_ls[0] not in NAZARENOS)
        one_firstname = firstnames_ls[0] if use_first else firstnames_ls[1]

        lastnames = names_2[:2]        
        if mode == "CURP":  # Apellidos compuestos consideran sólo la primer palabra. 
            lastnames   = [e_name.split(" ")[0] for e_name in lastnames]
            names_2[:2] = lastnames

        use_one      = "" in lastnames
        one_lastname = "".join(lastnames) if (use_one) else None
        two_lastname = one_lastname if one_lastname else names_2[0]

        helpers = { "names" : names_2, 
            "names_str"     : names_str, 
            "one_firstname" : one_firstname, 
            "one_lastname"  : (one_lastname, two_lastname) }
            # [1] : is None if there are two lastnames, used in RFC.
            # [2] : is Parental if it exists, or Maternal otherwise. 
        
        return helpers


    def get_initials(self, helpers, mode): 
        p_lastname  = helpers["names"][0]
        m_lastname  = helpers["names"][1]
        lastname_0  = helpers["one_lastname"][0]
        lastname_1  = helpers["one_lastname"][1]
        firstname_0 = helpers["one_firstname"]
        
        params = { "RFC" : ("AEIOU" , 3), 
                   "CURP": ("AEIOUX", 1) }
        (vowels, pos) = params[mode]
        
        if mode == "RFC":
            p_vowels = list(filter(lambda letter: 
                    letter in vowels, p_lastname[1:]))

            if  lastname_0:
                initials = lastname_0[:2] + firstname_0[:2]
            elif len(p_lastname) < 3 | len(p_vowels) < 1:
                initials = p_lastname[0] + m_lastname[0] + firstname_0[:2]
            else: 
                initials = (p_lastname[0] + p_vowels[0] 
                        + m_lastname[0] + firstname_0[0])
            
        elif mode == "CURP": 
            vowels_1  = list(filter(lambda letter: 
                    letter in vowels, lastname_1[1:]))
            
            get_first = lambda x_str: x_str[0] if len(x_str) > 0 else "X"

            initials_1 = "".join(map(get_first, 
                    [lastname_1, vowels_1, m_lastname, firstname_0]))
            initials = str_sub("Ñ", "X", initials_1)

        if initials in INCONVENIENTES[mode]: 
            initials = initials[:pos] + "X" + initials[pos+1:]    
        
        return initials


    def get_second_consonants(self, helpers): 
        
        def inner_consonant(x_str):
            consts   = "BCDFGHJKLMNÑPQRSTVWXYZ"
            x_consts = list(filter(lambda letter: letter in consts, x_str[1:]))
            return x_consts[0] if x_consts else "X"
        
        lastname_1  = helpers["one_lastname"][1]
        m_lastname  = helpers["names"][1]
        firstname_0 = helpers["one_firstname"]

        the_consts_1 = "".join( map(inner_consonant, 
                [lastname_1, m_lastname, firstname_0]) )

        the_consts = str_sub("Ñ", "X", the_consts_1)
        
        return the_consts

    
    def get_homoclave(self, helpers, mode): 
        if mode == "RFC": 
            names_str = helpers["names_str"]
            idx_list  = [LLAVES_1.index(c_char) for c_char in list(names_str)] 
            idx_seq   = ["0"] + [f"{c_pos:02}"  for c_pos  in idx_list]
            int_list  = [int(c_char) for c_char in "".join(idx_seq)]
            sum_terms = [10*int_list[i]*c_i + c_i**2 
                    for i, c_i in enumerate(int_list[1:])]
            # The actual definition is the sum of all two digit numbers times 
            #   their unit digits, that is: 
            #   SUM( [Ci_Ci1]*Ci1 ) = SUM( (10C_i+C_i1)*C_i1 ),
            #   where i1 = (i+1) for i = 0,...,len(C). 
            # Alongside notice that we have shifted indices in SUM_TERMS,
            #   so that C_i = INT_LIST[i+1] in the expression above. 

            sum_1000  = sum(sum_terms) % 1000
            (cociente, residuo) = (sum_1000 // 34, sum_1000 % 34)
            homoclave = (LLAVES_2[cociente] + LLAVES_2[residuo ])

        elif mode == "CURP": 
            before_2000 = self.date_of_birth < dt.date(2000, 1, 1)
            homoclave   = '0' if before_2000 else 'A'

        return homoclave


    def get_verificator(self, base, mode): 
        parameters = {
            "RFC" : (LLAVES_3, LLAVES_4, 12, 11), 
            "CURP": (LLAVES_5, LLAVES_6, 17, 10)}
        llaves_in, llaves_out, k_in, k_out = parameters[mode]

        if len(base) != k_in: 
            raise f"LEN of BASE must be {k_in}"

        seq_idx    = [llaves_in.index(c_char) for c_char in base]
        calc_sum   = sum(seq_idx[i]*(k_in+1 - i) for i in range(k_in))
        vrfy_digit = llaves_out[calc_sum % k_out]
        return vrfy_digit


            
class MoralPerson(BaseModel): 
    person_type:    Literal["moral"]
    names_list:     str
    date_of_issue:  dt.date


Person = Annotated[ Union[PhysicalPerson, MoralPerson], 
        Field(discriminator="person_type")]


class PersonaFisica:
    def __init__(self, nombres_ls):
        dict_rm_chars = dict( (c_char, "") for c_char in IGNORAR_CHARS["RFC"])
        str_rm_chars  = partial( str_multisub, sub_dict=dict_rm_chars, escape=True)

        reg_stopwds = dict( (rf"\b{palabra}\b", " ") for palabra in IGNORAR["RFC"])
        str_stopwds = partial( str_multisub, sub_dict=reg_stopwds, escape=False)

        nombres_0 = compose_apply(nombres_ls, [str_rm_chars, str.upper, str_normalize])

        self.la_cadena = str_spacing(" ".join(nombres_0))
        self.la_lista  = compose_apply(nombres_0, [str_stopwds, str_spacing])
        
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


    person_dict = {
        "person_type": "physical",
        "names_list" : ["Villamil", "Pesqueira", "Diego"], 
        "date_of_birth" : dt.date(1983, 12, 27), 
        "state_of_birth": "Ciudad de México", 
        "gender" : "H"
    }

    person_obj = PhysicalPerson(**person_dict)
    el_rfc     = person_obj.get_rfc()
    el_curp    = person_obj.get_curp()

    print(f"\nRFC\t: {el_rfc}\nCURP\t: {el_curp}")