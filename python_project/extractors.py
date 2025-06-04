import xml.etree.ElementTree as ET
import json
import re
from typing import List, Dict, Any

def extract_datasource_and_dependencies(twb_file_path: str) -> List[Dict[str, Any]]:
    """
    Extrae información de dependencias de datos y metadatos de cada worksheet
    desde un archivo Tableau (.twb). Devuelve una lista de diccionarios con la información.
    También guarda un archivo JSON con los datos extraídos.
    """
    try:
        tree = ET.parse(twb_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error al procesar el archivo XML: {e}")
        return []

    extracted_data_dependencies = []

    for worksheet in root.findall(".//worksheet"):
        # Extrae el título del worksheet
        run_tag = worksheet.find(".//run")
        worksheet_title = run_tag.text if run_tag is not None else ""

        # Extrae columnas y filas
        cols_tag = worksheet.find(".//cols")
        rows_tag = worksheet.find(".//rows")
        cols_value = cols_tag.text if cols_tag is not None and cols_tag.text is not None else ""
        rows_value = rows_tag.text if rows_tag is not None and rows_tag.text is not None else ""
        cols_result = re.findall(r":(.*?):", cols_value)
        rows_result = re.findall(r":(.*?):", rows_value)

        worksheet_info = {
            "worksheet_name": worksheet.get("name", ""),
            "worksheet_title": worksheet_title,
            "type": worksheet.find(".//mark").get("class", ""),
            "worksheet_datasources": [],
            "dependency_info": [],
            "cols": cols_result,
            "rows": rows_result
        }

        # Extrae datasources asociados al worksheet
        for datasources in worksheet.findall(".//datasources"):
            for datasource in datasources.findall(".//datasource"):
                datasource_info = {
                    "caption": datasource.get("caption", ""),
                    "name": datasource.get("name", "")
                }
                datasource_name = datasource.get("name", "")
                relation_name = None
                for relation in root.findall(f".//datasource[@name='{datasource_name}']//relation//relation"):
                    relation_name = relation.get("name", "")
                    break
                datasource_info["relation_name"] = relation_name
                worksheet_info["worksheet_datasources"].append(datasource_info)

        # Extrae dependencias de columnas
        for dependencies in worksheet.findall(".//datasource-dependencies"):
            dependency_info = {
                "datasource": dependencies.get("datasource", ""),
                "columns": [],
                "column_instances": []
            }
            for column in dependencies.findall(".//column"):
                column_info = {
                    "caption": column.get("caption", ""),
                    "name": column.get("name", ""),
                    "role": column.get("role", ""),
                    "calculation_formula": column.find("calculation").get("formula", "") if column.find("calculation") is not None else ""
                }
                dependency_info["columns"].append(column_info)
            for column_instance in dependencies.findall(".//column-instance"):
                column_instance_info = {
                    "column": column_instance.get("column", ""),
                    "derivation": column_instance.get("derivation", "")
                }
                dependency_info["column_instances"].append(column_instance_info)
            worksheet_info["dependency_info"].append(dependency_info)

        extracted_data_dependencies.append({
            "worksheet": worksheet_info
        })

    # Guarda el archivo JSON con los datos extraídos
    with open("extracted_data_dependencies.json", "w", encoding="utf-8") as f:
        json.dump(extracted_data_dependencies, f, ensure_ascii=False, indent=2)
        print("Archivo JSON generado con los datos extraídos.")
    return extracted_data_dependencies

def extract_dashboards_and_worksheets(twb_file_path: str) -> List[Dict[str, Any]]:
    """
    Extrae los dashboards y los worksheets asociados desde un archivo Tableau (.twb).
    Devuelve una lista de diccionarios con el nombre del dashboard y los worksheets asociados.
    """
    try:
        tree = ET.parse(twb_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error al procesar el archivo XML: {e}")
        return []
    dashboards = []
    for dashboard in root.findall(".//dashboard"):
        dashboard_name = dashboard.get("name", "")
        worksheet_names = []
        for zone in dashboard.findall(".//zone"):
            ws_name = zone.get("name")
            if ws_name:
                worksheet_names.append(ws_name)
        worksheet_names = list(dict.fromkeys(worksheet_names))
        dashboards.append({
            "dashboard_name": dashboard_name,
            "worksheet_names": worksheet_names
        })
    return dashboards
