from tokenizer import tokenize

__all__ = ["parse"]


def parse(source_code: str):
    tokens = tokenize(source_code)
    return compile_class(tokens, result=[], indent=1)


def to_xml(token, indent=0):
    kind, value = token
    return "  " * indent + f"<{kind}> {value} </{kind}>"


def opening(tag, indent):
    return "  " * indent + f"<{tag}>"


def closing(tag, indent):
    return "  " * indent + f"</{tag}>"


def compile_class(tokens, result, indent):
    """
    <class> =>
        'class' identifier '{' <classVarDec>* <subroutineDec>* '}'
    """
    result.append(opening("class", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))  # take 'class'
    result.append(to_xml(tokens.pop(0), indent))  # take identifier
    result.append(to_xml(tokens.pop(0), indent))  # take '{'
    compile_class_var_dec(tokens, result, indent + 1)
    compile_subroutine_dec(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))  # take '}'
    result.append(closing("class", indent - 1))
    return result


def compile_class_var_dec(tokens, result, indent):
    """
    <classVarDec> =>
        ('static' | 'field') ('int' | 'char' | 'boolean' | identifier) identifier (',' identifier)* ';'

    """
    while tokens[0][1] in ("static", "field"):
        result.append(opening("classVarDec", indent - 1))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        while tokens[0][1] == ",":
            result.append(to_xml(tokens.pop(0), indent))
            result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(closing("classVarDec", indent - 1))


def compile_subroutine_dec(tokens, result, indent):
    """
    <subroutineDec> =>
        ('constructor' | 'function' | 'method')
        ('void' | 'int' | 'char' | 'boolean' | identifier) identifier '(' <parameterList> ')'
        <subroutineBody>
    """
    while tokens[0][1] in ("constructor", "function", "method"):
        result.append(opening("subroutineDec", indent - 1))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        compile_parameter_list(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
        compile_subroutine_body(tokens, result, indent + 1)
        result.append(closing("subroutineDec", indent - 1))


def compile_parameter_list(tokens, result, indent):
    """
    <parameterList> =>
        (<type> identifier (',' <type> identifier)* )?
    """
    result.append(opening("parameterList", indent - 1))
    while tokens[0][1] != ")":
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        while tokens[0][1] == ",":
            result.append(to_xml(tokens.pop(0), indent))
            result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("parameterList", indent - 1))


def compile_subroutine_body(tokens, result, indent):
    """
    <subroutineBody> =>
        '{' <varDec>* <statements> '}'
    """
    result.append(opening("subroutineBody", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))
    compile_var_dec(tokens, result, indent + 1)
    compile_statements(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("subroutineBody", indent - 1))


def compile_var_dec(tokens, result, indent):
    """
    <varDec> =>
        'var' ('int' | 'char' | 'boolean' | identifier) identifier (',' identifier)* ';'
    """
    while tokens[0][1] == "var":
        result.append(opening("varDec", indent - 1))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        while tokens[0][1] == ",":
            result.append(to_xml(tokens.pop(0), indent))
            result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(closing("varDec", indent - 1))


def compile_statements(tokens, result, indent):
    """
    <statements> =>
      ( <letStatement> | <ifStatement> | <whileStatement> |
        <doStatement> | <returnStatement>
        <statement> )*
    """
    result.append(opening("statements", indent - 1))
    while tokens[0][1] in ("let", "if", "while", "do", "return"):
        kind, value = tokens[0]
        if value == "let":
            compile_let_statement(tokens, result, indent + 1)
        elif value == "if":
            compile_if_statement(tokens, result, indent + 1)
        elif value == "while":
            compile_while_statement(tokens, result, indent + 1)
        elif value == "do":
            compile_do_statement(tokens, result, indent + 1)
        elif value == "return":
            compile_return_statement(tokens, result, indent + 1)
    result.append(closing("statements", indent - 1))


def compile_let_statement(tokens, result, indent):
    """
    <letStatement> =>
        'let' identifier ('[' <expression> ']')? '=' <expression> ';'
    """
    result.append(opening("letStatement", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    if tokens[0][1] == "[":
        result.append(to_xml(tokens.pop(0), indent))
        compile_expression(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    compile_expression(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("letStatement", indent - 1))


def compile_if_statement(tokens, result, indent):
    """
    <ifStatement> =>
        'if' '(' <expression> ')' '{' statements> '}'
        ('else' '{' statements> '}')?
    """
    result.append(opening("ifStatement", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    compile_expression(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    compile_statements(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    if tokens[0][1] == "else":
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        compile_statements(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("ifStatement", indent - 1))


def compile_while_statement(tokens, result, indent):
    """
    <whileStatement> =>
        'while' '(' <expression> ')' '{' statements> '}'
        ('else' '{' statements> '}')?
    """
    result.append(opening("whileStatement", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    compile_expression(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    compile_statements(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    if tokens[0][1] == "else":
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        compile_statements(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("whileStatement", indent - 1))


def compile_do_statement(tokens, result, indent):
    """
    <doStatement> =>
        'do' (identifier '.')? identifier '(' <expressionList> ')' ';'
    """
    result.append(opening("doStatement", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))
    if tokens[1][1] == ".":
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    compile_expression_list(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("doStatement", indent - 1))


def compile_return_statement(tokens, result, indent):
    """
    <returnStatement> =>
        'return' <expression>? ';'
    """
    result.append(opening("returnStatement", indent - 1))
    result.append(to_xml(tokens.pop(0), indent))
    if tokens[0][1] != ";":
        compile_expression(tokens, result, indent + 1)
    result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("returnStatement", indent - 1))


def compile_expression(tokens, result, indent):
    """
    <expression> =>
        <term> (('+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=') <term>)*
    """
    result.append(opening("expression", indent - 1))
    compile_term(tokens, result, indent + 1)
    while tokens[0][1] in ("+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="):
        result.append(to_xml(tokens.pop(0), indent))
        compile_term(tokens, result, indent + 1)
    result.append(closing("expression", indent - 1))


def compile_term(tokens, result, indent):
    """
    <term> =>
        integerConstant | stringConstant | 'true' | 'false' | 'null' | 'this' |
        <varName> | <varName> '[' <expression> ']' | <subroutineCall> |
        '(' <expression> ')' | '-' | '~' <term>
    """
    result.append(opening("term", indent - 1))
    if tokens[0][1] == "(":
        result.append(to_xml(tokens.pop(0), indent))
        compile_expression(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
    elif tokens[0][1] in ("-", "~"):
        result.append(to_xml(tokens.pop(0), indent))
        compile_term(tokens, result, indent + 1)
    elif tokens[1][1] == "[":
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        compile_expression(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
    elif tokens[1][1] in ("(", "."):
        if tokens[1][1] == ".":
            result.append(to_xml(tokens.pop(0), indent))
            result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        result.append(to_xml(tokens.pop(0), indent))
        compile_expression_list(tokens, result, indent + 1)
        result.append(to_xml(tokens.pop(0), indent))
    else:
        result.append(to_xml(tokens.pop(0), indent))
    result.append(closing("term", indent - 1))


def compile_expression_list(tokens, result, indent):
    """
    <expressionList> =>
        (<expression> (',' <expression>)* )?
    """
    result.append(opening("expressionList", indent - 1))
    if tokens[0][1] != ")":
        compile_expression(tokens, result, indent + 1)
        while tokens[0][1] == ",":
            result.append(to_xml(tokens.pop(0), indent))
            compile_expression(tokens, result, indent + 1)
    result.append(closing("expressionList", indent - 1))

