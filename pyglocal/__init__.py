# pyglocal — Pythonic toolchains for the glocal constellation
"""
pyglocal — Pythonic toolchains for the glocal constellation
=============================================================
Offline-first, receipt-verified, local-first agentic tools.

Modules
-------
kabban     — Knowledge Breadbasket: sovereign local task board + CLI
fleet      — FleetWave all-in-one QR + glocal mesh protocol
ollama_cpu — Ollama CPU brain bootstrap (llama3.2:3b, no CUDA)
crypto     — SHA-256 hash-chained QR = THE_CHIP receipts
mp4_gen    — Constellation MP4 visualization (python-pptx + ffmpeg)
png_gen    — PNG generation (Pillow)
html_gen   — HTML/CSS pacelets + local fallback renderer
winsticky  — Windows Sticky Notes integration
cli        — CLI entry point (pyglocal)
"""
from pyglocal.version import __version__

__all__ = [
    "kabban", "fleet", "ollama_cpu", "crypto", "mp4_gen",
    "png_gen", "html_gen", "winsticky", "cli", "__version__",
]
