from .Component import AppstreamComponent
from lxml import etree
import gzip


class AppstreamCollection:
    "Represents a Collection of multiple AppStream files"
    def __init__(self) -> None:
        self._components: dict[str, AppstreamComponent] = {}
        self._categories: dict[str, list[str]] = {}

    def _add_appstream_tag(self, tag: etree.Element) -> None:
        component_data = AppstreamComponent()
        component_data.parse_component_tag(tag)
        self.add_component(component_data)

    def add_component(self, component: AppstreamComponent) -> None:
        "Adds a AppstreamComponent to the collection"
        self._components[component.id] = component

        for i in component.categories:
            if i not in self._categories:
                self._categories[i] = []
            self._categories[i].append(component.id)

    def load_uncompressed_appstream_collection(self, path: str) -> None:
        "Loads a uncompressed collection"
        with open(path, "rb") as f:
            root = etree.fromstring(f.read())

        for i in root.findall("component"):
            self._add_appstream_tag(i)

    def load_compressed_appstream_collection(self, path: str) -> None:
        "Loads a GZIP compressed collection"
        with gzip.open(path, "rb") as f:
            root = etree.fromstring(f.read())

        for i in root.findall("component"):
            self._add_appstream_tag(i)

    def load_appstream_file(self, path: str) -> None:
        """Load a appdata.xml or metainfo.xml file"""
        with open(path, "rb") as f:
            root = etree.fromstring(f.read())

        self._add_appstream_tag(root)

    def get_component_list(self) -> list[AppstreamComponent]:
        """Returns a list with all components"""
        return list(self._components.values())

    def get_component_id_list(self) -> list[str]:
        """Returns a list with all available component id's"""
        return list(self._components.keys())

    def get_component(self, component_id: str) -> AppstreamComponent:
        """Returns the component with the given id"""
        return self._components.get(component_id, None)

    def find_by_category(self, category: str) -> list[AppstreamComponent]:
        """Returns a list with all components with the given category"""
        if category not in self._categories:
            return []

        category_list: list[AppstreamComponent] = []
        for i in self._categories[category]:
            category_list.append(self._components[i])

        return category_list

    def get_collection_tag(self) -> etree.Element:
        "Gets the XML from the Collection"
        components_tag = etree.Element("components")

        for i in self._components.values():
            components_tag.append(i.get_component_tag())

        return components_tag

    def write_uncompressed_file(self, path: str) -> None:
        "Writes a Uncompressed collection file"
        with open(path, "w", encoding="utf-8") as f:
            f.write(etree.tostring(self.get_collection_tag(), pretty_print=True, xml_declaration=True, encoding="utf-8").decode("utf-8"))

    def write_compressed_file(self, path: str) -> None:
        "Writes a Uncompressed collection file"
        with gzip.open(path, "wb") as f:
            f.write(etree.tostring(self.get_collection_tag(), pretty_print=True, xml_declaration=True, encoding="utf-8"))

    def __len__(self) -> int:
        return len(self._components)
