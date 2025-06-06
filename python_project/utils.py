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

def scale_zone(zone, max_width, max_height, target_width=1280, target_height=720):
    scale_x = target_width / max_width if max_width else 1
    scale_y = target_height / max_height if max_height else 1
    return {
        "x": int(zone["x"] * scale_x),
        "y": int(zone["y"] * scale_y),
        "width": int(zone["width"] * scale_x),
        "height": int(zone["height"] * scale_y)
    }
