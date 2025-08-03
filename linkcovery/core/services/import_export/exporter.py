from csv import DictWriter
from json import dump

from rich.progress import track

from linkcovery.core.database import link_service
from linkcovery.core.logger import Logger

logger = Logger(__name__)
