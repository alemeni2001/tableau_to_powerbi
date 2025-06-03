import xml.etree.ElementTree as ET
import json
import os
import random
import re

"""
    Genera un string aleatorio de 20 caracteres hexadecimales.
    Se utiliza como identificador único para dashboards y visuals.
"""
def generar_hex_metodo():
    
    digitos_hex = '0123456789abcdef'
    return ''.join(random.choice(digitos_hex) for _ in range(20))

"""
    Extrae información de dependencias de datos y metadatos de cada worksheet
    desde un archivo Tableau (.twb). Devuelve una lista de diccionarios con la información.
    También guarda un archivo JSON con los datos extraídos.
"""
def extract_datasource_and_dependencies(twb_file_path):
    
    try:
        tree = ET.parse(twb_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error al procesar el archivo XML: {e}")
        return []

    extracted_data_dependencies = []

    for worksheet in root.findall(".//worksheet"):
        run_tag = worksheet.find(".//run")
        worksheet_title = run_tag.text if run_tag is not None else ""
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
    with open("extracted_data_dependencies.json", "w", encoding="utf-8") as f:
        json.dump(extracted_data_dependencies, f, ensure_ascii=False, indent=2)
        print("Archivo JSON generado con los datos extraídos.")
    return extracted_data_dependencies

#Función para gráfico de columnas
def generate_json_column_graph(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo columna (clusteredColumnChart).
    Devuelve el diccionario listo para ser guardado como visual.json.
    """
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_title = worksheet["worksheet_title"]
    worksheet_relation = worksheet["worksheet_datasources"][0].get('caption', '')
    worksheet_cols = worksheet["cols"][0] if worksheet["cols"] else ""
    worksheet_rows = worksheet["rows"][0] if worksheet["rows"] else ""
    worksheet_derivation = {
        "Sum": 0, "Promedio": 1, "Recuento(distintivo)": 2, "Minimo": 3, "Maximo": 4,
        "Recuento": 5, "Mediana": 6, "DesviacionEstándar": 7, "Varianza": 8, "None": 0
    }.get(worksheet["dependency_info"][0]["column_instances"][0].get("derivation", ""), 0)
    direction = "Ascending"
    isDefaultSort_true = True
    visualContainerObjects_value = "Nombre Prueba"
    drillFilterOtherVisuals = True
    position_X = 100
    position_Y = 100
    position_Z = 2
    position_height = 300
    position_width = 300

    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {
            "x": position_X,
            "y": position_Y,
            "z": position_Z,
            "height": position_height,
            "width": position_width
        },
        "visual": {
            "visualType": "clusteredColumnChart",
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
                                "queryRef": f"{worksheet_relation}.{worksheet_cols}",
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
                                        "Function": worksheet_derivation
                                    }
                                },
                                "queryRef": f"Sum({worksheet_relation}.{worksheet_rows})",
                                "nativeQueryRef": f"Suma de {worksheet_rows}"
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
                                    "Property": worksheet_rows
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
    return data

#Función para gráfico de barras
def generate_json_bar_graph(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo barra (barChart).
    Devuelve el diccionario listo para ser guardado como visual.json.
    """
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_title = worksheet["worksheet_title"]
    worksheet_relation = worksheet["worksheet_datasources"][0].get('caption', '')
    worksheet_cols = worksheet["cols"][0] if worksheet["cols"] else ""
    worksheet_rows = worksheet["rows"][0] if worksheet["rows"] else ""
    worksheet_derivation = {
        "Sum": 0, "Promedio": 1, "Recuento(distintivo)": 2, "Minimo": 3, "Maximo": 4,
        "Recuento": 5, "Mediana": 6, "DesviacionEstándar": 7, "Varianza": 8, "None": 0
    }.get(worksheet["dependency_info"][0]["column_instances"][0].get("derivation", ""), 0)
    direction = "Ascending"
    isDefaultSort_true = True
    visualContainerObjects_value = "Nombre Prueba"
    drillFilterOtherVisuals = True
    position_X = 100
    position_Y = 100
    position_Z = 2
    position_height = 300
    position_width = 300

    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {
            "x": position_X,
            "y": position_Y,
            "z": position_Z,
            "height": position_height,
            "width": position_width
        },
        "visual": {
            "visualType": "barChart",
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
                                "queryRef": f"{worksheet_relation}.{worksheet_cols}",
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
                                        "Function": worksheet_derivation
                                    }
                                },
                                "queryRef": f"Sum({worksheet_relation}.{worksheet_rows})",
                                "nativeQueryRef": f"Suma de {worksheet_rows}"
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
                                    "Property": worksheet_rows
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
    return data

#Función para gráfico de líneas
def generate_json_line_graph(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo línea (lineChart) con solo la columna de fecha en el eje X y filtros simples.
    """
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_relation = worksheet["worksheet_datasources"][0].get('caption', '')
    worksheet_cols = worksheet["cols"][0] if worksheet["cols"] else ""
    worksheet_rows = worksheet["rows"][0] if worksheet["rows"] else ""
    worksheet_derivation = {
        "Sum": 0, "Promedio": 1, "Recuento(distintivo)": 2, "Minimo": 3, "Maximo": 4,
        "Recuento": 5, "Mediana": 6, "DesviacionEstándar": 7, "Varianza": 8, "None": 0
    }.get(worksheet["dependency_info"][0]["column_instances"][0].get("derivation", ""), 0)
    position_X = 9.4488915545918015
    position_Y = 0
    position_Z = 0
    position_height = 680.32019193060978
    position_width = 1160.3238829038733
 
    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {
            "x": position_X,
            "y": position_Y,
            "z": position_Z,
            "height": position_height,
            "width": position_width,
            "tabOrder": 0
        },
        "visual": {
            "visualType": "lineChart",
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
                                "queryRef": f"{worksheet_relation}.{worksheet_cols}",
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
                                        "Function": worksheet_derivation
                                    }
                                },
                                "queryRef": f"Sum({worksheet_relation}.{worksheet_rows})",
                                "nativeQueryRef": f"Suma de {worksheet_rows}"
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
                            "direction": "Ascending"
                        }
                    ],
                    "isDefaultSort": True
                }
            },
            "drillFilterOtherVisuals": True
        },
        "filterConfig": {
            "filters": [
                {
                    "name": generar_hex_metodo(),
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
                    "type": "Categorical"
                },
                {
                    "name": generar_hex_metodo(),
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
                            "Function": worksheet_derivation
                        }
                    },
                    "type": "Advanced"
                }
            ]
        }
    }
    return data
 
#Función para gráfico de torta
def generate_json_pie(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo torta (pieChart) con categoría y valor.
    """
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_relation = worksheet["worksheet_datasources"][0].get('caption', '')
    worksheet_cols = worksheet["cols"][0] if worksheet["cols"] else ""
    worksheet_rows = worksheet["rows"][0] if worksheet["rows"] else ""
    worksheet_derivation = {
        "Sum": 0, "Promedio": 1, "Recuento(distintivo)": 2, "Minimo": 3, "Maximo": 4,
        "Recuento": 5, "Mediana": 6, "DesviacionEstándar": 7, "Varianza": 8, "None": 0
    }.get(worksheet["dependency_info"][0]["column_instances"][0].get("derivation", ""), 0)
    position_X = 9.4488915545918015
    position_Y = 0
    position_Z = 0
    position_height = 685.98952686336486
    position_width = 1184.891000945812
 
    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {
            "x": position_X,
            "y": position_Y,
            "z": position_Z,
            "height": position_height,
            "width": position_width,
            "tabOrder": 0
        },
        "visual": {
            "visualType": "pieChart",
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
                                "queryRef": f"{worksheet_relation}.{worksheet_cols}",
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
                                        "Function": worksheet_derivation
                                    }
                                },
                                "queryRef": f"Sum({worksheet_relation}.{worksheet_rows})",
                                "nativeQueryRef": f"Suma de {worksheet_rows}"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
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
                                    "Function": worksheet_derivation
                                }
                            },
                            "direction": "Descending"
                        }
                    ],
                    "isDefaultSort": True
                }
            },
            "drillFilterOtherVisuals": True
        },
        "filterConfig": {
            "filters": [
                {
                    "name": generar_hex_metodo(),
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
                    "type": "Categorical"
                },
                {
                    "name": generar_hex_metodo(),
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
                            "Function": worksheet_derivation
                        }
                    },
                    "type": "Advanced"
                }
            ]
        }
    }
    return data

#Función para gráfico de tablas
def generate_json_table(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo tabla (tableEx) con todas las columnas del worksheet,
    respetando el orden y la estructura del ejemplo dado.
    """
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_relation = worksheet["worksheet_datasources"][0].get('caption', '')
    worksheet_cols = worksheet.get("cols") or [col["name"].strip("[]") for col in worksheet.get("dependency_info", [{}])[0].get("columns", [])] or ["ColumnaDefault"]
    
    # Posiciones y dimensiones según tu ejemplo
    position_X = 532.91748367897765
    position_Y = 120.94581189877506
    position_Z = 4
    position_height = 177.63916122632588
    position_width = 487.56280421693697
    tabOrder = 2

    # Proyecciones y filtros dinámicos para cada columna
    projections = []
    filters = []
    for col in worksheet_cols:
        projections.append({
            "field": {
                "Column": {
                    "Expression": {
                        "SourceRef": {
                            "Entity": worksheet_relation
                        }
                    },
                    "Property": col
                }
            },
            "queryRef": f"{worksheet_relation}.{col}",
            "nativeQueryRef": col
        })
        filters.append({
            "name": generar_hex_metodo(),
            "field": {
                "Column": {
                    "Expression": {
                        "SourceRef": {
                            "Entity": worksheet_relation
                        }
                    },
                    "Property": col
                }
            },
            "type": "Categorical"
        })

    data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {
            "x": position_X,
            "y": position_Y,
            "z": position_Z,
            "height": position_height,
            "width": position_width,
            "tabOrder": tabOrder
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": projections
                    }
                }
            },
            "drillFilterOtherVisuals": True
        },
        "filterConfig": {
            "filters": filters
        }
    }
    return data
"""
    Extrae la relación entre dashboards y worksheets desde el archivo Tableau (.twb).
    Devuelve una lista de dashboards, cada uno con su nombre y los worksheets asociados.
"""
def extract_dashboards_and_worksheets(twb_file_path):
    
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

"""
    Normaliza un nombre de worksheet o dashboard para comparación (minúsculas y sin espacios extra).
"""
def normalize_name(name):
    
    return name.strip().lower() if name else ""


if __name__ == "__main__":
    # Ruta al archivo Tableau
    twb_path = f"C:\\Users\\jesquemb\\OneDrive - NTT DATA EMEAL\\Documentos\\Santander\\TableauPrueba.twb"
    
    # Extraer dashboards y worksheets
    dashboards = extract_dashboards_and_worksheets(twb_path)
    extracted_data = extract_datasource_and_dependencies(twb_path)
    dashboard_hex_list = []

    # Procesar cada dashboard y generar carpetas y archivos de página y visuals
    for dashboard in dashboards:
        print(f"Dashboard: {dashboard['dashboard_name']} - Worksheets asociados: {dashboard['worksheet_names']}")
        dashboard_hex = generar_hex_metodo()
        dashboard_hex_list.append(dashboard_hex)
        page_folder = f"C:\\Users\\jesquemb\\OneDrive - NTT DATA EMEAL\\Documentos\\Santander\\PowerBI\\Demo.report\\definition\\pages\\{dashboard_hex}"
        os.makedirs(page_folder, exist_ok=True)
        page_json = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.4.0/schema.json",
            "name": dashboard_hex,
            "displayName": dashboard['dashboard_name'],
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280
        }
        with open(f"{page_folder}\\page.json", "w", encoding="utf-8") as f:
            json.dump(page_json, f, ensure_ascii=False, indent=2)

        visuals_folder = f"{page_folder}\\visuals"
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
                visual_subfolder = f"{visuals_folder}\\{worksheet_hex}"
                visual_json_path = f"{visual_subfolder}\\visual.json"
                if not os.path.exists(visual_json_path):
                    os.makedirs(visual_subfolder, exist_ok=True)
                    data = generate_json_table([worksheet_data], worksheet_hex)    
                

                    with open(visual_json_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                visuals_creados.add(normalized_name)

    # Crear pages.json con la lista de páginas y la página activa
    pages_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": dashboard_hex_list,
        "activePageName": dashboard_hex_list[0] if dashboard_hex_list else ""
    }
    pages_json_path = "C:\\Users\\jesquemb\\OneDrive - NTT DATA EMEAL\\Documentos\\Santander\\PowerBI\\Demo.report\\definition\\pages\\pages.json"
    os.makedirs(os.path.dirname(pages_json_path), exist_ok=True)
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
    report_json_path = "C:\\Users\\jesquemb\\OneDrive - NTT DATA EMEAL\\Documentos\\Santander\\PowerBI\\Demo.report\\definition\\report.json"
    os.makedirs(os.path.dirname(report_json_path), exist_ok=True)
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_json, f, ensure_ascii=False, indent=2)
    