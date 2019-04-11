import re

# LEXICAL ELEMENTS
# Implement these functions using regex

KEYWORDS = "class constructor function method field static var int char boolean void true false null this let do if else while return".split()
SYMBOLS = "{ } ( ) [ ] . , ; + - * / & | < > = ~".split()

def is_keyword(token):
    return token in KEYWORDS

def is_symbol(token):
    return token in SYMBOLS

def is_integer_constant(token):
    return bool(re.match(r'^[-+]?([1-9]\d*|0)$', token)) and 0 <= int(token) <= 32767  

def is_string_constant(token):
    return bool(re.match(r'^".*"$', token))

def is_identifier(token):
    return bool(re.match(r'^[A-Za-z_]\w*$', token))

def qualify(temp):
    if is_keyword(temp):
        return f'<keyword> {temp} </keyword>'
    if is_integer_constant(temp):
        return f'<integerConstant> {temp} </integerConstant>'
    if is_string_constant(temp):
        return f'<StringConstant> {temp} </StringConstant>'
    if is_identifier(temp):
        return f'<identifier> {temp} </identifier>'

def tokenize(string):
    """Take string of source code and return string of 
    tokens."""
    clean_string = clean(string) # ignore comments
    result = ['<tokens>']
    temp = ''
    recording_string = False
    for c in clean_string:
        if recording_string:
            temp += c
            if c == '"':
                result.append(f'<StringConstant> {temp[:-1]} </StringConstant>')
                temp = ''
                recording_string = False
            continue
        if bool(re.match(r'\s', c)):
            if temp:
                token = qualify(temp)
                result.append(token)
                temp = ''
            else:
                continue
        else:
            if is_symbol(c):
                if temp:
                    token = qualify(temp)
                    result.append(token)
                    temp = ''
                result.append(f'<symbol> {c} </symbol>')
            elif c == '"':
                if not recording_string:
                    recording_string = True
            else:
                temp += c
    result.append('</tokens>')
    return result

def clean(string):
    """Returns a string without the comments."""
    no_block_comment_string = re.sub(r'/\*\*.*\*/', '', string)
    no_comment_string = re.sub(r'//.*\n', '\n', no_block_comment_string)
    return no_comment_string

def parse(tokens):
    """Take string of tokens and return parse tree."""
    pass

if __name__ == "__main__":
    """Takes a .jack file or directory containing list of .jack files.
    Then creates .xml file corresponding to tokenized or parsed file.
    
    e.g.
    $ analyzer.py tokenize xxx.jack 
    // will create a xxx.xml file in the same directory
    
    $ analyzer.py parse .
    // will create corresponding .xml file for all the files in the 
    // current directory
    """
    pass