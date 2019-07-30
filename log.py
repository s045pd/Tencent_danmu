import logging

from termcolor import colored

from conf import config


def makeStatus():
    return f"🏠:{colored(config.status['total'],'blue')} 🌀:{colored(config.status['fetching'],'blue')} ✅:{colored(config.status['success'],'green')} 🚫:{colored(config.status['failed'],'red')}] "


logging.basicConfig(format="[%(asctime)s]%(message)s", level=logging.INFO)
Loger = logging.getLogger(config.name)


def info(txt):
    return Loger.info(f"{ makeStatus()} {colored(txt, 'blue')}")


def success(txt):
    return Loger.info(f"{makeStatus()} {colored(txt, 'green')}")


def warning(txt):
    return Loger.info(f"{makeStatus()} {colored(txt, 'yellow')}")


def error(txt):
    return Loger.info(f"{makeStatus()} {colored(txt, 'red')}")
