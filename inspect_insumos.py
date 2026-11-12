import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from openpyxl import load_workbook

base = Path(r"C:\Users\Aney\AppData\Local\Temp\opencode")

xlsx_files = sorted(base.glob("*.xlsx"))

for xlsx_path in xlsx_files:
    print(f"\n{'='*70}")
    print(f"ARCHIVO: {xlsx_path.name}")
    print(f"{'='*70}")
    try:
        wb = load_workbook(str(xlsx_path), data_only=True)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            print(f"\n  Hoja: {sheet_name}")
            print(f"  max_row: {ws.max_row}, max_column: {ws.max_column}")
            
            # Buscar la fila de encabezados real (primera fila con datos no vacíos)
            header_row_idx = None
            headers = []
            for row_idx in range(1, min(ws.max_row + 1, 10)):
                row_vals = [c.value for c in ws[row_idx]]
                non_empty = [v for v in row_vals if v is not None and str(v).strip() != ""]
                if len(non_empty) >= 2:
                    header_row_idx = row_idx
                    headers = [str(v) if v is not None else "" for v in row_vals]
                    break
            
            if header_row_idx:
                print(f"  Fila de encabezados detectada: {header_row_idx}")
                print(f"  Encabezados: {headers}")
                
                # Contar filas de datos después del encabezado
                data_rows = 0
                for row in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
                    if any(cell is not None and str(cell).strip() != "" for cell in row):
                        data_rows += 1
                print(f"  Filas de datos: {data_rows}")
                
                # Mostrar primeras 2 filas de datos como muestra
                print("  Muestra (primeras 2 filas de datos):")
                count = 0
                for row in ws.iter_rows(min_row=header_row_idx + 1, max_row=header_row_idx + 2, values_only=True):
                    vals = [str(v) if v is not None else "" for v in row]
                    print(f"    Fila {header_row_idx + 1 + count}: {vals}")
                    count += 1
            else:
                print("  No se detectó fila de encabezados clara")
        wb.close()
    except Exception as e:
        print(f"  ERROR al leer el archivo: {type(e).__name__}: {e}")
