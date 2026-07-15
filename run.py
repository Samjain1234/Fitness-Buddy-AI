"""
Entry point — run Fitness Buddy AI with Uvicorn.

Usage:
    python run.py
    python run.py --port 8080 --workers 2
"""
from __future__ import annotations

import argparse

import uvicorn

from app.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fitness Buddy AI Server")
    parser.add_argument("--host", default=None, help="Bind host (default from .env)")
    parser.add_argument("--port", type=int, default=None, help="Bind port (default from .env)")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")
    return parser.parse_args()


def main() -> None:
    settings = get_settings()
    args = parse_args()

    host = args.host or settings.host
    port = args.port or settings.port
    workers = args.workers or settings.workers
    reload = args.reload or settings.debug

    print(
        f"\n"
        f"  🏋️  Fitness Buddy AI\n"
        f"  ─────────────────────────────────────\n"
        f"  🌐  http://{host}:{port}\n"
        f"  📖  Docs: http://{host}:{port}/docs\n"
        f"  📋  ReDoc: http://{host}:{port}/redoc\n"
        f"  🔧  Env: {settings.app_env}\n"
        f"  🤖  Model: {settings.watsonx_model_id}\n"
        f"  ─────────────────────────────────────\n"
    )

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=1 if reload else workers,   # reload mode requires 1 worker
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
