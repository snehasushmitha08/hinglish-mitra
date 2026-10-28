from pathlib import Path
from importlib.util import find_spec

package = find_spec("ai4bharat.transliteration")
package_dir = Path(next(iter(package.submodule_search_locations)))
target = package_dir / "transformer" / "base_engine.py"

old = "from urduhack import normalize as shahmukhi_normalize"

new = """# Compatibility fix: import UrduHack only when needed.
def shahmukhi_normalize(*args, **kwargs):
    from urduhack import normalize
    return normalize(*args, **kwargs)
"""

text = target.read_text(encoding="utf-8")

if old not in text:
    raise SystemExit("Expected import not found. No files changed.")

backup = target.with_suffix(".py.bak")
if not backup.exists():
    backup.write_text(text, encoding="utf-8")

target.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Patch applied. Original file backed up at:", backup)