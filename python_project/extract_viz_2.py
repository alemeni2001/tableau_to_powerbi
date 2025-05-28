import xml.etree.ElementTree as ET
import json
import os
import random
import re

def generar_hex_metodo():
    digitos_hex = '0123456789abcdef'
    return ''.join(random.choice(digitos_hex) for _ in range(20))

def extract_datasource_and_dependencies(twb_file_path):
    """
    Extrae los atributos de los tags datasource y datasource-dependencies, incluyendo sus hijos.
    """
    try:
        tree = ET.parse(twb_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error al procesar el archivo XML: {e}")
        return []

    extracted_data_dependencies = []

    # Buscar todas las <worksheet> en cualquier nivel del XML
    for worksheet in root.findall(".//worksheet"):
        # Extraer el título del worksheet desde el tag <run>
        run_tag = worksheet.find(".//run")
        worksheet_title = run_tag.text if run_tag is not None else ""

         # Extraer los tags <cols> y <rows>
        cols_tag = worksheet.find(".//cols")
        rows_tag = worksheet.find(".//rows")

        # Asegurarse de que los valores no sean None y convertirlos a cadenas vacías si es necesario
        cols_value = cols_tag.text if cols_tag is not None and cols_tag.text is not None else ""
        rows_value = rows_tag.text if rows_tag is not None and rows_tag.text is not None else ""

        # Usar expresiones regulares para extraer el contenido del segundo corchete
        cols_extracted = re.search(r":(.*?):", cols_value)
        rows_extracted = re.search(r":(.*?):", rows_value)

        # Si se encuentra un valor, tomarlo; de lo contrario, dejarlo vacío
        cols_result = cols_extracted.group(1) if cols_extracted else ""
        rows_result = rows_extracted.group(1) if rows_extracted else ""


        worksheet_info = {
            "worksheet_name": worksheet.get("name", ""),
            "worksheet_title": worksheet_title,
            "type": worksheet.find(".//mark").get("class", ""),
            "worksheet_datasources": [],
            "dependency_info": [],
            "cols": cols_result,
            "rows": rows_result
        }

        # Buscar <datasources> dentro del contexto del <worksheet>
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
                    break  # Solo tomamos el primer <relation> encontrado

                # Agregar el atributo 'relation_name' al datasource_info
                datasource_info["relation_name"] = relation_name

                worksheet_info["worksheet_datasources"].append(datasource_info)


        # Buscar <datasource-dependencies> dentro del contexto del <worksheet>
        for dependencies in worksheet.findall(".//datasource-dependencies"):
            dependency_info = {
                "datasource": dependencies.get("datasource", ""),
                "columns": [],
                "column_instances": []
            }

            # Extraer información de los tags <column> dentro de <datasource-dependencies>
            for column in dependencies.findall(".//column"):
                column_info = {
                    "caption": column.get("caption", ""),
                    "name": column.get("name", ""),
                    "role": column.get("role", ""),
                    "calculation_formula": column.find("calculation").get("formula", "") if column.find("calculation") is not None else ""
                }
                dependency_info["columns"].append(column_info)

            # Extraer información de los tags <column-instance> dentro de <datasource-dependencies>
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
    with open("extracted_data_dependencies.json", "w", encoding="utf-8") as f:
        json.dump(extracted_data_dependencies, f, ensure_ascii=False, indent=2)
        print("Archivo JSON generado con los datos extraídos.")
    return extracted_data_dependencies




def generate_json_graph(extracted_data, output_file):
    """
    Genera un archivo JSON con los datos extraídos en un formato específico para gráficos.
    """
    graph_data = []

    for worksheet_data in extracted_data:
        # variables usadas y validadas
        worksheet_title = worksheet_data["worksheet"]["worksheet_title"]
        worksheet_relation = (worksheet_data["worksheet"]["worksheet_datasources"][0]['relation_name'] if worksheet_data["worksheet"]["worksheet_datasources"][0].get('relation_name') else "")
        worksheet_cols = worksheet_data["worksheet"]["cols"] if worksheet_data["worksheet"]["cols"] else ""
        worksheet_rows = worksheet_data["worksheet"]["rows"]
        worksheet_visualType = worksheet_data["worksheet"]["type"]   

        # variables definidas sin origen a validar
        direction = "Ascending"
        isDefaultSort_true = True
        visualContainerObjects_value = "Nombre Prueba"
        drillFilterOtherVisuals = True
        position_X = 100
        position_Y = 100
        position_Z = 2
        position_height = 300
        position_width = 300
        

        # variables a validar no usadas
        worksheet_name = worksheet_data["worksheet"]["worksheet_name"]
        worksheet_type = worksheet_data["worksheet"]["type"]
        worksheet_datasources = worksheet_data["worksheet"]["worksheet_datasources"]
        worksheet_dependency_info = worksheet_data["worksheet"]["dependency_info"]
        worksheet = worksheet_data["worksheet"]

    
        data = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.6.0/schema.json",
            "name": generar_hex_metodo(),
            "position": {
                "x": position_X,
                "y": position_Y,
                "z": position_Z,
                "height": position_height,
                "width": position_width
            },
            "visual": {
                "visualType": worksheet_visualType,
                "query": {
                "queryState": {
                    "Category": {
                    "projections": [
                        {
                        "field": {
                            "Column": {
                            "Expression": {
                                "SourceRef": {
                                "Entity": worksheet_relation
                                }
                            },
                            "Property": worksheet_cols
                            }
                        },
                        "queryRef": worksheet_relation+ "." + worksheet_cols,
                        "nativeQueryRef": worksheet_cols,
                        "active": True
                        }
                    ]
                    },
                    "Y": {
                    "projections": [
                        {
                        "field": {
                            "Aggregation": {
                            "Expression": {
                                "Column": {
                                "Expression": {
                                    "SourceRef": {
                                    "Entity": worksheet_relation
                                    }
                                },
                                "Property": worksheet_rows
                                }
                            },
                            "Function": 1
                            }
                        },
                        "queryRef": f"A",
                        "nativeQueryRef": worksheet_title
                        }
                    ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                    {
                        "field": {
                        "Column": {
                            "Expression": {
                            "SourceRef": {
                                "Entity": worksheet_relation
                            }
                            },
                            "Property": worksheet_cols
                        }
                        },
                        "direction": direction
                    }
                    ],
                    "isDefaultSort": isDefaultSort_true
                }
                },
                "visualContainerObjects": {
                "title": [
                    {
                    "properties": {
                        "text": {
                        "expr": {
                            "Literal": {
                            "Value": visualContainerObjects_value
                            }
                        }
                        }
                    }
                    }
                ]
                },
                "drillFilterOtherVisuals": drillFilterOtherVisuals
            }
        }

        graph_data.append(data)

    # Guardar el JSON completo en un solo archivo
    # with open(output_file, "w", encoding="utf-8") as f:
    #     json.dump(graph_data, f, ensure_ascii=False, indent=2)


    # Guardar cada elemento de graph_data en un archivo JSON separado
    for idx, data in enumerate(graph_data): 
        output_file = f"graph_data/graph_data_{idx}.json" 
        with open(output_file, "w",encoding="utf-8") as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Archivo JSON para gráficos generado en: {output_file}")

import os

if __name__ == "__main__":
    # Ruta del archivo .twb
    twb_path = r"C:\Users\alejo\OneDrive\Desktop\New folder\TableauPrueba.twb"

    # Comprobar que el archivo existe
    if not os.path.exists(twb_path):
        print(f"El archivo no existe en la ruta: {twb_path}")
        twb_path = input("Por favor, introduce la ruta completa al archivo .twb: ")

    # Extraer datos
    extracted_data = extract_datasource_and_dependencies(twb_path)

    # Generar JSON para gráficos
    output_file = r"C:\Users\alejo\OneDrive\Desktop\New folder\graph_data.json"
    generate_json_graph(extracted_data, output_file)