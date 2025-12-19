from misc.patch_unified_planning_default_values import main as patch_unified_planning_default_values
from misc.patch_scrollableFrame import main as patch_scrollableFrame

import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv)>1:
        venv_path = Path(sys.argv[1])
        assert venv_path.exists()
    else:
        venv_path = Path() / 'env_cai'
        assert venv_path.exists()

    patch_unified_planning_default_values(venv_path)
    patch_scrollableFrame(venv_path)