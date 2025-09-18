"""Entrypoint for running the Audiovook FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from . import create_app


app: FastAPI = create_app()


__all__ = ["app", "create_app"]
