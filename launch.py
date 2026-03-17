"""
launch.py — CYRUS launcher
Run:  py -3.10 launch.py
"""
import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

from ui.hud import main
if __name__ == "__main__":
    main()
