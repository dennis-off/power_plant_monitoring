# -*- coding: utf-8 -*-
"""A module to read weather forecast.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""
import json
import logging
import random
import string
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import confuse
import requests
from requests.structures import CaseInsensitiveDict

_logger = logging.getLogger(__name__)

@dataclass
class WeatherInfo:
    """A class to store a binance announcement."""

    #: timestamp (int): The timestamp of this announcement
    timestamp: int
    #: id (int): The unique id of an announcement
    id: int
    #: title (str): The title of an announcement
    title: str

    @classmethod
    def from_dict(cls, data: dict) -> "WeatherInfo":
        return cls(
            timestamp=int(data["releaseDate"]), id=int(data["id"]), title=data["title"]
        )


class WeatherForecastReader(ABC):
    def __init__(self, config: confuse.ConfigView):

        #: ...
        self._config: confuse.ConfigView = config
        #: ...
        self._verbosity: int = 4


class BasfWeatherForecast(AnnouncementReader):
    def __init__(self, config: confuse.ConfigView):
        """
        ...
        """

        AnnouncementReader.__init__(self, config)

        # set typename
        self._typename = "BAPI"
        #: ...
        self._url = config["url"].get(str)
        #: ...
        self._avoid_chached_date = True

    def _get_announcements_internal(
        self, number_of_announcements: int, session: requests.Session = None
    ) -> list["AnnouncementInfo"]:

        # get the latest announcement
        with self._lock:
            number_of_announcements = number_of_announcements + self._offset

            assert (
                number_of_announcements <= 200
            ), "Number of announcements exceeds limits (< 200)"

            # Generate random query/params to help prevent caching
            rand_page = random.randint(number_of_announcements, 200)
            letters = string.ascii_letters
            random_string = "".join(
                random.choice(letters) for i in range(random.randint(10, 20))
            )
            random_number = random.randint(1, 99999999999999999999)
            queries = [
                "catalogId=48",
                "pageNo=1",
                f"pageSize={str(rand_page)}",
                f"rnd={str(time.time())}",
                f"{random_string}={str(random_number)}",
            ]
            random.shuffle(queries)
            request_url = f"{self._url}?{queries[0]}&{queries[1]}&{queries[2]}&{queries[3]}&{queries[4]}"

            headers = CaseInsensitiveDict()

            headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, proxy-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"
            headers["max-age"] = "2"

            if self._verbosity > 3:
                _logger.debug(f"Query = {request_url}")

            if session is None:
                response = requests.get(request_url, headers=headers, timeout=3)
            else:
                response = session.get(request_url, headers=headers, timeout=3)

            self._cached = False
            self._page_size = rand_page
            self._request_command = request_url

            # log caching behavior
            if self._verbosity > 3:
                age_log_msg = ""
                if "Age" in response.headers.keys():
                    age_log_msg = f", Age = {response.headers['Age']}"
                _logger.debug(
                    f"Date = {response.headers['Date']}, X-Cache = {response.headers['X-Cache']}{age_log_msg}"
                )

            substrings = ["Hit", "Error"]
            cache_value = response.headers["X-Cache"]
            is_cached_or_error = any(
                [substring in cache_value for substring in substrings]
            )

            if is_cached_or_error:
                self._cached = True
                _logger.debug(f"X-Cache: {cache_value}")

            announcements = response.json()["data"]["articles"]

        return list(map(lambda item: AnnouncementInfo.from_dict(item), announcements))[
            self._offset : self._offset + number_of_announcements - self._offset
        ]


class BinanceReaderZhGateway(AnnouncementReader):
    def __init__(self, config: confuse.ConfigView):
        """
        ...
        """

        AnnouncementReader.__init__(self, config)

        # set typename
        self._typename = "GTZH"
        #: ...
        self._url = config["url"].get(str)
        #: ...
        self._avoid_chached_date = True

    def _get_announcements_internal(
        self, number_of_announcements: int, session: requests.Session = None
    ) -> list["AnnouncementInfo"]:

        # get the latest announcement
        with self._lock:
            number_of_announcements = number_of_announcements + self._offset

            assert (
                number_of_announcements <= 200
            ), "Number of announcements exceeds limits (< 200)"

            # Generate random query/params to help prevent caching
            # rand_page = random.randint(number_of_announcements, 200)
            # letters = string.ascii_letters
            # random_string = "".join(
            #    random.choice(letters) for i in range(random.randint(10, 20))
            # )
            # random_number = random.randint(1, 99999999999999999999)
            # queries = [
            #    "type=1",
            #    "catalogId=48",
            #    "pageNo=1",
            #    f"pageSize={str(rand_page)}",
            #    f"rnd={str(time.time())}",
            #    f"{random_string}={str(random_number)}",
            # ]
            # random.shuffle(queries)
            # domains = ["com", "ac", "be", "cz", "in", "io", "jp", "sh"]
            # domain = random.choice(domains)
            # request_url = f"{self._url.replace('$DOMAIN', domain)}?{queries[0]}&{queries[1]}&{queries[2]}&{queries[3]}&{queries[4]}&{queries[5]}"  # noqa

            rand_page = 137
            queries = [
                "type=1",
                "catalogId=48",
                "pageNo=1",
                f"pageSize={str(rand_page)}",
            ]
            domains = ["com", "ac", "be", "cz", "in", "io", "jp", "sh"]
            domain = random.choice(domains)
            request_url = f"{self._url.replace('$DOMAIN', domain)}?{queries[0]}&{queries[1]}&{queries[2]}&{queries[3]}"  # noqa

            headers = CaseInsensitiveDict()

            headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, proxy-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"
            headers["max-age"] = "2"

            if self._verbosity > 3:
                _logger.debug(f"Query = {request_url}")

            if session is None:
                response = requests.get(request_url, headers=headers, timeout=3)
            else:
                response = session.get(request_url, headers=headers, timeout=3)

            self._cached = False
            self._page_size = rand_page
            self._request_command = request_url

            try:
                _logger.debug(f'X-Cache: {response.headers["X-Cache"]}')
                self._cached = True
            except KeyError:
                # No X-Cache header was found - great news, we're hitting the source.
                pass

            announcements = response.json()["data"]["catalogs"][0]["articles"]

            return list(
                map(lambda item: AnnouncementInfo.from_dict(item), announcements)
            )[self._offset : self._offset + number_of_announcements - self._offset]


class BinanceReaderGateway(AnnouncementReader):
    def __init__(self, config: confuse.ConfigView):
        """
        ...
        """

        AnnouncementReader.__init__(self, config)

        # set typename
        self._typename = "GTCO"
        #: ...
        self._url = config["url"].get(str)
        #: ...
        self._avoid_chached_date = True

    def _get_announcements_internal(
        self, number_of_announcements: int, session: requests.Session = None
    ) -> list["AnnouncementInfo"]:

        # get the latest announcement
        with self._lock:
            number_of_announcements = number_of_announcements + self._offset

            assert (
                number_of_announcements <= 200
            ), "Number of announcements exceeds limits (< 200)"

            # Generate random query/params to help prevent caching
            rand_page = random.randint(number_of_announcements, 200)
            letters = string.ascii_letters
            random_string = "".join(
                random.choice(letters) for i in range(random.randint(10, 20))
            )
            random_number = random.randint(1, 99999999999999999999)
            queries = [
                "type=1",
                "catalogId=48",
                "pageNo=1",
                f"pageSize={str(rand_page)}",
                f"rnd={str(time.time())}",
                f"{random_string}={str(random_number)}",
            ]
            random.shuffle(queries)

            request_url = f"{self._url}?{queries[0]}&{queries[1]}&{queries[2]}&{queries[3]}&{queries[4]}&{queries[5]}"

            headers = CaseInsensitiveDict()

            headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, proxy-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"
            headers["max-age"] = "2"

            if self._verbosity > 3:
                _logger.debug(f"Query = {request_url}")

            if session is None:
                response = requests.get(request_url, headers=headers, timeout=3)
            else:
                response = session.get(request_url, headers=headers, timeout=3)

            self._cached = False
            self._page_size = rand_page
            self._request_command = request_url

            # log caching behavior
            if self._verbosity > 3:
                age_log_msg = ""
                if "Age" in response.headers.keys():
                    age_log_msg = f", Age = {response.headers['Age']}"
                _logger.debug(
                    f"Date = {response.headers['Date']}, X-Cache = {response.headers['X-Cache']}{age_log_msg}"
                )

            substrings = ["Hit", "Error"]
            cache_value = response.headers["X-Cache"]
            is_cached_or_error = any(
                [substring in cache_value for substring in substrings]
            )

            if is_cached_or_error:
                self._cached = True
                _logger.debug(f"X-Cache: {cache_value}")

            announcements = response.json()["data"]["catalogs"][0]["articles"]

            return list(
                map(lambda item: AnnouncementInfo.from_dict(item), announcements)
            )[self._offset : self._offset + number_of_announcements - self._offset]


class JsonReader(AnnouncementReader):
    def __init__(self, config: confuse.ConfigView):
        """
        ...
        """

        AnnouncementReader.__init__(self, config)

        # set typename
        self._typename = "JSON"
        #: ...
        self._filename: str = config["filename"].get(str)

    def _get_announcements_internal(
        self, number_of_announcements: int, session: requests.Session = None
    ) -> list["AnnouncementInfo"]:

        with open(self._filename, "r+") as f:
            announcements = json.load(f)

        return list(map(lambda item: AnnouncementInfo.from_dict(item), announcements))[
            self._offset : self._offset + number_of_announcements
        ]


def create_reader_by_name(class_name_snake_case: str, config: confuse.ConfigView):
    def _get_class_name(module_name):
        """Build a class Name (CamelCase) from the module name

        @type (str) -> str
        @param module_name   \b str   The name of the python module (snake_case)
        @return              \b str   The Class name in CamelCase
        """

        words = module_name.split("_")
        return "".join(w.capitalize() for w in words).replace("_", "")

    class_name_camel_case = _get_class_name(class_name_snake_case)
    class_to_be_created = globals()[class_name_camel_case]

    return class_to_be_created(config)
