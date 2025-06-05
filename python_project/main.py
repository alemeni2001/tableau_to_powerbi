import os
import json

from extractors import extract_datasource_and_dependencies, extract_dashboards_and_worksheets
from generators import (
    generate_json_column_graph, generate_json_bar_graph, generate_json_line_graph,
    generate_json_pie, generate_json_table, get_visual_generator_by_type
)
from utils import generar_hex_metodo, normalize_name

"""
Script principal para convertir dashboards de Tableau a la estructura de Power BI.
Extrae dashboards y worksheets, genera la estructura de carpetas y archivos JSON.
"""

# Ruta base del proyecto Tableau (donde está el .twb)
BASE_PATH = r"C:\Users\alejo\OneDrive\Desktop\tableau_to_powerbi\python_project"
# Ruta base del proyecto Power BI (donde quieres los archivos generados) hasta la carpeta definition
POWERBI_PROJECT_PATH = r"C:\Users\alejo\OneDrive\Desktop\prueba\prueba.Report\definition"


if __name__ == "__main__":
    try:
        # Ruta al archivo Tableau
        twb_path = os.path.join(BASE_PATH, "TableauPrueba.twb")
        
        # Validación de existencia del archivo
        if not os.path.exists(twb_path):
            raise FileNotFoundError(f"No se encontró el archivo Tableau en: {twb_path}")
        
        # Extraer dashboards y worksheets
        dashboards = extract_dashboards_and_worksheets(twb_path)
        extracted_data = extract_datasource_and_dependencies(twb_path)
        dashboard_hex_list = []

        # Procesar cada dashboard y generar carpetas y archivos de página y visuals
        pages_folder = os.path.join(POWERBI_PROJECT_PATH, "pages")  # <-- Cambiado
        os.makedirs(pages_folder, exist_ok=True)

        for dashboard in dashboards:
            print(f"Dashboard: {dashboard['dashboard_name']} - Worksheets asociados: {dashboard['worksheet_names']}")
            dashboard_hex = generar_hex_metodo()
            dashboard_hex_list.append(dashboard_hex)
            page_folder = os.path.join(pages_folder, dashboard_hex)
            os.makedirs(page_folder, exist_ok=True)
            page_json = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.4.0/schema.json",
                "name": dashboard_hex,
                "displayName": dashboard['dashboard_name'],
                "displayOption": "FitToPage",
                "height": 720,
                "width": 1280
            }
            with open(os.path.join(page_folder, "page.json"), "w", encoding="utf-8") as f:
                json.dump(page_json, f, ensure_ascii=False, indent=2)

            visuals_folder = os.path.join(page_folder, "visuals")
            os.makedirs(visuals_folder, exist_ok=True)
            visuals_creados = set()
            for worksheet_name in dashboard["worksheet_names"]:
                normalized_name = normalize_name(worksheet_name)
                if normalized_name in visuals_creados:
                    continue
                worksheet_data = next(
                    (ws for ws in extracted_data if normalize_name(ws["worksheet"]["worksheet_name"]) == normalized_name),
                    None
                )
                if worksheet_data:
                    worksheet_hex = generar_hex_metodo()
                    visual_subfolder = os.path.join(visuals_folder, worksheet_hex)
                    visual_json_path = os.path.join(visual_subfolder, "visual.json")
                    if not os.path.exists(visual_json_path):
                        os.makedirs(visual_subfolder, exist_ok=True)
                        worksheet_type = worksheet_data["worksheet"]["type"]
                        generate_func = get_visual_generator_by_type(worksheet_type)
                        data = generate_func([worksheet_data], worksheet_hex)    
                        with open(visual_json_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    visuals_creados.add(normalized_name)

        # Crear pages.json con la lista de páginas y la página activa
        pages_json = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": dashboard_hex_list,
            "activePageName": dashboard_hex_list[0] if dashboard_hex_list else ""
        }
        pages_json_path = os.path.join(pages_folder, "pages.json")  # <-- Cambiado
        with open(pages_json_path, "w", encoding="utf-8") as f:
            json.dump(pages_json, f, ensure_ascii=False, indent=2)

        # Crear report.json con la estructura extendida por defecto de Power BI Desktop
        report_json = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.3.0/schema.json",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU10",
                    "reportVersionAtImport": "5.64",
                    "type": "SharedResources"
                }
            },
            "layoutOptimization": "None",
            "objects": {
                "section": [
                    {
                        "properties": {
                            "verticalAlignment": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Top'"
                                    }
                                }
                            }
                        }
                    }
                ]
            },
            "resourcePackages": [
                {
                    "name": "SharedResources",
                    "type": "SharedResources",
                    "items": [
                        {
                            "name": "CY24SU10",
                            "path": "BaseThemes/CY24SU10.json",
                            "type": "BaseTheme"
                        }
                    ]
                }
            ],
            "settings": {
                "useStylableVisualContainerHeader": True,
                "defaultDrillFilterOtherVisuals": True,
                "allowChangeFilterTypes": True,
                "useDefaultAggregateDisplayName": True
            }
        }
        report_json_path = os.path.join(POWERBI_PROJECT_PATH, "report.json") 
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report_json, f, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"Ocurrió un error: {e}")