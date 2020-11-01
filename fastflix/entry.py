# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
import logging
import traceback
import sys

try:
    import coloredlogs
    import requests
    import reusables
    from appdirs import user_data_dir
    from box import Box
    from qtpy import API, QT_VERSION, QtCore, QtGui, QtWidgets

    from fastflix.shared import (
        allow_sleep_mode,
        base_path,
        error_message,
        file_date,
        latest_fastflix,
        latest_ffmpeg,
        message,
        prevent_sleep_mode,
    )
    from fastflix.version import __version__
    from fastflix.models.fastflix import FastFlix
    from fastflix.models.config import Config
    from fastflix.conversion_worker import converter
    from fastflix.application import start_app

except ImportError as err:
    traceback.print_exc()
    print("Could not load FastFlix properly!", file=sys.stderr)
    input("Please report this issue on https://github.com/cdgriffith/FastFlix/issues (press any key to exit)")
    sys.exit(1)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("fastflix-core")
    coloredlogs.install(level="DEBUG", logger=logger)
    logger.info(f"Starting FastFlix {__version__}")

    fastflix = FastFlix()
    fastflix.config = Config()

    fastflix.worker_queue = Queue()
    fastflix.status_queue = Queue()
    fastflix.log_queue = Queue()

    gui_proc = Process(target=start_app, args=(fastflix,))
    gui_proc.start()
    converter(gui_proc, fastflix)