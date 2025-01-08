"This module contains constansts for Appstream"
from typing import Literal, get_args

URL_TYPES_LITERAL = Literal[
    "homepage",
    "bugtracker",
    "faq",
    "help",
    "donation",
    "translate",
    "contact",
    "vcs-browser",
    "contribute"
]

LAUNCHABLE_TYPES_LITERAL = Literal[
    "desktop-id",
    "service",
    "cockpit-manifest",
    "url"
]

OARS_ATTRIBUTE_TYPES_LITERAL = Literal[
    "violence-cartoon",
    "violence-fantasy",
    "violence-realistic",
    "violence-bloodshed",
    "violence-sexual",
    "violence-desecration",
    "violence-slavery",
    "drugs-alcohol",
    "drugs-narcotics",
    "drugs_tobacco",
    "sex_nudity",
    "sex-themes",
    "language-profanity",
    "language-humor",
    "language-discrimination",
    "money-advertising",
    "money-gambling",
    "money-purchasing",
    "social-chat",
    "social-audio",
    "social-contacts",
    "social-info",
    "social-location"
]

OARS_VALUE_TYPES_LITERAL = Literal[
    "none",
    "mild",
    "moderate",
    "intense"
]

PROVIDES_TYPES_LITERAL = Literal[
    "mediatype",
    "library",
    "binary",
    "font",
    "modalias",
    "firmware",
    "python2",
    "python3",
    "dbus",
    "id"
]

RELATION_COMPARISON_OPERATOR_LITERAL = Literal[
    "eq",
    "ne",
    "lt",
    "gt",
    "le",
    "ge"
]

CONTROL_TYPES_LITERAL = Literal[
    "pointing",
    "keyboard",
    "console",
    "tablet",
    "touch",
    "gamepad",
    "tv-remote",
    "voice",
    "vision"
]

INTERNET_RELATION_VALUE_LITERAL = Literal[
    "always"
    "offline-only"
    "first-run"
]

URL_TYPES = list(get_args(URL_TYPES_LITERAL))
"All URL types"

LAUNCHABLE_TYPES = list(get_args(LAUNCHABLE_TYPES_LITERAL))
"All launchable types"

OARS_ATTRIBUTE_TYPES = list(get_args(OARS_ATTRIBUTE_TYPES_LITERAL))
"All aviable OARS attributes"

OARS_VALUE_TYPES = list(get_args(OARS_VALUE_TYPES_LITERAL))
"All ORAS value types"

PROVIDES_TYPES = list(get_args(PROVIDES_TYPES_LITERAL))
"The list with all types for provides"

RELATION_COMPARISON_OPERATOR = list(get_args(RELATION_COMPARISON_OPERATOR_LITERAL))
"The aviable Operators for the relation compare attribute"

CONTROL_TYPES = list(get_args(CONTROL_TYPES_LITERAL))
"The list with all possible values for control"

INTERNET_RELATION_VALUE = list(get_args(INTERNET_RELATION_VALUE_LITERAL))
"The list with all possible values for internet"
