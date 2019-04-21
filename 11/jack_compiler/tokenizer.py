import re

__all__ = ["tokenize"]


KEYWORDS = "class constructor function method field static var int char boolean void true false null this let do if else while return".split()
SYMBOLS = r"\{ \} \( \) \[ \] \. \, \; \+ \- \* \/ \& \| \< \> \= \~".split()
SPECIAL_SYMBOLS = dict([("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"), ("&", "&amp;")])


def tokenize(source_code: str) -> list:
    """Take string of source code and return string of 
    tokens."""
    token_specification = [
        ("comment", "|".join([r"//.*\n", r"/\*\*([\s\S])+?\*/"])),
        ("symbol", "|".join(SYMBOLS)),
        ("integerConstant", r"([1-9]\d*|0)"),
        ("stringConstant", r'".*"'),
        ("identifier", r"[A-Za-z_]\w*"),
        ("mismatch", r"."),
    ]
    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, source_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "identifier":
            if value in KEYWORDS:
                kind == "keyword"
        if kind in ("mismatch", "comment"):
            continue
        if kind == "stringConstant":
            value = value[1:-1]
        yield (kind, value)

