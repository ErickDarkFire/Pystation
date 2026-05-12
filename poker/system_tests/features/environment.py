import subprocess
import time
import sys
import os

def before_scenario(context, scenario):
    python_exe = sys.executable
    poker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    game_script = os.path.join(poker_dir, "poker.py")
    project_root = os.path.abspath(os.path.join(poker_dir, ".."))
    
    env = os.environ.copy()
    env["SDL_VIDEO_WINDOW_POS"] = "0,0"
    
    context.game_proc = subprocess.Popen(
        [python_exe, game_script],
        cwd=project_root,
        env=env
    )
    time.sleep(1.5)

def after_scenario(context, scenario):
    if hasattr(context, 'game_proc'):
        context.game_proc.terminate()
        try:
            context.game_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            context.game_proc.kill()