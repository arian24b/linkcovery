from csv import DictReader
from json import JSONDecodeError, load
from urllib.parse import urlparse

from pydantic import HttpUrl, ValidationError, parse_obj_as

from linkcovery.core.database import link_service
from linkcovery.core.logger import Logger
from linkcovery.core.utils import get_description

logger = Logger(__name__)
