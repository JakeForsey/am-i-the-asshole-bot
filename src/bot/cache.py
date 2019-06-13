from typing import List
import os

from urllib.parse import urlparse


class FileURLCache:
    """
    Wraps a list of URLs, if a file is found for the URL then the file path
    is returned rather than the URL.
    """
    def __init__(self, directory: str, urls: List[str]):
        self._directory = directory
        self._urls = urls

        self._current_idx = 0

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._urls)

    def __next__(self):
        if self._current_idx > len(self._urls):
            raise StopIteration

        else:
            self._current_idx += 1
            return self._url_or_file(self._urls[self._current_idx - 1])

    def _url_or_file(self, url: str):
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

        if file_name in os.listdir(self._directory):
            return os.path.join(self._directory, file_name)
        else:
            return url
