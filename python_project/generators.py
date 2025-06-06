from utils import generar_hex_metodo
def is_dimension(field, worksheet):
    """
    Devuelve True si el campo es una dimensión según el atributo 'role' en dependency_info.
    """
    # Normaliza el nombre quitando corchetes
    def normalize(f):
        return f.replace('[', '').replace(']', '').lower()
    field_norm = normalize(field)
    for dep in worksheet.get("dependency_info", []):
        for col in dep.get("columns", []):
            name_norm = normalize(col.get("name", ""))
            caption_norm = normalize(col.get("caption", ""))
            if field_norm == name_norm or (caption_norm and field_norm == caption_norm):
                return col.get("role", "").lower() == "dimension"
    return False

def get_visual_generator_by_type(worksheet_type, worksheet):
    """
    Devuelve la función generadora de visual correspondiente según el tipo de gráfico de Tableau.
    Para 'bar', diferencia entre horizontal (bar) y vertical (column) según la ubicación de la dimensión.
    """
    if worksheet_type.lower() == "bar":
        # Si la dimensión está en Rows, es horizontal (bar)
        if worksheet.get("rows") and is_dimension(worksheet["rows"][0], worksheet):
            print("Bar horizontal detected")
            return generate_json_bar_graph
        # Si la dimensión está en Columns, es vertical (column)
        elif worksheet.get("cols") and is_dimension(worksheet["cols"][0], worksheet):
            print("Bar vertical detected")
            return generate_json_column_graph
        else:
            print("Bar type not recognized, defaulting to bar graph")
            return generate_json_bar_graph 
    # Otros tipos igual que antes
    visual_type_map = {
        "line": generate_json_line_graph,
        "pie": generate_json_pie,
        "table": generate_json_table,
    }
    return visual_type_map.get(worksheet_type.lower(), generate_json_table)

#Función para gráfico de columnas
def generate_json_column_graph(
    extracted_data, name,
    position_X=50, position_Y=50, position_width=500, position_height=350, position_Z=2
):
    if (position_X, position_Y, position_width, position_height, position_Z) == (50, 50, 500, 350, 2):
        print("[DEFAULT]")
    else:
        print("[CUSTOM]")
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
    drillFilterOtherVisuals = True

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
                                        "Value": worksheet_title
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
def generate_json_bar_graph(
    extracted_data, name,
    position_X=50, position_Y=50, position_width=500, position_height=350, position_Z=2
):
    if (position_X, position_Y, position_width, position_height, position_Z) == (50, 50, 500, 350, 2):
        print("[DEFAULT]")
    else:
        print("[CUSTOM]")
        print(f"Custom position: X={position_X}, Y={position_Y}, Width={position_width}, Height={position_height}, Z={position_Z}")
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
    drillFilterOtherVisuals = True

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
                                        "Value": worksheet_title
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

#Función para gráfico de torta
def generate_json_pie(
    extracted_data, name,
    position_X=50, position_Y=50, position_width=400, position_height=400, position_Z=2
):
    if (position_X, position_Y, position_width, position_height, position_Z) == (50, 50, 400, 400, 2):
        print("[DEFAULT]")
    else:
        print("[CUSTOM]")
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
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": worksheet_title
                                    }
                                }
                            }
                        }
                    }
                ]
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
def generate_json_table(
    extracted_data, name,
    position_X=50, position_Y=50, position_width=600, position_height=300, position_Z=2, tabOrder=2
):
    if (position_X, position_Y, position_width, position_height, position_Z) == (50, 50, 600, 300, 2):
        print("[DEFAULT]")
    else:
        print("[CUSTOM]")
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_title = worksheet["worksheet_title"]
    worksheet_relation = worksheet["worksheet_datasources"][0].get('caption', '')
    worksheet_cols = worksheet.get("cols") or [col["name"].strip("[]") for col in worksheet.get("dependency_info", [{}])[0].get("columns", [])] or ["ColumnaDefault"]

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
            "drillFilterOtherVisuals": True,
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": worksheet_title
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        },
        "filterConfig": {
            "filters": filters
        }
    }
    return data

#Función para gráfico de línea
def generate_json_line_graph(
    extracted_data, name,
    position_X=50, position_Y=50, position_width=600, position_height=350, position_Z=2
):
    if (position_X, position_Y, position_width, position_height, position_Z) == (50, 50, 600, 350, 2):
        print("[DEFAULT]")
    else:
        print("[CUSTOM]")
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
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": worksheet_title
                                    }
                                }
                            }
                        }
                    }
                ]
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