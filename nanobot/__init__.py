"""
nanobot - A lightweight AI agent framework
"""

__version__ = "0.1.0"

# Use text logo on Windows to avoid Unicode encoding issues
import sys
if sys.platform == "win32":
    __logo__ = "[nanobot]"
else:
    __logo__ = "🐈"
