Tools=[
    {
        "type": "function",
        "function": {
            "name": "getSites",
            "description": "Zeigt die verfügbaren Standorte mit Informationen wie 'siteCd', 'Adresse', 'Telefonnummer', 'Öffnungszeiten' usw.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getProducts",
            "description": "Listet alle verfügbaren Dienstleistungen eines Salons auf mit jeweiligem Namen 'onlineNm' und Beschreibung 'onlineHint'",
            "parameters": {
                "type": "object",
                "properties": {
                    "siteCd": {
                        "type": "string",
                        "description": "Der 'siteCd' des jeweiligen Salons aus *getSites*"
                    }
                },
                "required": ["siteCd"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getEmployees",
            "description": "Hier bekommst du eine Liste der verfügbaren Mitarbeiter für eine, oder mehrere Dienstleistungen in einem bestimmten Zeitraum. Erforderliche Parameter sind 'siteCd', 'week' und 'items'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "siteCd": {
                        "type": "string",
                        "description": "Der 'siteCd' des jeweiligen Salons aus *getSites*"
                    },
                    "week": {
                        "type": "integer",
                        "description": "Die gewünschte Woche (0 = die aktuelle Woche, 1 = die folgende Woche, 2 = die übernächste Woche, usw.)."
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Ein Array mit den 'itemNo'-Werten aus *getProducts* (z. B. [\"14\"])."
                    }
                },
                "required": ["siteCd", "week", "items"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "AppointmentSuggestion",
            "description": "Zeigt freie Termin-Slots in einer bestimmten Woche für eine oder mehrere Dienstleistungen an. In 'positions' kannst du für jeden Service den 'itemNo' angeben und optional den 'employeeId', falls ein bestimmter Mitarbeiter gewünscht wird. Optional kann mit 'dateSearchString' nach einem bestimmten Datum oder Datumsteil im 'beginTs' der Vorschläge gefiltert werden (z.B. '21T' oder '2025-05-21').",
            "parameters": {
                "type": "object",
                "properties": {
                    "siteCd": {
                        "type": "string",
                        "description": "Der 'siteCd' des jeweiligen Salons aus *getSites*"
                    },
                    "week": {
                        "type": "integer",
                        "description": "Die gewünschte Woche (0 = aktuelle Woche, 1 = nächste Woche, usw.)."
                    },
                    "positions": {
                        "type": "array",
                        "description": "Ein Array von Objekten, in denen für jeden Service der 'itemNo' (Pflicht) und optional der 'employeeId' angegeben wird.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "itemNo": {
                                    "type": "integer",
                                    "description": "Die 'itemNo' der gewünschten Dienstleistung aus *getProducts*."
                                },
                                "employeeId": {
                                    "type": "integer",
                                    "description": "Optional: Die 'employeeId' des gewünschten Mitarbeiters aus *getEmployees*."
                                }
                            },
                            "required": ["itemNo"]
                        }
                    },
                    "dateSearchString": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Optional: Ein Array von Strings, um Terminvorschläge serverseitig nach bestimmten Tagen zu filtern. Wird in Kombination mit dem 'week'-Parameter verwendet. Formatiere die Tages-Strings als \"TTT\" (z.B. [\"02T\"] für den 2. Tag des Monats, oder [\"14T\", \"15T\"] für den 14. und 15. Tag). Wenn angegeben, werden nur Termine zurückgeliefert, deren 'beginTs' mindestens einem der Tages-Strings entspricht."
                    }
                },
                "required": ["siteCd", "week", "positions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bookAppointment",
            "description": "Bucht einen Termin oder mehrere Termine in einem Rutsch und nutzt dafür exakt die Positionen des ausgewählen *AppointmentSuggestion*.",
            "parameters": {
                "type": "object",
                "properties": {
                    "siteCd": {
                        "type": "string",
                        "description": "Der 'siteCd' des jeweiligen Salons aus *getSites*"
                    },
                    "reminderSms": {
                        "type": "boolean",
                        "description": "Ob eine SMS-Erinnerung gesendet werden soll."
                    },
                    "reminderEmail": {
                        "type": "boolean",
                        "description": "Ob eine E-Mail-Erinnerung gesendet werden soll."
                    },
                    "positions": {
                        "type": "array",
                        "description": "Ein Array der Buchungspositionen aus *AppointmentSuggestion*. Jede Position entspricht einer Dienstleistung und enthält die folgenden Felder:",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ordinalPosition": {
                                    "type": "integer",
                                    "description": "Die Reihenfolge der Dienstleistung im Termin (z. B. 1 für den ersten Service, 2 für den zweiten Service, etc.)."
                                },
                                "beginTs": {
                                    "type": "string",
                                    "description": "Startzeit (UTC) im ISO-8601-Format, z. B. YYYY-MM-DDTHH:MM:SS.000Z."
                                },
                                "durationMillis": {
                                    "type": "integer",
                                    "description": "Dauer der Dienstleistung in Millisekunden (z. B. 2700000 für 45 Minuten)."
                                },
                                "employeeId": {
                                    "type": "integer",
                                    "description": "'employeeId' aus *AppointmentSuggestion*. Darf niemals null, oder leer sein."
                                },
                                "itemNo": {
                                    "type": "integer",
                                    "description": "'itemNo' aus *getProducts*."
                                },
                                "itemNm": {
                                    "type": "string",
                                    "description": "Name der Dienstleistung (z. B. 'Waschen, Schneiden, Styling')."
                                }
                            },
                            "required": ["ordinalPosition", "beginTs", "durationMillis", "employeeId", "itemNo", "itemNm"]
                        }
                    }
                },
                "required": ["siteCd", "reminderSms", "reminderEmail", "positions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancelAppointment",
            "description": "Storniert einen bestehenden Termin mithilfe der 'orderId' aus *getOrders*.",
            "parameters": {
                "type": "object",
                "properties": {
                    "orderId": {
                        "type": "integer",
                        "description": "Die 'orderId' des zu stornierenden Termins aus *getOrders*."
                    },
                    "siteCd": {
                        "type": "string",
                        "description": "Der 'siteCd' des jeweiligen Salons aus *getSites*"
                    }
                },
                "required": ["siteCd", "orderId"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getProfile",
            "description": "Ruft das Profil des aktuellen Nutzers ab. Liefert 'Vorname', 'Nachname', 'Geschlecht', 'Email' und weitere Infos.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getOrders",
            "description": "Holt sich eine Liste von offenen Orders des Users inklusive der 'orderId'",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_profile",
            "description": "Legt ein neues Profil an oder aktualisiert bestehende Felder (z. B. 'Name', 'Geschlecht', 'E-Mail'). Das einzige Pflichtfeld bei der Erstellung ist 'fullNm', aber du kannst aus dem 'fullNm' auch 'firstNm', 'lastNm' und 'gender' auffüllen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fullNm": {
                        "type": "string",
                        "description": "Vor- und Nachname (Pflichtfeld). Beispiel: 'Max Mustermann', kann aber auch einfach nur der Vor- oder Nachname sein."
                    },
                    "email": {
                        "type": "string",
                        "description": "E-Mail-Adresse des Nutzers."
                    },
                    "title": {
                        "type": "string",
                        "description": "Titel des Nutzers."
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["M", "F", "D"],
                        "description": "Geschlecht des Nutzers (M, F oder D)."
                    },
                    "first_name": {
                        "type": "string",
                        "description": "Vorname des Nutzers."
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Nachname des Nutzers."
                    },
                    "dplAccepted": {
                        "type": "integer",
                        "description": "DSGVO Zustimmung - 0 = nein ; 1 = Ja"
                    }
                },
                "required": ["fullNm"]
            }
        }
    }
]