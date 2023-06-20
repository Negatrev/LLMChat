import os
import platform
from typing import Optional

import psutil


def ensure_packages_installed():
    import subprocess

    subprocess.call(
        [
            "pip",
            "install",
            "--trusted-host",
            "pypi.python.org",
            "-r",
            "requirements.txt",
        ]
    )


def set_priority(pid: Optional[int] = None, priority: str = "high"):
    """Set The Priority of a Process.  Priority is a string which can be 'low', 'below_normal',
    'normal', 'above_normal', 'high', 'realtime'. 'normal' is the default priority."""

    if platform.system() == "Windows":
        priorities = {
            "low": psutil.IDLE_PRIORITY_CLASS,
            "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
            "normal": psutil.NORMAL_PRIORITY_CLASS,
            "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
            "high": psutil.HIGH_PRIORITY_CLASS,
            "realtime": psutil.REALTIME_PRIORITY_CLASS,
        }
    else:  # Linux and other Unix systems
        priorities = {
            "low": 19,
            "below_normal": 10,
            "normal": 0,
            "above_normal": -5,
            "high": -11,
            "realtime": -20,
        }

    if pid is None:
        pid = os.getpid()
    p = psutil.Process(pid)
    p.nice(priorities[priority])


if platform.system() == "Windows":
    set_priority(priority="high")
else:
    set_priority(priority="normal")


if __name__ == "__mp_main__":
    """Option 1: Skip section for multiprocess spawning
    This section will be skipped when running in multiprocessing mode"""
    pass

elif __name__ == "__main__":
    # ensure_packages_installed()
    """Option 2: Debug mode
    Running this file directly to debug the app
    Run this section if you don't want to run app in docker"""
    from os import environ

    environ[
        "API_ENV"
    ] = "local"  # everytime you run debugging, automatically testing db will be reset
    environ["DOCKER_MODE"] = "False"

    import uvicorn

    from app.common.app_settings import create_app
    from app.common.config import config

    app = create_app(config=config)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.port,
    )
else:
    # ensure_packages_installed()
    """Option 3: Non-debug mode
    Docker will run this section as the main entrypoint
    This section will mostly be used.
    Maybe LLaMa won't work in Docker."""
    from app.common.app_settings import create_app
    from app.common.config import config

    app = create_app(config=config)
