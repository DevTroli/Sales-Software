"""
Middleware e view para manter a conexão com o Neon "quente".

O Neon suspende o compute após `suspend_timeout_seconds` de inatividade.
Em serverless (Vercel), cada cold start do DB custa 3-5 segundos.

Este módlo:
1. Health check endpoint (/health/) — usado por Vercel Cron para manter o DB acordado
2. Middleware que faz um ping leve ao DB a cada request se o DB estiver hibernando
"""
import time
import logging
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Timestamp da última vez que o DB respondeu rápido
_last_db_ping = 0.0
# Intervalo mínimo entre pings (evita ping em CADA request)
_PING_INTERVAL_SECONDS = 30


def health_check(request):
    """
    Endpoint leve que faz um SELECT 1 no banco.
    Usado como Vercel Cron Job para manter o Neon acordado.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return JsonResponse({"status": "ok", "db": "connected"}, status=200)
    except Exception as e:
        logger.error("Health check DB failed: %s", e)
        return JsonResponse({"status": "error", "db": "disconnected", "detail": str(e)}, status=503)


class NeonKeepAliveMiddleware:
    """
    Middleware que faz um ping leve ao banco se ele estiver hibernando.

    Detecta cold starts do Neon medindo o tempo da primeira query.
    Se demorar > 1 segundo, loga um aviso (útil para monitorar).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _last_db_ping

        now = time.time()
        # Só faz o ping se já passou tempo suficiente desde o último
        if now - _last_db_ping > _PING_INTERVAL_SECONDS:
            try:
                start = time.monotonic()
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                elapsed = time.monotonic() - start
                _last_db_ping = time.time()

                if elapsed > 1.0:
                    logger.warning(
                        "Neon cold start detectado: %.1fs para SELECT 1 "
                        "(path=%s)",
                        elapsed, request.path,
                    )
            except Exception:
                # Se o ping falhar, deixa o request seguir — o Django
                # vai lidar com o erro de conexão normalmente
                pass

        return self.get_response(request)
