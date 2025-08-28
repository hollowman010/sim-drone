# Thin launcher that delegates to your existing src/main.py
import importlib
import sys

def main():
    mod = importlib.import_module("src.main")
    # Prefer a callable main() if present; otherwise just importing may already run code
    if hasattr(mod, "main") and callable(mod.main):
        return mod.main()
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
