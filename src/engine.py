import re
from operator import itemgetter
from datetime import datetime as dt
from fastapi.exceptions import HTTPException
import pandas as pd

from config import ENV, PATH_DIRS
from src.get_rfc import rfc_completo
from src.authenticate import AzureResourcer
from src.utilities.basic import str_delatinize


def process_rfc_physical(an_input): 
    try: 
        a_person     = an_input.get("personPhysical")
        campos_ls    = ["lastName", "maternalLastName", "firstName"]
        nombres_ls   = itemgetter(*campos_ls)(a_person)
        f_inicio     = dt.strptime(a_person.get("dateOfBirth"), "%Y-%m-%d")
        el_rfc       = rfc_completo("fisica", nombres_ls, f_inicio)
        pre_respuesta = {"rfc" : el_rfc}
        
    except ValueError: 
        excepcion = HTTPException(status_code=400, 
            detail="dateOfBirth: Incorrect data fromat, use YYYY-MM-DD")
        raise excepcion
    except Exception as exc: 
        pre_respuesta = {
            "code"       : "0002",
            "status_code": "500",
            "type"       : "internal-error",
            "instance"   : "input/get-rfc/internal-error",
            "timestamp"  : str(dt.now()),
            "detail"     : str(exc)}
    return pre_respuesta  


def approve_alias(an_alias): 
    offensive_df  = check_feather_file("offensive-words.feather").dropna()
    offensive_srs = offensive_df["Phrase"].str.lower().apply(str_delatinize)

    offensive_str_2 = "|".join( offensive_srs.tolist() )
    offensive_str_1 = re.sub(r" ?\((.*?)\)", r"|\1", offensive_str_2)
    offensive_str   = rf"({(offensive_str_1)})"
    
    is_offensive = re.search(offensive_str, an_alias, re.IGNORECASE)

    response = {"alias": an_alias}
    if is_offensive:
        offense = is_offensive.group(0).lower()
        indices = offensive_srs.str.contains(offense)
        which_offensive = offensive_df.loc[indices, "Type"].tolist()[0]
        response.update({
            "offense": offense, 
            "offenseType" : which_offensive }) 
            
    return response


def check_feather_file(a_file): 
    file_at_dir = PATH_DIRS[ENV]/a_file

    if not file_at_dir.exists(): 
        resourcer = AzureResourcer(ENV) 
        
        (client, path) = resourcer.get_blob_service()
        blob_file = client.get_blob_client("bronze", f"{path}/{a_file}")

        with open(file_at_dir, "wb") as _f: 
            _f.write(blob_file.download_blob().readall())

    return pd.read_feather(file_at_dir)
