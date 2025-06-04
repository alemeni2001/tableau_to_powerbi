import random

def generar_hex_metodo():
    """
    Genera un string hexadecimal aleatorio de 20 caracteres.
    """
    digitos_hex = '0123456789abcdef'
    return ''.join(random.choice(digitos_hex) for _ in range(20))


def normalize_name(name):
    """
    Normaliza un nombre: elimina espacios al inicio/fin y lo convierte a minúsculas.
    Si el nombre es None, devuelve una cadena vacía.
    """
    return name.strip().lower() if name else ""
