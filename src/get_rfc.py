#!/usr/bin/env python3
from datetime import datetime as dt, date
from enum import Enum
from functools import partial
from operator import methodcaller as ϱ
import re 
from typing import Optional

from pydantic import BaseModel, Field   # pylint: disable=no-name-in-module
from toolz import compose, compose_left, pipe
from toolz.curried import map as map_z
from src.utilities.basic import partial2, str_iconv, str_multisub


#%% Aux variables

# These keys are defined in the corresponding documentation for RFC and CURP.
# Spaces and tildes are used as place-holders on purpose. 

# RFC
CHARS_1 = ' 123456789&ABCDEFGHI~JKLMNOPQR~~STUVWXYZÑ' 
CHARS_2 = '123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'
CHARS_3 = '0123456789ABCDEFGHIJKLMN&OPQRSTUVWXYZ Ñ'  
CHARS_4 = '0A987654321'  

# CURP
CHARS_5 = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
CHARS_6 = '0987654321'


INCONVENIENTS = { 
    'RFC':  ("BUEI,BUEY,CACA,CACO,CAGA,CAGO,CAKA,COGE,COJA,COJI,COJO,CULO,FETO,"
        "GUEY,JOTO,KACA,KACO,KAGA,KAGO,KOGE,KOJO,KAKA,KULO,MAME,MAMO,MEAR,MEON,"
        "MION,MOCO,MULA,PEDA,PEDO,PENE,PUTA,PUTO,QULO,RATA,RUIN"
        ).split(','),  # 38 words
    'CURP': ("BACA,BAKA,BUEI,BUEY,CACA,CACO,CAGA,CAGO,CAKA,CAKO,COGE,COGI,COJA,"
        "COJE,COJI,COJO,COLA,CULO,FALO,FETO,GETA,GUEI,GUEY,JETA,JOTO,KACA,KACO,"
        "KAGA,KAGO,KAKA,KAKO,KOGE,KOGI,KOJA,KOJE,KOJI,KOJO,KOLA,KULO,LILO,LOCA,"
        "LOCO,LOKA,LOKO,MAME,MAMO,MEAR,MEAS,MEON,MIAR,MION,MOCO,MOKO,MULA,MULO,"
        "NACA,NACO,PEDA,PEDO,PENE,PIPI,PITO,POPO,PUTA,PUTO,QULO,RATA,ROBA,ROBE,"
        "ROBO,RUIN,SENO,TETA,VACA,VAGA,VAGO,VAKA,VUEI,VUEY,WUEI,WUEY"
        ).split(',') }  # 81 words

IGNORE_WORDS = {
    'RFC': ("EL,LA,DE,S DE RL,SA DE CV,DE,LOS,LAS,Y,MC,DEL,SA,COMPAÑIA,CIA,"
        "SOCIEDAD,SOC,COOPERATIVA,COOP,S EN C POR A,A EN P,MAC,S EN NC,S EN C,"
        "VAN,PARA,EN,MI,POR,CON,AL,SUS,E,SC,SCL,SCS,SNC,THE,OF,AND,COMPANY,CO,"
        "MC,MI,A,SRL CV,SA DE CV MI,SA MI,COMPA.IA,SRL CV MI,SRL MI"
        ).split(','),
    'CURP': ("DA,DAS,DE,DEL,DER,DI,DIE,DD,EL,LA,LOS,LAS,LE,LES,MAC,MC,VAN,VON,Y"
        ).split(',')}

IGNORE_CHARS = {
    'RFC'   : '´\'.', 
    'CURP'  : '/-.', 
    'moral' : '@"´%#!.$\'-/+()'}

NAZARENES = ['MARIA', 'JOSE', 'MA', 'MAXX']  # Last entry MAXX is used for MA, 
    # when modified with some rules. 

# These codes assume the Mexican State name. 
STATES_STR = ("Aguascalientes:AS,Baja California:BC,Baja California Sur:BS," 
    "Campeche:CC,Chiapas:CS,Chihuahua:CH,Ciudad de México:DF,Coahuila:CL,"
    "Colima:CM,Durango:DG,Guanajuato:GT,Guerrero:GR,Hidalgo:HG,Jalisco:JC,"
    "Edo. México:MC,Morelos:MS,Nayarit:NT,Nuevo León:NL,Oaxaca:OC,Puebla:PL," 
    "Querétaro:QO,Quintana Roo:QR,San Luis Potosí:SP,Sinaloa:SL,Sonora:SR," 
    "Tabasco:TC,Tamaulipas:TS,Tlaxcala:TL,Veracruz:VZ,Yucatán:YN,Zacatecas:ZS")

State = pipe(STATES_STR, 
    ϱ('split', ','), 
    map_z(ϱ('split', ':')), 
    map_z(reversed), 
    partial(Enum, 'State'))


# And now some auxiliary functions. 

str_normalize = partial2(str_iconv, ..., 'ÁÉÍÓÚÜ', 'AEIOUU')
str_spacing = compose(str.strip, partial2(re.sub, ' +', ' ', ...))

has_match = lambda a_str, a_reg: re.match(a_reg, a_str) is not None


def valid_datestring(dt_str:str, date_format='%y%m%d') -> bool: 
    try: 
        _date = dt.strptime(dt_str, date_format)
        is_it = True
    except ValueError:
        is_it = False
    return is_it 



#%% The Real Models.  

class Gender(str, Enum): 
    HOMBRE = 'H'
    MUJER = 'M'


class PersonPhysical(BaseModel): 
    # person_type      : Literal['Physical']
    first_name         : str = Field(alias='firstName')
    last_name          : Optional[str] = Field(alias='lastName')
    maternal_last_name : Optional[str] = Field(default = '', alias='maternalLastName')
    date_of_birth      : Optional[date] = Field(alias='dateOfBirth') 
    state_of_birth     : Optional[State] = Field(default = None, alias='stateOfBirth')
    gender             : Optional[Gender] = Field(default = None)

    def get_rfc(self) -> str:
        extras = self.get_helpers(mode='RFC')
        rfc_0 = self.get_initials(extras, mode='RFC')
        rfc_1 = rfc_0 + self.date_of_birth.strftime('%y%m%d')
        rfc_2 = rfc_1 + self.get_homoclave(extras, mode='RFC')
        rfc_3 = rfc_2 + self.get_verificator(rfc_2, mode='RFC') 
        return rfc_3

    def get_curp(self) -> str: 
        extras = self.get_helpers(mode='CURP')
        curp_0 = self.get_initials(extras, mode='CURP')
        curp_1 = self.date_of_birth.strftime('%y%m%d')
        curp_2 = self.gender.value + self.state_of_birth.name
        curp_3 = self.get_second_consonants(extras)
        curp_4 = curp_0 + curp_1 + curp_2 + curp_3
        curp_5 = curp_4 + self.get_homoclave(extras, mode='CURP')
        curp_6 = curp_5 + self.get_verificator(curp_5, mode='CURP') 
        return curp_6


    def get_helpers(self, mode):
        sub_chars = {'RFC': '', 'CURP': 'XX'} 
        
        str_chars = partial2(str_multisub, escape=True,
            sub_dict=dict.fromkeys(IGNORE_CHARS[mode], sub_chars[mode]))
        
        ignore_regs = list(map(r'\b{}\b'.format, IGNORE_WORDS[mode]) )
        str_stopwds = partial2(str_multisub, escape=True, 
            sub_dict=dict.fromkeys(ignore_regs, ' '))
        
        names_list = [self.last_name, self.maternal_last_name, self.first_name]
        pre_names = pipe(names_list, 
            map_z(compose(str_normalize, str_chars, str.upper)),
            map_z(partial2(re.sub, r'^(MA?C|VAN)', r'\1', ...)), list)

        names_str = str_spacing(' '.join(pre_names))
        names_2 = pipe(pre_names, map_z(str_stopwds), map_z(str_spacing), list)

        firstnames_ls = names_2[2].split(' ')
        use_first = (len(firstnames_ls) == 1) | (firstnames_ls[0] not in NAZARENES)
        one_firstname = firstnames_ls[0] if use_first else firstnames_ls[1]

        lastnames = names_2[:2]        
        if mode == 'CURP': 
            lastnames = [each_name.split(' ')[0] for each_name in lastnames]
            names_2[:2] = lastnames

        use_one      = '' in lastnames
        one_lastname = ''.join(lastnames) if (use_one) else None
        two_lastname = one_lastname if one_lastname else names_2[0]

        helpers = { 'names' : names_2, 
            'names_str'     : names_str, 
            'one_firstname' : one_firstname, 
            'one_lastname'  : (one_lastname, two_lastname), 
            'date_of_birth' : self.date_of_birth }
            # [1] : is None if there are two lastnames, used in RFC.
            # [2] : is Parental if it exists, or Maternal otherwise.         
        return helpers

    
    @classmethod
    def get_initials(cls, helpers, mode): 
        p_lastname  = helpers['names'][0]
        m_lastname  = helpers['names'][1]
        lastname_0  = helpers['one_lastname'][0]
        lastname_1  = helpers['one_lastname'][1]
        firstname_0 = helpers['one_firstname']
        
        params = { 'RFC' : ('AEIOU' , 3), 
                   'CURP': ('AEIOUX', 1) }
                   
        (vowels, pos) = params[mode]
        
        if mode == 'RFC':
            p_vowels = list(filter(lambda letter: 
                    letter in vowels, p_lastname[1:]))

            if  lastname_0:
                initials = lastname_0[:2] + firstname_0[:2]
            elif len(p_lastname) < 3 | len(p_vowels) < 1:
                initials = p_lastname[0] + m_lastname[0] + firstname_0[:2]
            else: 
                initials = (p_lastname[0] + p_vowels[0] 
                        + m_lastname[0] + firstname_0[0])
            
        elif mode == 'CURP': 
            vowels_1 = list(filter(lambda letter: 
                    letter in vowels, lastname_1[1:]))
            
            get_first = lambda x_str: x_str[0] if len(x_str) > 0 else 'X'

            initials_1 = ''.join(map(get_first, 
                    [lastname_1, vowels_1, m_lastname, firstname_0]))
            initials = re.sub('Ñ', 'X', initials_1)

        if initials in INCONVENIENTS[mode]: 
            initials = initials[:pos] + 'X' + initials[pos+1:]    
        
        return initials


    @classmethod
    def get_second_consonants(cls, helpers): 
        
        def inner_consonant(x_str):
            consts = 'BCDFGHJKLMNÑPQRSTVWXYZ'
            x_consts = list(filter(lambda letter: letter in consts, x_str[1:]))
            return x_consts[0] if x_consts else 'X'
        
        lastname_1 = helpers['one_lastname'][1]
        m_lastname = helpers['names'][1]
        firstname_0 = helpers['one_firstname']

        the_consts_1 = ''.join(map(inner_consonant, 
                [lastname_1, m_lastname, firstname_0]) )
        return re.sub('Ñ', 'X', the_consts_1)
        

    @classmethod
    def get_homoclave(cls, helpers, mode): 
        if mode == 'RFC': 
            names_str = helpers['names_str']
            idx_list  = [CHARS_1.index(c_char) for c_char in list(names_str)] 
            idx_seq   = ['0'] + [f'{c_pos:02}'  for c_pos  in idx_list]
            int_list  = [int(c_char) for c_char in ''.join(idx_seq)]
            sum_terms = [10*int_list[i]*c_i + c_i**2 
                    for i, c_i in enumerate(int_list[1:])]
            # The actual definition is the sum of all two digit numbers times 
            #   their unit digits, that is: 
            #   SUM([Ci_Ci1]*Ci1 ) = SUM((10C_i+C_i1)*C_i1 ),
            #   where i1 = (i+1) for i = 0,...,len(C). 
            # Alongside notice that we have shifted indices in SUM_TERMS,
            #   so that C_i = INT_LIST[i+1] in the expression above. 
            sum_1000 = sum(sum_terms) % 1000
            (quotient, residue) = (sum_1000 // 34, sum_1000 % 34)
            a_homoclave = (CHARS_2[quotient] + CHARS_2[residue])

        elif mode == 'CURP': 
            before_2000 = helpers['date_of_birth'] < date(2000, 1, 1)
            a_homoclave = '0' if before_2000 else 'A'

        return a_homoclave


    @classmethod
    def get_verificator(cls, base_str, mode): 
        parameters = {
            'RFC' : (CHARS_3, CHARS_4, 12, 11), 
            'CURP': (CHARS_5, CHARS_6, 17, 10)}
        llaves_in, llaves_out, k_in, k_out = parameters[mode]

        if len(base_str) != k_in: 
            raise f'LEN of BASE must be {k_in}'

        seq_idx = [llaves_in.index(c_char) for c_char in base_str]
        calc_sum = sum(seq_idx[i]*(k_in+1 - i) for i in range(k_in))
        vrfy_digit = llaves_out[calc_sum % k_out]
        return vrfy_digit


    @classmethod
    def validate_rfc(cls, rfc_1: str, rfc_0: str): 
        rfc_1 = rfc_1.upper()  # USER
        rfc_0 = rfc_0.upper()  # CALCULATED

        k_inits = 4 if has_match(rfc_1[1], r"[AEIOU]") else 3
        
        okays = [False]*6

        # Structure format.
        okay_01 = has_match(rfc_1, r"^[A-Z]{3,4}[0-9]{6}[A-Z0-9]{3}$")
        # Initals are okay. 
        okay_02 = has_match(rfc_1[1], r"[AEIOU]") or has_match(rfc_1[3], r"[0-9]")
        # Date-of-birth is a date.   
        okay_03 = valid_datestring(rfc_1[k_inits:(k_inits+6)])
        
        okay_05 = has_match(rfc_1, r"^[A-Z]{3,4}[0-9]{6}$")
        
        # Initial validator.   
        okays[0] = (okay_01 and okay_02 and okay_03)
        # Verificator digit validator.  
        okays[1] = (len(rfc_1) == len(rfc_0) 
                and cls.get_verificator(rfc_1[:-1], 'RFC') == rfc_1[-1])
        # Homonymial Keys
        okays[2] = (len(rfc_1) == len(rfc_0)
                and rfc_1[-3:-1] == rfc_0[-3:-1])
        # Date of Birth
        okays[3] = okay_03 and (rfc_1[k_inits:(k_inits+6)] == rfc_0[k_inits:(k_inits+6)])
        # Initials
        okays[4] = okay_02 and (rfc_1[:k_inits] == rfc_0[:k_inits])
        # Pseudo-RFC. 
        okays[5] = okay_05 and okays[4] and okays[3]
        return okays

           

class PersonaFisica:
    def __init__(self, nombres_ls):
        dict_rm_chars = dict((c_char, '') for c_char in IGNORE_CHARS['RFC'])
        str_rm_chars = partial(str_multisub, sub_dict=dict_rm_chars, escape=True)

        reg_stopwds = dict((rf'\b{word}\b', ' ') for word in IGNORE_WORDS['RFC'])
        str_stopwds = partial(str_multisub, sub_dict=reg_stopwds, escape=False)

        nombres_0 = pipe(nombres_ls, str_rm_chars, str.upper, str_normalize)

        self.la_cadena = str_spacing(' '.join(nombres_0))
        self.la_lista = compose(nombres_0, str_stopwds, str_spacing)
        
        self.identificar_elementos()
        

    def identificar_elementos(self):
        the_list = self.la_lista

        lastnames = the_list[:2]
        the_names = the_list[ 2].split(' ')
        use_first = (len(the_names) == 1) | (the_names[0] not in NAZARENES)
        
        self.apellido_p = the_list[0]
        self.apellido_m = the_list[1]
        self.nombres = the_list[2]
        
        self.k_nombres = len(the_names)
        self.nombre_base = the_names[0] if use_first else the_names[1]
        self.un_apellido = ''.join(lastnames) if ('' in lastnames) else None


    def obtener_iniciales(self, modo='estandar'):
        if   modo == 'estandar':
            initials = list(map(lambda x: x[0], self.la_lista))

        elif modo == 'RFC':
            p_vowels = list(filter(lambda a_char: a_char in 'AEIOU', self.apellido_p[1:]))
                        
            if self.un_apellido:
                initials = self.un_apellido[:2] + self.nombre_base[:2]

            elif len(self.apellido_p) < 3 | len(p_vowels) < 1:
                initials = self.apellido_p[0] + self.apellido_m[0] + self.nombre_base[:2]
            
            else: 
                initials= (self.apellido_p[0] + p_vowels[0] + 
                            self.apellido_m[0] + self.nombre_base[0])
            
            if initials in INCONVENIENTS['RFC']: 
                initials = initials[0:3] + 'X'

        elif modo == 'CURP': 
            pass
            
        return initials


def rfc_completo(tipo: str, nombres_ls: list, f_inicio: date) -> str:  
    # TIPO: 'fisica' o 'moral'
    # NOMBRES_LS tiene: 
    #   - 3 elementos: apellido_p, apellido_m, nombres_juntos; en persona física.
    #   - 1 elemento con espacios en persona moral. 
    # F_INICIO: tiene formato de fecha. 
    
    nombres_obj = PersonaFisica(nombres_ls)

    rfc_0 = rfc_inicial(tipo, nombres_obj)
    rfc_1 = (rfc_0 + f_inicio.strftime('%y%m%d'))
    
    homoclave_1 = homoclave(nombres_obj.la_cadena)
    rfc_2 = rfc_1 + homoclave_1
    
    verificador_2 = verificador(rfc_2)
    rfc_final = rfc_2 + verificador_2 

    return rfc_final


#%% Componentes secundarios
def rfc_inicial(tipo: str, nombres_obj: PersonaFisica) -> str:
    # INPUTS como arriba; 
    # -> INICIALES   : cuatro letras
    # -> NOMBRES_STR : nombres concatenados
    if tipo == 'fisica':  
        iniciales = nombres_obj.obtener_iniciales(modo='RFC')

    elif tipo == 'moral':
        # Quitar caracteres y palabras no usadas.
        pass
    else:
        print('ERROR')
    
    return iniciales


def homoclave(nombres: str) -> str:
    # En realidad la homoclave consta de dos caracteres, el tercero es el digito verificador. 
    char_posiciones = [CHARS_1.index(c_char) for c_char in list(nombres)] 
    posiciones_str  = ['0'] + [f'{c_pos:02}'  for c_pos  in char_posiciones]

    # Nótese que c_i = cadena[i + 1] para i = 0... len(cadena-2)
    cadena = [int(c_char) for c_char in ''.join(posiciones_str)]
    terms  = [10*cadena[i]*c_i + c_i**2 for i, c_i in enumerate(cadena[1:])]
    calc_trippy = sum(terms) % 1000
    
    (cociente, residuo) = (calc_trippy // 34, calc_trippy % 34)
    homo_1 = CHARS_2[cociente]
    homo_2 = CHARS_2[residuo ]
    return (homo_1 + homo_2) 


def verificador(pre_id: str, tipo=None) -> str:  
    # El verificador es el tercero de la homoclave. 
    
    parametros = {
        'RFC' : (CHARS_3, CHARS_4, 12, 11), 
        'CURP': (CHARS_5, CHARS_6, 17, 10)
    }
    if tipo not in parametros: 
        tipo = 'RFC'

    llaves_in, llaves_out, k_in, k_out = parametros[tipo]
    
    seq_idx = [llaves_in.index(c_char) for c_char in pre_id]
    calc_suma = sum(seq_idx[i]*(k_in+1 - i) for i in range(k_in))
    digito_ver = llaves_out[calc_suma % k_out]
        
    return digito_ver



if __name__ == '__main__':
    ## Imports preparation.
    
    # import src.utilities.parsers as parsers
    
    # ## Setup the parsers.
    # the_parser = parsers.rfc_parser()
    # the_args = the_parser.parse_args()

    # el_rfc = rfc_completo('fisica',  
    #     nombres_ls = [the_args.apellido_p, the_args.apellido_m, the_args.nombres], 
    #     f_inicio = datetime.strptime(the_args.f_inicio, '%Y-%m-%d'))

    # print(f'\tEl RFC es: {el_rfc}')


    # person_dict = {
    #     # 'person_type': 'physical',
    #     'names_list' : ['Villamil', 'Pesqueira', 'Diego'], 
    #     'date_of_birth' : date(1983, 12, 27), 
    #     'state_of_birth': 'Ciudad de México', 
    #     'gender' : 'H'
    # }
    
    person_dict = {
        'firstName' : "Alejandra Jimena",
        'maternalLastName': "Ruiz", 
        'dateOfBirth' : date(1985, 6, 14), 
        'stateOfBirth': 'Nuevo León', 
        'lastName' : "Rodriguez", 
        'gender' : 'H'
    }
    
    # Construc

    person_obj = PersonPhysical(**person_dict)
    el_rfc = person_obj.get_rfc()
    # el_curp = person_obj.get_curp()

    print(f'\nRFC\t: {el_rfc}\n')