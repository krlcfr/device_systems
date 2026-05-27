Reto Integrador – API REST de Usuarios para device_systems
Objetivo del reto
Construir una API REST funcional para administrar usuarios del sistema device_systems,
aplicando validaciones, modelos de entrada/salida, parámetros de ruta, parámetros de consulta y
respuestas HTTP estructuradas.
Instrucciones para el desarrollo de la actividad

Fase 1 – Configuración del proyecto
Crear un proyecto llamado:
device_systems

Estructura sugerida:
device_systems/
│── app/
│ │── main.py
│ │── schemas/
│ │ │── user_schema.py
│ │── routes/
│ │ │── user_routes.py
│── requirements.txt o pyproject.toml(si usas uv)
│── README.md


Fase 2 – Modelo de usuario con Pydantic
Crear modelos para validar los datos del usuario.

Campos mínimos:
• id
• name
• email
• role
• is_active

Validaciones sugeridas:
• name: obligatorio, mínimo 3 caracteres.
• email: formato válido.
• role: valores permitidos: admin, support, user.
• is_active: valor booleano.

Fase 3 – Endpoints GET

Implementar endpoints para:
GET /users
GET /users/{user_id}
GET /users?role=admin
GET /users?is_active=true

Estos endpoints deben permitir:
• Listar todos los usuarios.
• Consultar un usuario por ID usando Path Parameter.
• Filtrar usuarios por rol usando Query Parameter.
• Filtrar usuarios por estado activo/inactivo.

Fase 4 – Endpoints POST

Implementar el endpoint:
POST /users

Debe permitir:
• Registrar un nuevo usuario.
• Validar los datos de entrada con Pydantic.
• Evitar correos duplicados.
• Retornar el usuario creado con un response_model.

Fase 5 – Response Models y cabeceras HTTP
Implementar modelos de respuesta para:
• Ocultar datos no necesarios.

• Estandarizar la respuesta del API.
• Retornar cabeceras personalizadas, por ejemplo:
X-App-Name: device_systems
X-API-Version: 1.0

Fase 6 – Documentación y pruebas
Probar la API usando:
• Swagger UI
• Postman
• Thunder Client

Documentar en el README.md:
• Descripción de la aplicación device_systems.
• Instalación de dependencias.
• Ejecución del servidor.
• Tabla de endpoints.
• Ejemplos de peticiones GET y POST.
• Capturas de Swagger UI.

Ambiente requerido
• Computador con Python instalado.
• Editor de código Visual Studio Code o similar.
• FastAPI y Uvicorn.
• Git y GitHub.
• Cliente HTTP: Postman o Thunder Client.

Estrategias o técnicas didácticas activas
• Aprendizaje basado en retos.
• Desarrollo incremental de APIs REST.
• Resolución de problemas prácticos.
• Validación de datos con modelos.
• Pruebas funcionales mediante Swagger UI.

Materiales de formación
• Introducción a FastAPI.
• Instalación de FastAPI y configuración.
• Métodos GET.
• Métodos POST.
• Path Parameters y Query Parameters.
• Validación de datos con Pydantic 2.
• Cabeceras HTTP y Response Models.

Link Materiales: https://educated-show-144.notion.site/Guia-de-aprendizaje-Material-de-apoyo-
2414671e02a180eebe92d827e2f7c8d1

Evidencias de aprendizaje

Repositorio individual en GitHub con:
• Proyecto device_systems funcional.
• Recurso users implementado.
• Endpoints GET y POST.
• Validaciones con Pydantic.
• Response Models.
• Cabeceras HTTP personalizadas.
• README.md documentado.

Documento README.md con:
• Capturas de Swagger UI.
• Evidencia de pruebas GET /users.
• Evidencia de pruebas GET /users/{user_id}.
• Evidencia de pruebas POST /users.
• Evidencia de validaciones y errores.
• Reflexión sobre el uso de FastAPI para construir APIs REST.