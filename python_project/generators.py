from utils import generar_hex_metodo

def get_visual_generator_by_type(worksheet_type):
    """
    Devuelve la función generadora de visual correspondiente según el tipo de gráfico de Tableau.
    """
    visual_type_map = {
        "bar": generate_json_bar_graph,
        "column": generate_json_column_graph,
        "line": generate_json_line_graph,
        "pie": generate_json_pie,
        "table": generate_json_table,
    }
    # Por defecto, si no se reconoce el tipo, usa tabla
    return visual_type_map.get(worksheet_type.lower(), generate_json_table)


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
def generate_json_pie(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo torta (pieChart) con categoría y valor.
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
def generate_json_table(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo tabla (tableEx) con todas las columnas del worksheet,
    respetando el orden y la estructura del ejemplo dado.
    """
    worksheet_data = extracted_data[0]
    worksheet = worksheet_data["worksheet"]
    worksheet_title = worksheet["worksheet_title"]
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
def generate_json_line_graph(extracted_data, name):
    """
    Genera la estructura JSON para un visual de Power BI tipo línea (lineChart) con solo la columna de fecha en el eje X y filtros simples.
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