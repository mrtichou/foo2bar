from logging import *

stdout_formatter = Formatter("%(asctime)s %(levelname)s %(message)s")

stdout_handler = StreamHandler()
stdout_handler.setFormatter(stdout_formatter)
stdout_handler.setLevel(INFO)

logger = getLogger("foo2bar")
logger.addHandler(stdout_handler)