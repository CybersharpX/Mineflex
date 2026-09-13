"""Logging subsystem for Mineflex with sensitive credential redaction."""

from __future__ import annotations

import logging
import re

# Patterns that match potential secrets in log strings
REDACT_PATTERNS = [
    re.compile(
        r'(["\']?(?:password|access_token|session_token|auth_token|client_secret|token)["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])',
        re.IGNORECASE,
    ),
    re.compile(r"(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE),
]


class CredentialRedactingFilter(logging.Filter):
    """Filter that masks passwords, access tokens, and sensitive keys from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self.redact(v) if isinstance(v, str) else v for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self.redact(v) if isinstance(v, str) else v for v in record.args
                )
        return True

    @classmethod
    def redact(cls, text: str) -> str:
        for pattern in REDACT_PATTERNS:
            text = pattern.sub(r"\1[REDACTED]\3" if pattern.groups == 3 else r"\1[REDACTED]", text)
        return text


def get_logger(name: str = "mineflex") -> logging.Logger:
    """Get a configured logger for Mineflex."""
    logger = logging.getLogger(name)
    if not any(isinstance(f, CredentialRedactingFilter) for f in logger.filters):
        logger.addFilter(CredentialRedactingFilter())
    return logger


# Pre-configured namespace loggers
logger = get_logger("mineflex")
protocol_logger = get_logger("mineflex.protocol")
physics_logger = get_logger("mineflex.physics")
world_logger = get_logger("mineflex.world")
entity_logger = get_logger("mineflex.entity")
inventory_logger = get_logger("mineflex.inventory")
