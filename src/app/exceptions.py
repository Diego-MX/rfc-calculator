
class ValidationError(Exception):
    mapping = {}

    def __init__(self, name: str, detail: str):
        self.name = name
        self.detail = detail

# 404-NotFoundError se refiere al servidor, no al resultado.  
# Revisar con los proveedores el uso de NotFoundError. 
class FormatError(ValidationError):
    pass

ValidationError.mapping ={
    FormatError: 500}
