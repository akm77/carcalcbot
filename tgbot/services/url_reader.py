import logging
from enum import IntEnum
from ssl import SSLContext
from typing import Optional, Dict, Any, Union

import aiohttp
import tenacity
from aiohttp import Fingerprint
from aiohttp.typedefs import StrOrURL


class UrlReaderMode(IntEnum):
    HTML = 0
    JSON = 1


class UrlReader:
    """
    This is base class get JSON data or HTML page from various API.
    """

    def __init__(self,
                 session: Optional[aiohttp.ClientSession] = None,
                 url: Optional[StrOrURL] = None,
                 params: Optional[Dict] = None,
                 headers: Optional[Dict] = None,
                 data: Optional[Dict] = None,
                 mode: UrlReaderMode = UrlReaderMode.JSON,
                 method: str = "GET",
                 proxy: Optional[StrOrURL] = None,
                 ssl: Optional[Union[SSLContext, bool, Fingerprint]] = None,
                 logger: Optional[logging.Logger] = None,
                 **kwargs) -> None:
        self.__session = session or aiohttp.ClientSession()
        self.__url: StrOrURL = url
        self.__params = params or None
        self.__headers = headers or None
        self.__data = data or None
        self.__mode = mode
        self.__method = method
        self.__response_status = 0
        self.__response_url: StrOrURL = ''
        self.__proxy = proxy
        self.__ssl = ssl
        self.__logger = logger or logging.getLogger(self.__class__.__module__)
        self.__result = None

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, session: aiohttp.ClientSession):
        self.__session = session

    @property
    def url(self) -> StrOrURL:
        return self.__url

    @url.setter
    def url(self, url: StrOrURL):
        self.__url = url

    @property
    def params(self) -> Dict:
        return self.__params

    @params.setter
    def params(self, params: Dict):
        self.__params = params

    @property
    def headers(self) -> Dict:
        return self.__headers

    @headers.setter
    def headers(self, headers: Dict):
        self.__headers = headers

    @property
    def data(self) -> Dict:
        return self.__data

    @data.setter
    def data(self, data: Dict):
        self.__data = data

    @property
    def status(self):
        return self.__response_status

    @property
    def response_url(self) -> StrOrURL:
        return self.__response_url

    @property
    def logger(self):
        return self.__logger

    @tenacity.retry(stop=tenacity.stop_after_attempt(6), wait=tenacity.wait_random(min=0.2, max=0.5),
                    after=tenacity.after_log(logging.getLogger(__name__), logging.ERROR))
    async def get_raw_data(self) -> Optional[Dict[str, Any] | str]:
        """
        :return JSON Result:
        """
        if not self.url:
            self.__logger.error("Url can not be None.")
            raise ValueError("Url can not be None.")
        self.__result = None
        method = self.session.get if self.__method == "GET" else self.session.post
        async with method(url=self.url,
                          params=self.params,
                          headers=self.headers,
                          json=self.data,
                          proxy=self.__proxy,
                          ssl=self.__ssl) as response:
            self.__response_url = response.url
            self.__response_status = response.status
            self.__result = await response.json(encoding='utf-8') \
                if self.__mode == UrlReaderMode.JSON else await response.text()
        return self.__result
