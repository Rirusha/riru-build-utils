from typing import Optional, Literal
from ._helper import assert_func
from lxml import etree


_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class TranslateableTag:
    "Represents a translatable tag"
    def __init__(self) -> None:
        self._text = ""
        self._translations: dict[str, str] = {}

    def get_default_text(self) -> str:
        """Returns the untranslated text"""
        return self._text

    def set_default_text(self, text: str) -> None:
        """Sets the untranslated text"""
        self._text = text

    def get_translated_text(self, lang: str) -> Optional[str]:
        """Returns the translated text"""
        return self._translations.get(lang, None)

    def get_translated_text_default(self, lang: str) -> Optional[str]:
        """Returns the translated text. Returns the default text, if the translation does not exists"""
        return self._translations.get(lang, self._text)

    def set_translated_text(self, lang: str, text: str) -> None:
        """Sets the translated text"""
        self._translations[lang] = text

    def get_available_languages(self) -> list[str]:
        """Returns a list with all languages of the tag"""
        return list(self._translations.keys())

    def load_tags(self, tag_list: list[etree.Element]) -> None:
        """Load a list of Tags"""
        for i in tag_list:
            if i.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
                if i.text is not None:
                    self._text = i.text.strip()
                else:
                    self._text = ""
            else:
                if i.text is not None:
                    self._translations[i.get(_XML_LANG)] = i.text.strip()
                else:
                    self._translations[i.get(_XML_LANG)] = ""

    def write_tags(self, parent_tag: etree.Element, tag_name: str) -> None:
        """Writes a Tag"""
        default_tag = etree.SubElement(parent_tag, tag_name)
        default_tag.text = self._text

        for key, value in self._translations.items():
            translation_tag = etree.SubElement(parent_tag, tag_name)
            translation_tag.set("{http://www.w3.org/XML/1998/namespace}lang", key)
            translation_tag.text = value

    def clear(self) -> None:
        """Resets all data"""
        self._text = ""
        self._translations.clear()

    def __repr__(self) -> str:
        return f"<TranslateableTag default='{self._text}'>"

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, TranslateableTag):
            return False

        try:
            assert_func(self._translations == obj._translations)
            return True
        except AssertionError:
            return False


class TranslateableList:
    "Represents a translatable list"

    def __init__(self) -> None:
        self._translated_data: dict[str, dict[str, str]] = {}
        self._translated_lists: dict[str, list[str]] = {}

    def get_default_list(self) -> list[str]:
        "Returns a list with the default items"
        return list(self._translated_data.keys())

    def get_translated_list(self, lang: str) -> list[str]:
        "Returns the translated list for the given language"
        if lang in self._translated_lists:
            return self._translated_lists[lang]

        return_list: list[str] = []
        for untranslated_text, translations in self._translated_data.items():
            return_list.append(translations.get(lang, untranslated_text))
        return return_list

    def load_tag(self, tag: etree.Element) -> None:
        "Loads an Tag. Only for internal use."
        if tag.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
            current_text = ""
            for i in tag.getchildren():
                if i.get(_XML_LANG) is None:
                    try:
                        current_text = i.text.strip()
                        self._translated_data[current_text] = {}
                    except AttributeError:
                        pass
                else:
                    if current_text in self._translated_data:
                        self._translated_data[current_text][i.get(_XML_LANG)] = i.text.strip()
        else:
            if tag.get("{http://www.w3.org/XML/1998/namespace}lang") not in self._translated_lists:
                self._translated_lists[tag.get("{http://www.w3.org/XML/1998/namespace}lang")] = []
            for i in tag.getchildren():
                self._translated_lists[tag.get("{http://www.w3.org/XML/1998/namespace}lang")].append(i.text.strip())

    def write_all_tag(self, parent_tag: etree.Element, tag_name: str) -> None:
        "Writes the XML tags. Onnly for internal use."
        for untranslated_text, translations in self._translated_data.items():
            default_tag = etree.SubElement(parent_tag, tag_name)
            default_tag.text = untranslated_text
            for lang, translated_text in translations.items():
                translated_tag = etree.SubElement(parent_tag, tag_name)
                translated_tag.set(_XML_LANG, lang)
                translated_tag.text = translated_text

    def write_untranslated_tags(self, parent_tag: etree.Element, tag_name: str) -> None:
        "Writes the untranslated XML tags. Onnly for internal use."
        for untranslated_text in self._translated_data.keys():
            default_tag = etree.SubElement(parent_tag, tag_name)
            default_tag.text = untranslated_text

    def write_translated_tags(self, parent_tag: etree.Element, tag_name: str, lang: str) -> None:
        "Writes the translated XML tags. Onnly for internal use."
        for untranslated_text, translations in self._translated_data.items():
            child_tag = etree.SubElement(parent_tag, tag_name)
            child_tag.text = translations.get(lang, untranslated_text)

    def clear(self) -> None:
        """Resets all data"""
        self._translated_data.clear()

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, TranslateableList):
            return False

        try:
            assert_func(self._translated_data == obj._translated_data)
            assert_func(self._translated_lists == obj._translated_lists)
            return True
        except AssertionError:
            return False


class DescriptionItem:
    "The Interface for a Description Item"

    def get_type(self) -> Literal["paragraph", "unordered-list", "ordered-list"]:
        "Retutns the Type of the Item"
        return "none"

    def load_tags(self, tag_list: list[etree.Element]) -> None:
        "Loads teh XML tags into the Elemnt. Only for internal use."
        raise NotImplementedError

    def get_tags(self, parent_tag: etree.Element) -> None:
        "Get the XML Tag from the Element. Only for internal use."
        raise NotImplementedError()

    def get_translated_tag(self, lang: Optional[str]) -> etree.Element:
        "Loads the tag for a given language"
        raise NotImplementedError()

    def to_plain_text(self, lang: Optional[str] = None) -> str:
        "Returns the content as plain text"
        raise NotImplementedError()


class DescriptionParagraph(DescriptionItem):
    "Represents a paragraph <p> in the Description"

    def __init__(self) -> None:
        self.content = TranslateableTag()
        """The Text of the Paragraph"""

    def get_type(self) -> Literal["paragraph", "unordered-list", "ordered-list"]:
        "Retutns the Type of the Item"
        return "paragraph"

    def load_tags(self, tag_list: list[etree.Element]) -> None:
        "Loads teh XML tags into the Elemnt. Only for internal use."
        self.content.load_tags(tag_list)

    def get_tags(self, parent_tag: etree.Element) -> None:
        "Get the XML Tag from the Element. Only for internal use."
        self.content.write_tags(parent_tag, "p")

    def get_translated_tag(self, lang: Optional[str]) -> etree.Element:
        "Loads the tag for a given language"
        paragraph_tag = etree.Element("p")
        if lang is None:
            paragraph_tag.text = self.content.get_default_text()
        else:
            paragraph_tag.text = self.content.get_translated_text_default(lang)
        return paragraph_tag

    def to_plain_text(self, lang: Optional[str] = None) -> str:
        "Returns the content as plain text"
        return self.content.get_translated_text_default(lang).strip()

    def __repr__(self) -> str:
        return f"<DescriptionParagraph default='{self.content.get_default_text()}'>"

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, DescriptionParagraph):
            return False

        return self.content == obj.content


class DescriptionList(DescriptionItem):
    "Represents a list <ul>/<ol> in the Description"

    def __init__(self, list_type: str) -> None:
        self._list_type = list_type

        self.content: TranslateableList = TranslateableList()
        "The list"

    def get_type(self) -> Literal["paragraph", "unordered-list", "ordered-list"]:
        "Returns the Type of the Item"
        if self._list_type == "ul":
            return "unordered-list"
        else:
            return "ordered-list"

    def load_tags(self, tag_list: list[etree.Element]) -> None:
        "Loads the XML tags into the Elemnt. Only for internal use."
        self.content.load_tag(tag_list)

    def get_tags(self, parent_tag: etree.Element) -> None:
        "Get the XML Tag from the Element. Only for internal use."
        list_tag = etree.SubElement(parent_tag, self._list_type)
        self.content.write_all_tag(list_tag, "li")

    def get_translated_tag(self, lang: Optional[str] = None) -> etree.Element:
        "Loads the tag for a given language"
        list_tag = etree.Element(self._list_type)
        if lang is None:
            self.content.write_untranslated_tags(list_tag, "li")
        else:
            self.content.write_translated_tags(list_tag, "li", lang)
        return list_tag

    def to_plain_text(self, lang: Optional[str] = None) -> str:
        "Returns the content as plain text"
        tag_list = self.content.get_translated_list(lang)

        return_text = ""
        if self.get_type() == "unordered-list":
            for tag_text in tag_list:
                return_text += f"• {tag_text}\n"
        elif self.get_type() == "ordered-list":
            for count, tag_text in enumerate(tag_list):
                return_text += f"{count + 1}. {tag_text}\n"

        return return_text.strip()

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, DescriptionList):
            return False

        try:
            assert_func(self._list_type == obj._list_type)
            assert_func(self.content == obj.content)
            return True
        except AssertionError:
            return False


class Description:
    "Represents a <description> tag"

    def __init__(self) -> None:
        self.items: list[DescriptionItem] = []
        """All Description Items"""

    def load_tags(self, tag: etree.Element) -> None:
        "Load a XML tag. Onyl for internal use."
        paragraph_list: list[etree.Element] = []
        for i in tag.getchildren():
            if i.tag == "p":
                if i.get("{http://www.w3.org/XML/1998/namespace}lang") is not None:
                    paragraph_list.append(i)
                else:
                    if len(paragraph_list) != 0:
                        paragraph_item = DescriptionParagraph()
                        paragraph_item.load_tags(paragraph_list)
                        self.items.append(paragraph_item)
                    paragraph_list.clear()
                    paragraph_list.append(i)
            elif i.tag in ("ul", "ol"):
                if len(paragraph_list) != 0:
                    paragraph_item = DescriptionParagraph()
                    paragraph_item.load_tags(paragraph_list)
                    self.items.append(paragraph_item)
                    paragraph_list.clear()

                list_item = DescriptionList(i.tag)
                list_item.load_tags(i)
                self.items.append(list_item)

        if len(paragraph_list) != 0:
            paragraph_item = DescriptionParagraph()
            paragraph_item.load_tags(paragraph_list)
            self.items.append(paragraph_item)

    def get_tags(self, parent_tag: etree.Element) -> None:
        "Writes a Description tag. Only for internal use."
        description_tag = etree.SubElement(parent_tag, "description")
        for i in self.items:
            i.get_tags(description_tag)

    def to_html(self, lang: Optional[str] = None) -> str:
        "Get the HTML code of the description in the given language"
        description_tag = etree.Element("description")

        for i in self.items:
            description_tag.append(i.get_translated_tag(lang))

        text = etree.tostring(description_tag, pretty_print=True, encoding="utf-8").decode("utf-8")

        # Remove the description tag
        text = text.replace("<description>", "")
        text = text.replace("</description>", "")
        text = text.replace("<description/>", "")

        # Remove the 2 spaces at the start of each line, after we removed the description tag
        return_text = ""
        for line in text.splitlines():
            return_text += line.removeprefix("  ") + "\n"

        return return_text.strip()

    def to_plain_text(self, lang: Optional[str] = None) -> str:
        """
        Converts the Description into Plain Text

        :param lang: The language
        :return: The Description
        """
        text = ""

        for i in self.items:
            text += f"{i.to_plain_text(lang)}\n\n"

        text = text.removesuffix("\n\n")

        return text.strip()

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Description):
            return False

        return self.items == obj.items
