"""App Factory v2 — App Factory (Layer 2).

Turns a brain spec into a complete, self-contained app workspace. The
workspace scaffolding (folders, manifests, status tracking, queue moves) is
handled by factory.py; the actual SwiftUI / Kotlin code is written by a
Claude Code worker session running inside the claimed workspace.
"""

__version__ = "2.1"
