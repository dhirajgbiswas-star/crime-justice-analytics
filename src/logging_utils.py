"""Logging setup for the CSA pipeline."""

from __future__ import annotations

import logging

from src.config import LOGS_DIR, ensure_output_dirs


def get_logger(name: str = "pipeline") -> logging.Logger:
    ensure_output_dirs()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOGS_DIR / "pipeline.log")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger
