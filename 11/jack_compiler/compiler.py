from tokenizer import tokenize
from dataclasses import dataclass

__all__ = ["JackCompiler"]


@dataclass
class Identifier:
    name: str
    type: str
    kind: str
    index: int


class JackCompiler:
    current_index_of_kinds = {"field": 0, "static": 0, "local": 0, "argument": 0}

    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = tokenize(source_code)
        self.class_name = ""
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.current_subroutine_name = ""
        self.current_subroutine_kind = ""
        self.current_subroutine_type = ""

    def __call__(self):
        return self.compile_class(result=[])

    def ignore_token(self, *args):
        self.tokens.pop(0)

    @staticmethod
    def get_index(kind):
        """SIDE-EFFECT: increments the index corresponding to kind."""
        old_index = JackCompiler.current_index_of_kinds.get(kind)
        JackCompiler.current_index_of_kinds.update({kind: old_index + 1})
        return old_index

    @staticmethod
    def reset_index(kind):
        JackCompiler.current_index_of_kinds.update({kind: 0})

    def compile_class(self, result):
        """
        <class> =>
            'class' identifier '{' <classVarDec>* <subroutineDec>* '}'
        """
        self.ignore_token("class")
        self.class_name = self.tokens.pop(0)
        self.ignore_token("{")
        compile_class_var_dec(self.tokens, result)
        compile_subroutine_dec(self.tokens, result)
        self.ignore_token("}")
        return result

    def compile_class_var_dec(self, result):
        """
        <classVarDec> =>
            ('static' | 'field') ('int' | 'char' | 'boolean' | identifier) identifier (',' identifier)* ';'

        """
        while self.tokens[0][1] in ("static", "field"):
            kind = self.tokens.pop(0)
            type_ = self.tokens.pop(0)
            name = self.tokens.pop(0)
            self.class_symbols.update(
                {name: Identifier(name, type_, kind, JackCompiler.get_index(kind))}
            )
            while self.tokens[0][1] == ",":
                self.ignore_token(",")
                name = self.tokens.pop(0)
                self.class_symbols.update(
                    {name: Identifier(name, type_, kind, JackCompiler.get_index(kind))}
                )
            self.ignore_token(";")

    def compile_subroutine_dec(self, result):
        """
        <subroutineDec> =>
            ('constructor' | 'function' | 'method')
            ('void' | 'int' | 'char' | 'boolean' | identifier) identifier '(' <parameterList> ')'
            <subroutineBody>
        """
        while self.tokens[0][1] in ("constructor", "function", "method"):
            self.current_subroutine_kind = self.tokens.pop(0)
            self.current_subroutine_type = self.tokens.pop(0)
            self.current_subroutine_name = self.tokens.pop(0)
            self.subroutine_symbols = {}  # start new subroutine symbol table
            self.ignore_token("(")
            compile_parameter_list(self.tokens, result)
            self.ignore_token(")")
            compile_subroutine_body(self.tokens, result)

    def compile_parameter_list(self, result):
        """
        <parameterList> =>
            (<type> identifier (',' <type> identifier)* )?
        """
        while self.tokens[0][1] != ")":
            type_ = self.tokens.pop(0)  # type
            name = self.tokens.pop(0)  # name
            self.subroutine_symbols.update(
                {
                    name: Identifier(
                        name, type_, "argument", JackCompiler.get_index("argument")
                    )
                }
            )
            while self.tokens[0][1] == ",":
                self.ignore_token(",")
                type_ = self.tokens.pop(0)  # type
                name = self.tokens.pop(0)  # name
                self.subroutine_symbols.update(
                    {
                        name: Identifier(
                            name, type_, "argument", JackCompiler.get_index("argument")
                        )
                    }
                )

    def compile_subroutine_body(self, result):
        """
        <subroutineBody> =>
            '{' <varDec>* <statements> '}'
        """
        self.ignore_token("{")
        compile_var_dec(self.tokens, result)
        compile_statements(self.tokens, result)
        self.ignore_token("}")

    def compile_var_dec(self, result):
        """
        <varDec> =>
            'var' ('int' | 'char' | 'boolean' | identifier) identifier (',' identifier)* ';'
        """
        while self.tokens[0][1] == "var":
            self.ignore_token("var")
            type_ = self.tokens.pop(0)
            name = self.tokens.pop(0)
            self.subroutine_symbols.update(
                {
                    name: Identifier(
                        name, type_, "local", JackCompiler.get_index("local")
                    )
                }
            )
            while self.tokens[0][1] == ",":
                self.ignore_token(",")
                type_ = self.tokens.pop(0)  # type
                name = self.tokens.pop(0)  # name
                self.subroutine_symbols.update(
                    {
                        name: Identifier(
                            name, type_, "local", JackCompiler.get_index("local")
                        )
                    }
                )
            self.ignore_token(";")
        JackCompiler.reset_index("local")
        JackCompiler.reset_index("argument")

    def compile_statements(self, result):
        """
        <statements> =>
            ( <letStatement> 
            | <ifStatement> 
            | <whileStatement> 
            | <doStatement> 
            | <returnStatement>
            )*
        """
        while self.tokens[0][1] in ("let", "if", "while", "do", "return"):
            kind, value = self.tokens[0]
            if value == "let":
                compile_let_statement(self.tokens, result)
            elif value == "if":
                compile_if_statement(self.tokens, result)
            elif value == "while":
                compile_while_statement(self.tokens, result)
            elif value == "do":
                compile_do_statement(self.tokens, result)
            elif value == "return":
                compile_return_statement(self.tokens, result)

    def compile_let_statement(self, result):
        """
        <letStatement> =>
            'let' identifier ('[' <expression> ']')? '=' <expression> ';'
        """
        self.ignore_token("let")
        identifier = self.subroutine_symbols.get(self.tokens.pop(0))
        if self.tokens[0][1] == "[":
            is_array = True
            self.ignore_token("[")
            result.append(f"push {identifier.kind} {identifier.index}")
            compile_expression(self.tokens, result)
            result.append(f"add")
            result.append(f"pop pointer 1")
            self.ignore_token("]")
        self.ignore_token('=')
        compile_expression(self.tokens, result)
        if is_array:
            result.append(f"pop that 0")
        else:
            result.append(f"pop {identifier.kind} {identifier.index}")
        self.ignore_token(";")

    def compile_if_statement(self, result):
        """
        <ifStatement> =>
            'if' '(' <expression> ')' '{' <statements> '}'
            ('else' '{' statements> '}')?
        """
        result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))
        compile_expression(self.tokens, result)
        result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))
        compile_statements(self.tokens, result)
        result.append(self.tokens.pop(0))
        if self.tokens[0][1] == "else":
            result.append(self.tokens.pop(0))
            result.append(self.tokens.pop(0))
            compile_statements(self.tokens, result)
            result.append(self.tokens.pop(0))

    def compile_while_statement(self, result):
        """
        <whileStatement> =>
            'while' '(' <expression> ')' '{' <statements> '}'
            ('else' '{' statements> '}')?
        """
        result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))
        compile_expression(self.tokens, result)
        result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))
        compile_statements(self.tokens, result)
        result.append(self.tokens.pop(0))
        if self.tokens[0][1] == "else":
            result.append(self.tokens.pop(0))
            result.append(self.tokens.pop(0))
            compile_statements(self.tokens, result)
            result.append(self.tokens.pop(0))

    def compile_do_statement(self, result):
        """
        <doStatement> =>
            'do' (identifier '.')? identifier '(' <expressionList> ')' ';'
        """
        result.append(self.tokens.pop(0))
        if self.tokens[1][1] == ".":
            result.append(self.tokens.pop(0))
            result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))
        compile_expression_list(self.tokens, result)
        result.append(self.tokens.pop(0))
        result.append(self.tokens.pop(0))

    def compile_return_statement(self, result):
        """
        <returnStatement> =>
            'return' <expression>? ';'
        """
        result.append(self.tokens.pop(0))
        if self.tokens[0][1] != ";":
            compile_expression(self.tokens, result)
        result.append(self.tokens.pop(0))

    def compile_expression(self, result):
        """
        <expression> =>
            <term> (('+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=') <term>)*
        """
        compile_term(self.tokens, result)
        while self.tokens[0][1] in (
            "+",
            "-",
            "*",
            "/",
            "&amp;",
            "|",
            "&lt;",
            "&gt;",
            "=",
        ):
            result.append(self.tokens.pop(0))
            compile_term(self.tokens, result)

    def compile_term(self, result):
        """
        <term> =>
            ( integerConstant 
            | stringConstant 
            | 'true' 
            | 'false' 
            | 'null' 
            | 'this' 
            | <varName> 
            | <varName> '[' <expression> ']' 
            | (identifier '.')? identifier '(' <expressionList> ')' 
            | '(' <expression> ')' 
            | ('-' | '~') <term> 
            )
        """
        if self.tokens[0][1] == "(":
            result.append(self.tokens.pop(0))
            compile_expression(self.tokens, result)
            result.append(self.tokens.pop(0))
        elif self.tokens[0][1] in ("-", "~"):
            result.append(self.tokens.pop(0))
            compile_term(self.tokens, result)
        elif self.tokens[1][1] == "[":
            result.append(self.tokens.pop(0))
            result.append(self.tokens.pop(0))
            compile_expression(self.tokens, result)
            result.append(self.tokens.pop(0))
        elif self.tokens[1][1] in ("(", "."):
            if self.tokens[1][1] == ".":
                result.append(self.tokens.pop(0))
                result.append(self.tokens.pop(0))
            result.append(self.tokens.pop(0))
            result.append(self.tokens.pop(0))
            compile_expression_list(self.tokens, result)
            result.append(self.tokens.pop(0))
        else:
            result.append(self.tokens.pop(0))

    def compile_expression_list(self, result):
        """
        <expressionList> =>
            (<expression> (',' <expression>)* )?
        """
        if self.tokens[0][1] != ")":
            compile_expression(self.tokens, result)
            while self.tokens[0][1] == ",":
                result.append(self.tokens.pop(0))
                compile_expression(self.tokens, result)
