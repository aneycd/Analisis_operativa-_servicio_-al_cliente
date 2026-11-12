import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from openpyxl import load_workbook

# Leer solo un archivo específico pasado como argumento
import sys
if len(sys.argv) < 2:
    print("Uso: python inspect_insumos.py <nombre_archivo.xlsx>")
    sys.exit(1)

fname = sys.argv[1]
base = Path(r"C:\Users\Aney\AppData\Local\Temp\opencode")
xlsx_path = base / fname

print(f"\n{'='*70}")
print(f"ARCHIVO: {xlsx_path.name}")
print(f"{'='*70}")

wb = load_workbook(str(xlsx_path), data_only=True)
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f"\n  Hoja: {sheet_name}")
    print(f"  max_row: {ws.max_row}, max_column: {ws.max_column}")
    
    # Leer solo las primeras 5 filas para encontrar encabezados
    for row_idx in range(1, min(6, ws.max_row + 1)):
        row_vals = [c.value for c in ws[row_idx]]
        non_empty = [(i, v) for i, v in enumerate(row_vals) if v is not None and str(v).strip() != ""]
        if non_empty:
            cols = [(i, str(v)) for i, v in non_empty]
            print(f"  Fila {row_idx}: {cols}")
wb.close()
