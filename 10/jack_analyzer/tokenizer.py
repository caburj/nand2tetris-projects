import re

# LEXICAL ELEMENTS
# Implement these functions using regex

KEYWORDS = "class constructor function method field static var int char boolean void true false null this let do if else while return".split()
SYMBOLS = "{ } ( ) [ ] . , ; + - * / & | < > = ~".split()
SPECIAL_SYMBOLS = dict([("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"), ("&", "&amp;")])


def is_keyword(token):
    return token in KEYWORDS


def is_symbol(token):
    return token in SYMBOLS


def is_integer_constant(token):
    return bool(re.match(r"^[-+]?([1-9]\d*|0)$", token)) and 0 <= int(token) <= 32767


def is_string_constant(token):
    return bool(re.match(r'^".*"$', token))


def is_identifier(token):
    return bool(re.match(r"^[A-Za-z_]\w*$", token))


def remove_comments(source_code: str) -> str:
    """Returns a string without the comments."""
    # removes one-line block comments /** */
    no_line_comment1 = re.sub(r"/\*\*.*\*/", "", source_code)
    # removes line comments //
    no_line_comment2 = re.sub(r"//.*\n", "\n", no_line_comment1)
    # removes block comments /** \n */
    no_comment_string = re.sub(r"/\*\*[\s\S]*\*/", "", no_line_comment2)
    return no_comment_string


def create_token(value):
    if is_keyword(value):
        return f"<keyword> {value} </keyword>"
    if is_integer_constant(value):
        return f"<integerConstant> {value} </integerConstant>"
    if is_identifier(value):
        return f"<identifier> {value} </identifier>"


def tokenize(source_code: str) -> str:
    """Take string of source code and return string of 
    tokens."""
    clean_source_code = remove_comments(source_code)  # ignore comments
    result = ["<tokens>"]
    value = ""
    recording_string = False  # flag for recording string constant
    for char in clean_source_code:
        if recording_string:
            if char == '"':
                result.append(f"<stringConstant> {value} </stringConstant>")
                value = ""
                recording_string = False
            else:
                value += char
        elif bool(re.match(r"\s", char)):
            if value:
                token = create_token(value)
                result.append(token)
                value = ""
        else:
            if is_symbol(char):
                if value:
                    token = create_token(value)
                    result.append(token)
                    value = ""
                result.append(f"<symbol> {SPECIAL_SYMBOLS.get(char) or char } </symbol>")
            elif char == '"':  # start recording string constant here
                if not recording_string:
                    recording_string = True
            else:
                value += char
    result.append("</tokens>")
    return "\n".join(result) + "\n"

