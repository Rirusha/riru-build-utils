from .Shared import TranslateableTag, TranslateableList, Description
from typing import Any, Optional, Literal, TypedDict, Union
from .Release import ReleaseList
from ._helper import assert_func
from .StandardConstants import *
from lxml import etree
import dataclasses
import io
import os


_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def _compare_relation_value(operator: RELATION_COMPARISON_OPERATOR_LITERAL, first: Any, second: Any) -> bool:
    "Matches 2 relation values with the given Operator"
    match operator:
        case "eq":
            return first == second
        case "ne":
            return first != second
        case "lt":
            return first < second
        case "gt":
            return first > second
        case "le":
            return first <= second
        case "ge":
            return first >= second
        case _:
            raise ValueError(f"Invalid Operator {operator}")


class InternetRelationDict(TypedDict):
    "the type for the content of the Internet attribute"
    value: INTERNET_RELATION_VALUE_LITERAL
    bandwidth_mbitps: Optional[int]


class Image:
    "Represents a <image> tag"

    def __init__(self) -> None:
        self.url: str = ""
        "The image URL"

        self.type: Literal["source", "thumbnail"] = "source"
        "The image type"

        self.width: Optional[int] = None
        "The width"

        self.height: Optional[int] = None
        "The height"

        self.language: Optional[str] = None
        "The language"

    def load_tag(self, tag: etree.Element) -> None:
        "Loads a image tag"
        self.url = tag.text.strip()
        self.type = tag.get("type", "source")

        try:
            self.width = int(tag.get("width"))
        except (ValueError, TypeError):
            self.width = None

        try:
            self.height = int(tag.get("height"))
        except (ValueError, TypeError):
            self.height = None

        self.language = tag.get("{http://www.w3.org/XML/1998/namespace}lang")


class Screenshot:
    "Represents a <screenshot> tag"

    def __init__(self) -> None:
        self.images: list[Image] = []
        "the list with thumbnail images"

        self.caption: TranslateableTag = TranslateableTag()
        "The caption"

    def get_source_image(self) -> Optional[Image]:
        "Returns the soucre image"
        for image in self.images:
            if image.type in ("source", None):
                return image
        return None

    def get_thumbnail_images(self) -> list[Image]:
        "Returns the thumbnail images"
        return [image for image in self.images if image.type == "thumbnail"]

    def load_tag(self, tag: etree.Element) -> None:
        "Load a screenshot tag"
        for i in tag.findall("image"):
            img = Image()
            img.load_tag(i)
            self.images.append(img)

        self.caption.load_tags(tag.findall("caption"))


class DisplayLength:
    "Represents a <display_length> tag"

    def __init__(self, px: int = 0, compare: str = "ge") -> None:
        self.px: int = px
        "The logical pixels"

        self.compare: str = compare
        "Compare"

    def compare_px(self, value: int) -> bool:
        """
        Compares the length with the given logical pixels

        :param value: The logical pixels to compare
        :return: If it is valid
        """
        return _compare_relation_value(self.compare, value, self.px)

    def get_tag(self) -> etree.Element:
        """
        Returns the XML Tag

        :return: The Tag
        """
        tag = etree.Element("display_length")
        tag.text = str(self.px)

        if self.compare is not None:
            tag.set("compare", self.compare)

        return tag

    @classmethod
    def from_tag(cls: "DisplayLength", tag: etree.Element) -> "DisplayLength":
        "Creates the Object from an XML Tag"
        display_length = cls()

        try:
            display_length.px = int(tag.text)
        except ValueError:
            display_length.px = cls.string_to_px(tag.text)

        display_length.compare = tag.get("compare", "ge")

        return display_length

    @staticmethod
    def string_to_px(string: str) -> int:
        """
        Converts a Lenght String (e.g.small) to logical pixels value

        :param string: The String
        :raises ValueError: The Length String is invalid
        :return: The logical pixels  pixels
        """
        # https://github.com/ximion/appstream/blob/8d43c78288889d97a3e8502f4a4e777532bb6b04/src/as-relation.c#L418
        match string:
            case "xsmall":
                return 360
            case "small":
                return 420
            case "medium":
                return 760
            case "large":
                return 900
            case "xlarge":
                return 1200
            case _:
                raise ValueError(f"{string} is not a valid size")

    def __repr__(self) -> str:
        return f"<AppstreamPythonDisplayLength px={self.px} compare='{self.compare}>'"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, DisplayLength):
            return False

        try:
            assert_func(self.px == value.px)
            assert_func(self.compare == value.compare)
            return True
        except AssertionError:
            return False


@dataclasses.dataclass
class Developer:
    "Represents a <developer> tag"

    id: Optional[str] = None
    name: TranslateableTag = dataclasses.field(default_factory=lambda: TranslateableTag())

    def load_tag(self, tag: etree.Element) -> None:
        "Loads the data from a XML tag"
        self.id = tag.get("id")

        self.name.load_tags(tag.findall("name"))

    def get_tag(self) -> etree.Element:
        """
        Returns the XML Tag

        :return: The Tag
        """
        tag = etree.Element("developer")

        if self.id is not None:
            tag.set("id", self.id)

        self.name.write_tags(tag, "name")

        return tag

    def clear(self) -> None:
        """Resets all data"""
        self.id = None
        self.name.clear()

    def is_empty(self) -> bool:
        "Checks if the developer tag is empty"
        return self.id is None and self.name.get_default_text() == ""


class AppstreamComponent:
    "Represents AppStream Component"

    def __init__(self) -> None:
        self.id: str = ""
        "The component ID"

        self.type: str = "desktop"
        "The type"

        self.name: TranslateableTag = TranslateableTag()
        "The component name"

        self.developer: Developer = Developer()
        "The developer"

        self.summary: TranslateableTag = TranslateableTag()
        "The component summary"

        self.description: Description = Description()
        "The description"

        self.metadata_license: str = ""
        "The metadata license"

        self.project_license: str = ""
        "The project license"

        self.urls: dict[URL_TYPES_LITERAL, str] = {}
        "The URLs"

        self.launchables: dict[LAUNCHABLE_TYPES, str] = {}
        "The launchables"

        self.oars: dict[OARS_ATTRIBUTE_TYPES_LITERAL, OARS_VALUE_TYPES_LITERAL] = {}
        "The content rating"

        self.categories: list[str] = []
        "The categories"

        self.provides: dict[PROVIDES_TYPES_LITERAL, list[str]] = {}
        "The provides. The content of the depracted mimetype tag goes intp provides['mimetype']"

        self.releases: ReleaseList = ReleaseList()
        "The releases"

        self.screenshots: list[Screenshot] = []
        "The screenshots"

        self.project_group: Optional[str] = None
        "The project group"

        self.translation: list[dict[str, str]] = []
        "The translations"

        self.languages: dict[str, int] = {}
        "The languages"

        self.keywords: TranslateableList = TranslateableList()
        "The Keywords"

        self.controls: dict[CONTROL_TYPES_LITERAL, Optional[Literal["requires", "recommends", "supports"]]] = {}
        "The Controls"

        self.display_length: dict[Literal["requires", "recommends", "supports"], list[DisplayLength]] = {}
        "The Display Length"

        self.internet: dict[Literal["requires", "recommends", "supports"], InternetRelationDict] = {}

        self.kudos: list[str] = []
        "The Kudos"

        self.update_contact: Optional[str] = None
        "The update contact"

        self.replaces: list[str] = []
        "The replaces tag"

        self.suggests: list[str] = []
        "The suggests tag"

        self.custom: dict[str, str] = {}
        "The custom tag"

        self.extends: list[str] = []
        "The extends tag for addons"

        self.clear()

    def clear(self) -> None:
        """Resets the Component"""
        self.id = ""
        self.type = "desktop"
        self.name.clear()
        self.developer.clear()
        self.summary.clear()
        self.description.items.clear()
        self.metadata_license = ""
        self.project_license = ""
        self.categories.clear()
        self.urls.clear()
        self.launchables.clear()
        self.oars.clear()
        self.provides.clear()
        self.releases = ReleaseList()
        self.screenshots.clear()
        self.project_group = None
        self.translation.clear()
        self.languages.clear()
        self.keywords.clear()
        self.controls.clear()
        self.display_length.clear()
        self.internet.clear()
        self.kudos.clear()
        self.update_contact = None
        self.replaces.clear()
        self.suggests.clear()
        self.custom.clear()
        self.extends.clear()

        for i in PROVIDES_TYPES:
            self.provides[i] = []

        for i in CONTROL_TYPES:
            self.controls[i] = None

    def get_available_languages(self) -> list[str]:
        "Returns a list with all available languages of the Component"
        lang_list = self.name.get_available_languages() + self.summary.get_available_languages() + self.developer.name.get_available_languages()
        return list(set(lang_list))

    def _parse_relation_tag(self, tag: etree.Element) -> None:
        "Parses a relation tag"
        relation = tag.tag

        for control_tag in tag.findall("control"):
            if control_tag.text.strip() in CONTROL_TYPES:
                self.controls[control_tag.text.strip()] = relation

        for display_length_tag in tag.findall("display_length"):
            if relation in self.display_length:
                self.display_length[relation].append(DisplayLength.from_tag(display_length_tag))
            else:
                self.display_length[relation] = [DisplayLength.from_tag(display_length_tag)]

        internet_tag = tag.find("internet")
        if internet_tag is not None:
            internet_dict: InternetRelationDict = {"value": internet_tag.text.strip()}

            try:
                internet_dict["bandwidth_mbitps"] = int(internet_tag.get("bandwidth_mbitps"))
            except (ValueError, TypeError):
                internet_dict["bandwidth_mbitps"] = None

            self.internet[relation] = internet_dict

    def parse_component_tag(self, tag: etree._ElementTree) -> None:
        "Parses a XML tag"
        self.id = tag.find("id").text.strip()

        try:
            self.type = tag.xpath("/component")[0].get("type")
        except IndexError:
            self.type = tag.get("type")

        self.name.load_tags(tag.findall("name"))

        # For backward compatibility
        self.developer.name.load_tags(tag.findall("developer_name"))

        if (developer_tag := tag.find("developer")) is not None:
            self.developer.load_tag(developer_tag)

        self.summary.load_tags(tag.findall("summary"))

        description_tag = tag.find("description")
        if description_tag is not None:
            self.description.load_tags(description_tag)

        metadata_license_tag = tag.find("metadata_license")
        if metadata_license_tag is not None and metadata_license_tag.text is not None:
            self.metadata_license = metadata_license_tag.text.strip()

        project_license_tag = tag.find("project_license")
        if project_license_tag is not None and project_license_tag.text is not None:
            self.project_license = project_license_tag.text.strip()

        categories_tag = tag.find("categories")
        if categories_tag is not None:
            for i in categories_tag.findall("category"):
                self.categories.append(i.text.strip())

        for i in tag.findall("url"):
            if i.get("type") in URL_TYPES:
                self.urls[i.get("type")] = i.text.strip()

        for i in tag.findall("launchable"):
            if i.get("type") in LAUNCHABLE_TYPES:
                self.launchables[i.get("type")] = i.text.strip()

        oars_tag = tag.find("content_rating")
        if oars_tag is not None:
            for i in oars_tag.findall("content_attribute"):
                if i.get("id") in OARS_ATTRIBUTE_TYPES and i.text.strip() in OARS_VALUE_TYPES:
                    self.oars[i.get("id")] = i.text.strip()

        provides_tag = tag.find("provides")
        if provides_tag is not None:
            for i in provides_tag.getchildren():
                if i.tag in PROVIDES_TYPES:
                    self.provides[i.tag].append(i.text.strip())

        # For backwards compatibility. See: https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html#tag-mimetypes
        mimetypes_tag = tag.find("mimetypes")
        if mimetypes_tag is not None:
            for i in mimetypes_tag.findall("mimetype"):
                self.provides["mediatype"].append(i.text.strip())

        releases_tag = tag.find("releases")
        if releases_tag is not None:
            self.releases = ReleaseList.from_tag(releases_tag)

        screenshots_tag = tag.find("screenshots")
        if screenshots_tag is not None:
            for i in screenshots_tag.findall("screenshot"):
                screenshot = Screenshot()
                screenshot.load_tag(i)
                self.screenshots.append(screenshot)

        project_group_tag = tag.find("project_group")
        if project_group_tag is not None:
            self.project_group = project_group_tag.text.strip()

        for i in tag.findall("translation"):
            trans_dict = {}
            trans_dict["type"] = i.get("type")
            if i.text is None:
                trans_dict["value"] = ""
            else:
                trans_dict["value"] = i.text.strip()
            self.translation.append(trans_dict)

        languages_tag = tag.find("languages")
        if languages_tag is not None:
            for i in languages_tag.findall("lang"):
                try:
                    self.languages[i.text.strip()] = int(i.get("percentage") or 100)
                except ValueError:
                    pass

        for i in tag.findall("keywords"):
            self.keywords.load_tag(i)

        supports_tag = tag.find("supports")
        if supports_tag is not None:
            self._parse_relation_tag(supports_tag)

        recommends_tag = tag.find("recommends")
        if recommends_tag is not None:
            self._parse_relation_tag(recommends_tag)

        requires_tag = tag.find("requires")
        if requires_tag is not None:
            self._parse_relation_tag(requires_tag)

        kudos_tag = tag.find("kudos")
        if kudos_tag is not None:
            for i in kudos_tag.findall("kudo"):
                self.kudos.append(i.text.strip())

        update_contact_tag = tag.find("update_contact")
        if update_contact_tag is not None:
            self.update_contact = update_contact_tag.text.strip()

        replaces_tag = tag.find("replaces")
        if replaces_tag is not None:
            for i in replaces_tag.findall("id"):
                self.replaces.append(i.text)

        suggests_tag = tag.find("suggests")
        if suggests_tag is not None:
            for i in suggests_tag.findall("id"):
                self.suggests.append(i.text)

        custom_tag = tag.find("custom")
        if custom_tag is not None:
            for i in custom_tag.findall("value"):
                if key := i.get("key", "").strip():
                    self.custom[key] = i.text.strip()

        for i in tag.findall("extends"):
            self.extends.append(i.text.strip())

    @classmethod
    def from_component_tag(cls: "AppstreamComponent", root: etree._Element) -> "AppstreamComponent":
        "Load an appdata.xml or metainfo.xml file"
        component = cls()
        component.parse_component_tag(root)
        return component

    def load_file(self, path: Union[str, os.PathLike, io.RawIOBase]) -> None:
        """Load an appdata.xml or metainfo.xml file"""
        root = etree.parse(path)
        self.parse_component_tag(root)

    @classmethod
    def from_file(cls: "AppstreamComponent", path: Union[str, os.PathLike, io.RawIOBase]) -> "AppstreamComponent":
        "Load an appdata.xml or metainfo.xml file"
        component = cls()
        component.load_file(path)
        return component

    def load_bytes(self, data: bytes, encoding: Optional[str] = None) -> None:
        """Load an appdata.xml or metainfo.xml byte string"""
        root = etree.fromstring(data, parser=etree.XMLParser(encoding=encoding))
        self.parse_component_tag(root)

    @classmethod
    def from_bytes(cls: "AppstreamComponent", data: bytes, encoding: Optional[str] = None) -> "AppstreamComponent":
        "Load an appdata.xml or metainfo.xml byte string"
        component = cls()
        component.load_bytes(data, encoding)
        return component

    def load_string(self, text: str) -> None:
        """Load an appdata.xml or metainfo.xml string"""
        self.load_bytes(text.encode("utf-8"), encoding="utf-8")

    @classmethod
    def from_string(cls: "AppstreamComponent", text: str) -> "AppstreamComponent":
        "Load an appdata.xml or metainfo.xml string"
        component = cls()
        component.load_string(text)
        return component

    def _get_relation_tag(self, parent_tag: etree.Element, relation: Literal["supports", "recommends", "requires"]) -> None:
        "Craetes a relation tag from the Component."
        relation_tag = etree.SubElement(parent_tag, relation)

        for key, value in self.controls.items():
            if key in CONTROL_TYPES and value == relation:
                control_tag = etree.SubElement(relation_tag, "control")
                control_tag.text = key

        for display_length in self.display_length.get(relation, []):
            relation_tag.append(display_length.get_tag())

        if relation in self.internet:
            internet_tag = etree.SubElement(relation_tag, "internet")

            if self.internet[relation]["bandwidth_mbitps"] is not None:
                internet_tag.set("bandwidth_mbitps", str(self.internet[relation]["bandwidth_mbitps"]))

            internet_tag.text = self.internet[relation]["value"]

        if len(relation_tag.getchildren()) == 0:
            parent_tag.remove(relation_tag)

    def get_component_tag(self) -> etree.Element:
        "Creates a XML tag from the Component"
        tag = etree.Element("component")
        tag.set("type", self.type)

        id_tag = etree.SubElement(tag, "id")
        id_tag.text = self.id

        self.name.write_tags(tag, "name")

        if not self.developer.is_empty():
            tag.append(self.developer.get_tag())

        self.summary.write_tags(tag, "summary")

        self.description.get_tags(tag)

        metadata_license_tag = etree.SubElement(tag, "metadata_license")
        metadata_license_tag.text = self.metadata_license

        project_license_tag = etree.SubElement(tag, "project_license")
        project_license_tag.text = self.project_license

        for key, value in self.urls.items():
            if key in URL_TYPES:
                url_tag = etree.SubElement(tag, "url")
                url_tag.set("type", key)
                url_tag.text = value

        for key, value in self.launchables.items():
            if key in LAUNCHABLE_TYPES:
                url_tag = etree.SubElement(tag, "launchable")
                url_tag.set("type", key)
                url_tag.text = value

        oars_tag = etree.SubElement(tag, "content_rating")
        oars_tag.set("type", "oars-1.1")
        for key, value in self.oars.items():
            if key in OARS_ATTRIBUTE_TYPES and value in OARS_VALUE_TYPES:
                single_oars_tag = etree.SubElement(oars_tag, "content_attribute")
                single_oars_tag.set("id", key)
                single_oars_tag.text = value

        if len(self.categories) > 0:
            categories_tag = etree.SubElement(tag, "categories")
            for i in self.categories:
                single_categorie_tag = etree.SubElement(categories_tag, "category")
                single_categorie_tag.text = i

        provides_tag = etree.SubElement(tag, "provides")
        for key, value in self.provides.items():
            if key not in PROVIDES_TYPES:
                continue
            for i in value:
                single_provides_tag = etree.SubElement(provides_tag, key)
                single_provides_tag.text = i

        # Don't write empty provides tag
        if len(provides_tag.getchildren()) == 0:
            tag.remove(provides_tag)

        if len(self.releases) != 0:
            tag.append(self.releases.get_tag())

        if self.project_group:
            project_group_tag = etree.SubElement(tag, "project_group")
            project_group_tag.text = self.project_group

        for i in self.translation:
            translation_tag = etree.SubElement(tag, "translation")
            translation_tag.set("type", i["type"])
            translation_tag.text = i["value"]

        if len(self.languages) > 0:
            languages_tag = etree.SubElement(tag, "languages")
            for key, value in self.languages.items():
                single_language_tag = etree.SubElement(languages_tag, "lang")
                single_language_tag.set("percentage", str(value))
                single_language_tag.text = key

        self._get_relation_tag(tag, "supports")
        self._get_relation_tag(tag, "recommends")
        self._get_relation_tag(tag, "requires")

        if len(self.kudos) > 0:
            kudos_tag = etree.SubElement(tag, "kudos")
            for i in self.kudos:
                single_kudos_tag = etree.SubElement(kudos_tag, "kudo")
                single_kudos_tag.text = i

        if self.update_contact:
            update_contact_tag = etree.SubElement(tag, "update_contact")
            update_contact_tag.text = self.update_contact

        if len(self.replaces) > 0:
            replaces_tag = etree.SubElement(tag, "replaces")
            for i in self.replaces:
                replaces_id_tag = etree.SubElement(replaces_tag, "id")
                replaces_id_tag.text = i.strip()

        if len(self.suggests) > 0:
            suggests_tag = etree.SubElement(tag, "suggests")
            for i in self.suggests:
                suggests_id_tag = etree.SubElement(suggests_tag, "id")
                suggests_id_tag.text = i.strip()

        if len(self.custom) > 0:
            custom_tag = etree.SubElement(tag, "custom")
            for key, value in self.custom:
                value_tag = etree.SubElement(custom_tag, "value")
                value_tag.set("key", key.strip())
                value_tag.text = value.strip()

        for i in self.extends:
            extends_tag = etree.SubElement(tag, "extends")
            extends_tag.text = i

        return tag

    def get_xml_string(self) -> str:
        """Returns the XML data of the Component as string"""
        return etree.tostring(self.get_component_tag(), pretty_print=True, encoding=str).strip()

    def save_file(self, path: str) -> None:
        """Saves the Component as XML file"""
        with open(path, "wb") as f:
            f.write(etree.tostring(self.get_component_tag(), pretty_print=True, xml_declaration=True, encoding="utf-8"))

    def __repr__(self) -> str:
        return f"<AppstreamComponent id='{self.id}'>"
