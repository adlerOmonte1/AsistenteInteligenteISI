/*
 * Modelo C4 del Asistente Académico UDH (Structurizr DSL).
 *
 * Vista previa local:
 *   docker run -it --rm -p 8080:8080 -v "$PWD/docs/03-arquitectura/modelo-c4:/usr/local/structurizr" structurizr/lite
 *
 * Regla: cada app de backend/apps y cada proyecto o feature de frontend/projects
 * tiene aquí un elemento con la propiedad "ruta". scripts/validar_c4.py lo
 * comprueba en el CI; quien cree, renombre o borre una app o feature actualiza
 * este archivo en el mismo PR.
 */
workspace "Asistente Académico UDH" "Consulta de trámites del P.A. de Ingeniería de Sistemas e Informática." {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante" "Consulta trámites desde el portal o desde el widget insertado en otra web. No tiene cuenta."
        editor = person "Editor" "Personal administrativo que mantiene fichas, intents, pendientes y documentos."
        revisor = person "Revisor" "Coordinación del programa: aprueba o rechaza los cambios antes de publicarlos."
        centro = person "Centro de Cómputo" "Administra cuentas, configuración, despliegue y respaldos."

        llm = softwareSystem "Proveedor de LLM y embeddings" "API externa (Gemini por defecto; intercambiable por variables de entorno)." "Externo"
        webUdh = softwareSystem "Web institucional UDH" "Páginas de la universidad que pueden insertar el widget." "Externo"

        asistente = softwareSystem "Asistente Académico UDH" "Portal de consultas, asistente conversacional y panel de mantenimiento." {

            portal = container "Portal" "SPA pública: trámites, fases, documentos, buscador y asistente." "Angular 22" "Web" {
                properties {
                    "ruta" "frontend/projects/portal"
                }
                pInicio = component "Inicio" "Portada, buscador y lista de trámites." "Angular" {
                    properties {
                        "ruta" "frontend/projects/portal/src/app/features/inicio"
                    }
                }
                pTramite = component "Trámite" "Fases publicadas de un proceso y sus documentos." "Angular" {
                    properties {
                        "ruta" "frontend/projects/portal/src/app/features/tramite"
                    }
                }
                pDocumentos = component "Documentos" "Biblioteca normativa con filtros." "Angular" {
                    properties {
                        "ruta" "frontend/projects/portal/src/app/features/documentos"
                    }
                }
                pBuscar = component "Buscar" "Resultados de búsqueda en las fichas." "Angular" {
                    properties {
                        "ruta" "frontend/projects/portal/src/app/features/buscar"
                    }
                }
                pAsistente = component "Asistente" "Conversación a pantalla completa." "Angular" {
                    properties {
                        "ruta" "frontend/projects/portal/src/app/features/asistente"
                    }
                }
                pAcerca = component "Acerca" "Cómo funciona el asistente y política de privacidad." "Angular" {
                    properties {
                        "ruta" "frontend/projects/portal/src/app/features/acerca"
                    }
                }
            }

            widget = container "Widget <udh-chat>" "Web Component con Shadow DOM para insertar el chat en cualquier página." "Angular Elements" "Web" {
                properties {
                    "ruta" "frontend/projects/widget"
                }
            }

            compartida = container "Librería compartida" "Modelos del dominio, cliente SSE y componente de conversación." "Angular library" "Librería" {
                properties {
                    "ruta" "frontend/projects/shared"
                }
            }

            panel = container "Panel de administración" "SPA para mantener el conocimiento y revisar la calidad." "Angular 22" "Web" {
                properties {
                    "ruta" "frontend/projects/admin"
                }
                aAuth = component "Autenticación" "Login, guards e interceptores; access en memoria y refresh en cookie." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/auth"
                    }
                }
                aDashboard = component "Resumen" "Métricas de uso, vías, derivaciones y costo." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/dashboard"
                    }
                }
                aConocimiento = component "Conocimiento" "Fichas, editor, bandeja de revisión y subida de documentos." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/conocimiento"
                    }
                }
                aIntents = component "Intents" "Intents, ejemplos y secciones que responden." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/intents"
                    }
                }
                aPendientes = component "Pendientes" "Datos por confirmar con Coordinación." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/pendientes"
                    }
                }
                aDocumentos = component "Documentos" "Biblioteca normativa del portal." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/documentos"
                    }
                }
                aCalidad = component "Calidad" "Servicio de datos de métricas, probador, golden set y conversaciones." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/calidad"
                    }
                }
                aProbador = component "Probador" "Pregunta de prueba con traza completa." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/probador"
                    }
                }
                aEvaluacion = component "Golden set" "Ejecución y resultados de la evaluación." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/evaluacion"
                    }
                }
                aConversaciones = component "Conversaciones" "Historial anonimizado con filtros." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/conversaciones"
                    }
                }
                aUsuarios = component "Usuarios" "Cuentas, roles y facultad." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/usuarios"
                    }
                }
                aConfiguracion = component "Configuración" "Umbrales, límite de gasto y textos." "Angular" {
                    properties {
                        "ruta" "frontend/projects/admin/src/app/features/configuracion"
                    }
                }
            }

            api = container "API" "Expone /api/v1: canal del chat (SSE), portal y panel." "Python 3.12, Django 5.2, DRF" "API" {
                properties {
                    "ruta" "backend"
                }
                dialogo = component "Diálogo" "Canal /chat/, orquestador, router por confianza, límites y probador." "Django app" {
                    properties {
                        "ruta" "backend/apps/dialogo"
                    }
                }
                nlu = component "NLU" "Normalización, sinónimos, entidades y clasificador k vecinos." "Django app" {
                    properties {
                        "ruta" "backend/apps/nlu"
                    }
                }
                recuperacion = component "Recuperación" "Índice de secciones y búsqueda híbrida BM25 + pgvector." "Django app" {
                    properties {
                        "ruta" "backend/apps/recuperacion"
                    }
                }
                generacion = component "Generación" "Proveedores de LLM y embeddings, prompt RAG y control de gasto." "Django app" {
                    properties {
                        "ruta" "backend/apps/generacion"
                    }
                }
                validacion = component "Validación" "Verifica correos, montos, plazos y resoluciones contra las fichas." "Django app" {
                    properties {
                        "ruta" "backend/apps/validacion"
                    }
                }
                conocimiento = component "Conocimiento" "Catálogo, fichas con versiones, intents, pendientes, documentos, importador y publicación." "Django app" {
                    properties {
                        "ruta" "backend/apps/conocimiento"
                    }
                }
                evaluacion = component "Evaluación" "Golden set, ejecución y métricas frente a metas." "Django app" {
                    properties {
                        "ruta" "backend/apps/evaluacion"
                    }
                }
                analitica = component "Analítica" "Registro anonimizado, métricas y purga a los 12 meses." "Django app" {
                    properties {
                        "ruta" "backend/apps/analitica"
                    }
                }
                cuentas = component "Cuentas" "Usuarios administrativos, roles, JWT con refresh en cookie." "Django app" {
                    properties {
                        "ruta" "backend/apps/cuentas"
                    }
                }
                sistema = component "Sistema" "Configuración editable, salud y tareas programadas." "Django app" {
                    properties {
                        "ruta" "backend/apps/sistema"
                    }
                }
            }

            worker = container "Worker" "Indexación, prueba de humo, golden set, propuestas de fichas y purga." "django-q2 (cola en el ORM)" "Worker" {
                properties {
                    "ruta" "backend"
                }
            }

            db = container "Base de datos" "Datos, embeddings (HNSW), cola de tareas y caché." "PostgreSQL 16 + pgvector" "Base de datos"

            web = container "Servidor web" "HTTPS, archivos estáticos de las SPA y proxy a la API." "Nginx" "Infraestructura" {
                properties {
                    "ruta" "infra/nginx"
                }
            }
        }

        # Contexto
        estudiante -> asistente.portal "Consulta trámites y conversa" "HTTPS"
        estudiante -> webUdh "Navega"
        webUdh -> asistente.widget "Inserta" "<script> + <udh-chat>"
        editor -> asistente.panel "Edita conocimiento" "HTTPS"
        revisor -> asistente.panel "Aprueba o rechaza cambios" "HTTPS"
        centro -> asistente.panel "Administra cuentas y configuración" "HTTPS"

        # Contenedores
        asistente.portal -> asistente.compartida "Usa"
        asistente.widget -> asistente.compartida "Usa"
        asistente.panel -> asistente.compartida "Usa"
        asistente.web -> asistente.api "Proxy /api/" "HTTP"
        asistente.portal -> asistente.api "Lee procesos, fichas y documentos; envía mensajes" "JSON / SSE"
        asistente.widget -> asistente.api "Envía mensajes" "SSE"
        asistente.panel -> asistente.api "Gestiona conocimiento y métricas" "JSON + JWT"
        asistente.api -> asistente.db "Lee y escribe" "SQL"
        asistente.worker -> asistente.db "Toma tareas y escribe índices" "SQL"
        asistente.api -> llm "Embeddings de la pregunta; redacción RAG" "HTTPS REST"
        asistente.worker -> llm "Embeddings de secciones; propuesta de fichas" "HTTPS REST"

        # Componentes de la API
        asistente.api.dialogo -> asistente.api.nlu "Clasifica la pregunta"
        asistente.api.dialogo -> asistente.api.recuperacion "Busca secciones (vía RAG)"
        asistente.api.dialogo -> asistente.api.generacion "Redacta con las secciones"
        asistente.api.dialogo -> asistente.api.validacion "Valida datos críticos"
        asistente.api.dialogo -> asistente.api.conocimiento "Lee versiones publicadas"
        asistente.api.dialogo -> asistente.api.analitica "Registra la consulta"
        asistente.api.dialogo -> asistente.api.sistema "Lee umbrales y textos"
        asistente.api.nlu -> asistente.api.generacion "Pide embeddings"
        asistente.api.recuperacion -> asistente.api.generacion "Pide embeddings"
        asistente.api.conocimiento -> asistente.api.recuperacion "Indexa al publicar"
        asistente.api.conocimiento -> asistente.api.evaluacion "Prueba de humo"
        asistente.api.evaluacion -> asistente.api.dialogo "Ejecuta el orquestador"
        asistente.api.generacion -> asistente.api.analitica "Consulta el gasto del mes"
        asistente.api.generacion -> llm "Llama a la API" "HTTPS"
    }

    views {
        systemContext asistente "Contexto" {
            include *
            autoLayout lr
        }
        container asistente "Contenedores" {
            include *
            autoLayout lr
        }
        component asistente.api "ComponentesAPI" {
            include *
            autoLayout tb
        }
        component asistente.panel "ComponentesPanel" {
            include *
            autoLayout lr
        }
        component asistente.portal "ComponentesPortal" {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #0b3a6e
                color #ffffff
            }
            element "Software System" {
                background #0b3a6e
                color #ffffff
            }
            element "Externo" {
                background #8a94a3
                color #ffffff
            }
            element "Container" {
                background #1f5fa8
                color #ffffff
            }
            element "Base de datos" {
                shape Cylinder
            }
            element "Web" {
                shape WebBrowser
            }
            element "Component" {
                background #e7eef7
                color #1c2430
            }
        }
    }
}
