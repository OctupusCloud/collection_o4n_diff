# Clase find patrón en un archivo de configuración
# By Ed Scrimgalia

import re

class RegMatch():
    """ Clase para reslover matchs en la colección o4n_diff """
    def __init__(self, expresion, case_sensitive: bool = False) -> None:
        self._regexp = expresion
        self._cs = case_sensitive

    @property
    def expreg(self):
        return self._regexp
    
    @expreg.setter
    def expreg(self, exp):
        self._regexp = f"r{exp}"

    @property
    def case_sensitive(self):
        return self._cs
    
    def pattern(self):
        if not self._cs:
            return re.compile(self.expreg, re.IGNORECASE)
        else:
            return re.compile(self.expreg)
        
    def lector(self, file_path):
        with open(file_path, "r") as file:
            file_as_text = file.read()

        return file_as_text
    
    def findall(self, texto: str):
        """ 
        findall() -> lista de matches
        """
        match = self.pattern().findall(texto)

        return match

    def finditer(self, texto: str):
        """ 
        finditer() -> secuencia de match object (iterable)

        match object (iterable):
        (0, 2) -> match en posisión cero dos caracteres
        (22, 24) -> match en posisión veintidos cuatro caracteres
        (29, 31) -> match en posisión veintinueve dos caracteres
        """

        match = self.pattern().finditer(texto)

        return match


if __name__ == "__main__":
    
    # Expresion regular que se recibe como parámetro
    exp_reg = "int[a-z]+\s*[a-zA-z]+\s*[0-9]/[0-9]"
    
    # Objeto Expresion Regular
    r = RegMatch(exp_reg)

    # Read file
    file = r.lector("config.txt")

    # Uso de metodo finditer
    span = r.finditer(file)
    for match in span:
        print (match.group(),match.span())

    # Uso de metodo findall
    lista = r.findall(file)
    print (lista)