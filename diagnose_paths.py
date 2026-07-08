import sys
import os
from PyQt6.QtCore import QLibraryInfo

print("--- Python Info ---")
print(f"sys.executable: {sys.executable}")
print(f"sys.prefix: {sys.prefix}")
print(f"CWD: {os.getcwd()}")

print("\n--- Environment Variables ---")
for k, v in os.environ.items():
    if "QT" in k or "PYTHON" in k:
        print(f"{k}: {v}")

print("\n--- Qt Library Info ---")
try:
    print(f"PluginsPath: {QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)}")
except AttributeError:
    # Older PyQt6 might use distinct enum or method
    try:
        print(f"PluginsPath: {QLibraryInfo.location(QLibraryInfo.LibraryLocation.PluginsPath)}")
    except:
        print("Could not get PluginsPath")
