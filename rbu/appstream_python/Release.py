from dataclasses import dataclass
from typing import Type, Literal
from ._helper import assert_func
from .Shared import Description
from lxml import etree
import collections
import datetime
import requests
import copy
import os


ReleaseType = Literal["stable", "development"]
ReleaseListType = Literal["embedded", "external"]
UrgencyType = Literal["unknown", "low", "medium", "high", "critical"]


@dataclass
class Release:
    "Represents a <release> tag"

    version: str = ""
    type: ReleaseType = "stable"
    urgency: UrgencyType = "unknown"
    date: datetime.date | None = None
    description = Description()
    date_eol: datetime.date | None = None

    def __post_init__(self) -> None:
        self.description = copy.deepcopy(self.description)

    def get_tag(self) -> etree.Element:
        """
        Returns the XML Tag

        :return: The Tag
        """
        tag = etree.Element("release")
        tag.set("type", self.type)
        tag.set("version", self.version)

        if self.urgency != "unknown":
            tag.set("urgency", self.urgency)

        if self.date is not None:
            tag.set("date", self.date.isoformat())

        if self.date_eol is not None:
            tag.set("date_eol", self.date_eol.isoformat())

        self.description.get_tags(tag)

        return tag

    @classmethod
    def from_tag(cls: Type["Release"], tag: etree._Element) -> "Release":
        "Loads a release tag"
        release = cls()

        release.version = tag.get("version", "")
        release.type = tag.get("type", "stable")
        release.urgency = tag.get("urgency", "unknown")

        try:
            release.date = datetime.datetime.fromisoformat(tag.get("date")).date()
        except Exception:
            pass

        try:
            release.date = datetime.date.fromtimestamp(int(tag.get("timestamp")))
        except Exception:
            pass

        try:
            release.date_eol = datetime.datetime.fromisoformat(tag.get("date_eol")).date()
        except Exception:
            pass

        description_tag = tag.find("description")
        if description_tag is not None:
            release.description.load_tags(description_tag)

        return release


class ReleaseList(collections.UserList[Release]):
    "Represents a list of releases"

    def __init__(self) -> None:
        super().__init__()

        self.type: ReleaseListType = "embedded"
        "The type"

        self.url: str = ""
        "The URL if external"

    def load_external_releases(self) -> None:
        "Loads the external releases from the Internet"
        if self.type != "external":
            return

        r = requests.get(self.url)

        tag = etree.fromstring(r.content)

        for single_release in tag.findall("release"):
            self.append(Release.from_tag(single_release))

    def get_tag(self) -> etree.Element:
        """
        Returns the XML Tag

        :return: The Tag
        """
        tag = etree.Element("releases")

        if self.type != "external":
            for release in self.data:
                tag.append(release.get_tag())
        else:
            tag.set("type", self.type)

        if self.url != "":
            tag.set("url", self.url)

        return tag

    def get_xml_string(self) -> str:
        """
        Returns the XML data of the ReleaseList as string

        :return: The XMl as string
        """
        return etree.tostring(self.get_tag(), pretty_print=True, encoding=str).strip()

    def save_file(self, path: str | os.PathLike) -> None:
        """Saves the Component as XML file"""
        with open(path, "wb") as f:
            f.write(etree.tostring(self.get_tag(), pretty_print=True, xml_declaration=True, encoding="utf-8"))

    @classmethod
    def from_tag(cls: Type["ReleaseList"], tag: etree._Element, fetch_external: bool = False) -> "ReleaseList":
        "Creates the list from an XMl tag"
        release_list = cls()

        release_list.type = tag.get("type", "embedded")
        release_list.url = tag.get("url", "")

        for single_release in tag.findall("release"):
            release_list.append(Release.from_tag(single_release))

        if fetch_external:
            release_list.load_external_releases()

        return release_list

    @classmethod
    def from_string(cls: Type["ReleaseList"], text: str) -> "ReleaseList":
        "Loads the Releases from a string"
        return cls.from_tag(etree.fromstring(text.encode("utf-8")))

    @classmethod
    def from_file(cls: Type["ReleaseList"], path: str | os.PathLike) -> "ReleaseList":
        "Loads the Releases from a file"
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_string(f.read())

    @classmethod
    def from_url(cls: Type["ReleaseList"], url: str) -> "ReleaseList":
        "Loads the Releases from a URL"
        return cls.from_tag(etree.fromstring(requests.get(url).content))

    def __repr__(self) -> str:
        return f"ReleaseList(type='{self.type}', url='{self.url}', data={self.data})"

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, ReleaseList):
            return False

        try:
            assert_func(self.url == obj.url)
            assert_func(self.type == obj.type)
            assert_func(self.data == obj.data)
            return True
        except AssertionError:
            return False
