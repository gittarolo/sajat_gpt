import io
import sys
from contextlib import redirect_stdout
import traceback


def run_python_code(code_string):
    """
    Biztonságosan lefuttatja a Python kódot,
    és elfogja a standard kimenetet, valamint az esetleges hibákat.
    """
    # Egy virtuális szövegfájl, ami elkapja a kimenetet
    output_catcher = io.StringIO()

    try:
        # A kimenet átirányítása a virtuális fájlba
        with redirect_stdout(output_catcher):
            # A kód végrehajtása egy elszigetelt névtérben (dictionary)
            exec(code_string, {})

        # Ha sikeresen lefutott, visszaadjuk a kimenetet
        return True, output_catcher.getvalue()
    except Exception as e:
        # Ha szintaktikai vagy logikai hiba van, elkapjuk a pontos hibaüzenetet
        error_msg = traceback.format_exc()
        return False, error_msg