import discogs_client
from models import *


class DiscogsClient:
    def __init__(self):
        self.discogs_api = discogs_client.Client('lydia/0.0.0.alpha')
