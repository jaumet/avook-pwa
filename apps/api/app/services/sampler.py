"""Preview sampler helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SamplerManifest:
    """Represents a generated sampler manifest."""

    token: str
    duration_seconds: int
    url: str


def build_sampler_manifest(token: str) -> SamplerManifest:
    """Return a placeholder sampler manifest for early development."""

    return SamplerManifest(
        token=token, duration_seconds=600, url=f"/preview/{token}.m3u8"
    )
