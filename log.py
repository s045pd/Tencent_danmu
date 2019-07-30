import logging

from termcolor import colored

from conf import conf


def makeStatus():
    return f"🏠:{colored(conf.status['total'],'blue')} 🌀:{colored(conf.status['fetching'],'blue')} ✅:{colored(conf.status['success'],'green')} 🚫:{colored(conf.status['failed'],'red')}] "


logging.basicConfig(format="[%(asctime)s]%(message)s", level=logging.INFO)
Loger = logging.getLogger(conf.name)


def info(txt):
    return Loger.info(f"{ makeStatus()} {colored(txt, 'blue')}")


def success(txt):
    return Loger.info(f"{makeStatus()} {colored(txt, 'green')}")


def warning(txt):
    return Loger.info(f"{makeStatus()} {colored(txt, 'yellow')}")


def error(txt):
    return Loger.info(f"{makeStatus()} {colored(txt, 'red')}")
