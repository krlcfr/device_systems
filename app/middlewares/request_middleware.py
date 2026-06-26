"""
Middleware personalizado para device_systems API.

Proporciona:
- Medición de tiempo de respuesta (X-Process-Time)
- Correlation ID por petición (X-Request-ID)
- Cabecera X-App-Name: device_systems
- Logging estructurado de método, ruta y código de estado
"""

import time
import uuid
import logging
from typing import Callable, Awaitable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("device_systems")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que captura cada petición entrante y:
    - Asigna un X-Request-ID único (o propaga el existente)
    - Mide el tiempo de procesamiento
    - Agrega X-Process-Time y X-App-Name a la respuesta
    - Registra en log: método, ruta, código de estado y duración
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # --- Correlation ID ---
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4().hex[:12])

        # Tiempo de inicio
        start_time = time.perf_counter()

        # Ejecutar la ruta
        response: Response = await call_next(request)

        # Tiempo transcurrido
        process_time = time.perf_counter() - start_time

        # Cabeceras de respuesta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-App-Name"] = "device_systems"

        # Logging estructurado
        extra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_s": round(process_time, 4),
        }
        logger.info(
            "%s %s -> %d (%.4fs)",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            extra=extra,
        )

        return response
