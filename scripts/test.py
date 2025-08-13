from json import loads
from os import popen
from time import sleep

with open("links.json", "rb") as f:
    links = loads(f.read())

for link in links:
    popen(f"uv run linkcovery links add {link['url']}")
    sleep(1)
