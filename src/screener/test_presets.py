import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from engine import run_preset, PRESETS

for name in PRESETS:
    result = run_preset(name)
    print(f"{name}: {len(result)} companies")