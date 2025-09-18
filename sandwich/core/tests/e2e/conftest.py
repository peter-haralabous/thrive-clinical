import logging
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from django.core.management import call_command

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def live_server_with_assets(live_server):
    """
    A custom fixture that builds frontend assets and collects static files
    before the live_server (and Playwright tests) run.
    """
    # 1. Find the yarn executable
    yarn_executable = shutil.which("yarn")
    if not yarn_executable:
        message = "yarn executable not found."
        raise RuntimeError(message)

    # 2. Change to project root directory (where package.json is located)
    project_root = Path(__file__).parent.parent.parent
    original_cwd = Path.cwd()

    try:
        os.chdir(project_root)

        # 3. Run yarn install and build
        # The `check=True` flag will raise an exception if the command fails.
        logger.info("Installing dependencies with yarn")

        subprocess.run([yarn_executable, "install"], check=True)  # noqa: S603
        logger.info("Building frontend assets")

        subprocess.run([yarn_executable, "run", "build"], check=True)  # noqa: S603
        logger.info("Frontend assets built successfully")

    finally:
        # Always restore the original working directory
        os.chdir(original_cwd)

    # 4. Run Django's collectstatic
    logger.info("Collecting static files")
    call_command("collectstatic", "--noinput")
    logger.info("Static files collected")

    # The original live_server fixture will now start, serving the newly
    # collected static files. We just return its value.
    return live_server
