import json
import os

def map_tableau_to_powerbi_type(tableau_type):
    mapping = {
        "Pie": "pieChart",
        "Bar": "clusteredBarChart",
        "Line": "lineChart",
        "Circle": "scatterChart",
        "Text": "card",
        "Automatic": "barChart"
    }
    return mapping.get(tableau_type, "table")

def generate_layout(tableau_json_path, output_layout_path):
    with open(tableau_json_path, "r", encoding="utf-8") as f:
        tableau_data = json.load(f)

    visual_containers = []

    for i, ws_data in enumerate(tableau_data):
        worksheet = ws_data["worksheet"]
        visual_type = map_tableau_to_powerbi_type(worksheet.get("type", ""))
        title = worksheet.get("worksheet_name", f"Visual {i+1}")
        datasource = worksheet["worksheet_datasources"][0]["caption"] if worksheet["worksheet_datasources"] else "Tabla1"

        category_fields = []
        y_fields = []
        aggregation = "SUM"

        for dep in worksheet.get("dependency_info", []):
            for col in dep.get("columns", []):
                clean_name = col["name"].strip("[]")
                if col["role"] == "dimension":
                    category_fields.append(f"{datasource}[{clean_name}]")
                elif col["role"] == "measure":
                    y_fields.append(f"{aggregation}({datasource}[{clean_name}])")

        visual_config = {
            "singleVisual": {
                "visualType": visual_type,
                "projections": {
                    "Category": category_fields,
                    "Y": y_fields
                },
                "title": {
                    "visible": True,
                    "text": title
                }
            }
        }

        visual = {
            "x": 0 + (i * 420),
            "y": 0,
            "z": i,
            "width": 400,
            "height": 300,
            "name": f"visual{i+1}",
            "config": json.dumps(visual_config)
        }

        visual_containers.append(visual)

    layout = {
        "sections": [
            {
                "name": "Page 1",
                "displayName": "Página 1",
                "visualContainers": visual_containers
            }
        ]
    }

    output_dir = os.path.dirname(output_layout_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_layout_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)

    print(f"Layout generado en: {output_layout_path}")

def inject_layout_into_reportjson(layout_json_path, pbip_project_path):
    report_folders = [f for f in os.listdir(pbip_project_path) if f.endswith(".Report")]
    if not report_folders:
        raise FileNotFoundError(f"No se encontró carpeta *.Report en: {pbip_project_path}")

    report_folder = os.path.join(pbip_project_path, report_folders[0])
    report_json_path = os.path.join(report_folder, "report.json")

    if not os.path.exists(report_json_path):
        raise FileNotFoundError(f"No se encontró report.json en: {report_json_path}")

    with open(report_json_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    with open(layout_json_path, "r", encoding="utf-8") as f:
        layout_data = json.load(f)

    if len(report_data.get("sections", [])) == 0:
        raise ValueError("report.json no tiene secciones")

    if len(layout_data.get("sections", [])) == 0:
        raise ValueError("layout.json no tiene secciones")

    report_data["sections"][0]["visualContainers"] = layout_data["sections"][0]["visualContainers"]
    report_data["sections"][0]["displayName"] = layout_data["sections"][0].get("displayName", report_data["sections"][0]["displayName"])

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"Layout visual inyectado correctamente en: {report_json_path}")

# ---------- PARAMETROS ----------
input_json = r"C:\Users\alejo\OneDrive\Desktop\New folder\extracted_data_dependencies.json"
layout_json = r"C:\Users\alejo\OneDrive\Desktop\New folder\layout.json"
pbip_folder = r"C:\Users\alejo\OneDrive\Desktop\New folder\prueba"

# Ejecutar generación de layout
generate_layout(input_json, layout_json)

# Inyectar layout en report.json dentro de .Report de pbip
inject_layout_into_reportjson(layout_json, pbip_folder)
