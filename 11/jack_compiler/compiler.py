from tokenizer import tokenize
from dataclasses import dataclass

__all__ = ["JackCompiler"]


@dataclass
class Identifier:
    name: str
    type: str
    kind: str
    index: int


@dataclass
class Class:
    name: str
    symbols: dict


@dataclass
class Subroutine:
    name: str
    type: str
    kind: str
    symbols: dict


op_map = dict(
    zip(
        ("+", "-", "*", "/", "&", "|", "<", ">", "="),
        (
            "add",
            "sub",
            "call Math.multiply 2",
            "call Math.divide 2",
            "and",
            "or",
            "lt",
            "gt",
            "eq",
        ),
    )
)


def call(op):
    return f"{op_map[op]}"


def num_fields(symbols):
    return len([symbol for symbol in symbols.values() if symbol.kind == "field"])


class JackCompiler:
    def __init__(self, source_code):
        self.source_code = source_code
        self.INDECES = {"field": -1, "static": -1, "local": -1, "argument": -1}
        self.CLASS = Class("", {})
        self.SUBROUTINE = Subroutine("", "", "", {})
        self.suffices = {}

    def next_index(self, kind):
        self.INDECES.update({kind: self.INDECES[kind] + 1})
        return self.INDECES.get(kind)

    def reset_index(self, kind):
        self.INDECES.update({kind: -1})

    def next_label(self, suffix):
        if not self.suffices.get(suffix):
            self.suffices.update({suffix: 0})
        l = f"{suffix}{self.suffices[suffix]}"
        self.suffices.update({suffix: self.suffices[suffix] + 1})
        return l

    def compile(self):
        tokens = list(reversed(list(tokenize(self.source_code))))
        return self.compile_class(tokens, result=[])

    def compile_class(self, tokens, result):
        """
        <class> =>
            'class' identifier '{' <classVarDec>* <subroutineDec>* '}'
        """
        tokens.pop()
        self.CLASS.name = tokens.pop()[1]
        tokens.pop()
        self.compile_class_var_dec(tokens, result)
        self.compile_subroutine_dec(tokens, result)
        tokens.pop()
        return result

    def compile_class_var_dec(self, tokens, result):
        """
        <classVarDec> =>
            ('static' | 'field') ('int' | 'char' | 'boolean' | identifier) identifier (',' identifier)* ';'

        """
        while tokens[-1][1] in ("static", "field"):
            kind = tokens.pop()[1]
            type = tokens.pop()[1]
            name = tokens.pop()[1]
            self.CLASS.symbols.update(
                {name: Identifier(name, type, kind, self.next_index(kind))}
            )
            while tokens[-1][1] == ",":
                tokens.pop()
                name = tokens.pop()[1]
                self.CLASS.symbols.update(
                    {name: Identifier(name, type, kind, self.next_index(kind))}
                )
            tokens.pop()

    def compile_subroutine_dec(self, tokens, result):
        """
        <subroutineDec> =>
            ('constructor' | 'function' | 'method')
            ('void' | 'int' | 'char' | 'boolean' | identifier) identifier '(' <parameterList> ')'
            <subroutineBody>
        """
        while tokens[-1][1] in ("constructor", "function", "method"):
            self.SUBROUTINE.kind = tokens.pop()[1]
            self.SUBROUTINE.type = tokens.pop()[1]
            self.SUBROUTINE.name = tokens.pop()[1]
            self.SUBROUTINE.symbols = {}
            tokens.pop()
            self.compile_parameter_list(tokens, result)
            tokens.pop()
            self.compile_subroutine_body(tokens, result)
            self.SUBROUTINE = Subroutine("", "", "", {})

    def compile_parameter_list(self, tokens, result):
        """
        <parameterList> =>
            (<type> identifier (',' <type> identifier)* )?
        """
        if self.SUBROUTINE.kind == "method":
            self.next_index("argument")  # start argument at 1 instead of 0
        while tokens[-1][1] != ")":
            type = tokens.pop()[1]
            name = tokens.pop()[1]
            self.SUBROUTINE.symbols.update(
                {name: Identifier(name, type, "argument", self.next_index("argument"))}
            )
            while tokens[-1][1] == ",":
                tokens.pop()
                type = tokens.pop()[1]
                name = tokens.pop()[1]
                self.SUBROUTINE.symbols.update(
                    {
                        name: Identifier(
                            name, type, "argument", self.next_index("argument")
                        )
                    }
                )

    def compile_subroutine_body(self, tokens, result):
        """
        <subroutineBody> =>
            '{' <varDec>* <statements> '}'
        """
        tokens.pop()
        var_count = self.compile_var_dec(tokens, result)
        result.append(f"function {self.CLASS.name}.{self.SUBROUTINE.name} {var_count}")
        if self.SUBROUTINE.kind == "constructor":
            result.append(f"push constant {num_fields(self.CLASS.symbols)}")
            result.append(f"call Memory.alloc 1")
            result.append(f"pop pointer 0")
        elif self.SUBROUTINE.kind == "method":
            result.append(f"push argument 0")
            result.append(f"pop pointer 0")
        self.compile_statements(tokens, result)
        tokens.pop()

    def compile_var_dec(self, tokens, result):
        """
        Spec:
        <varDec> =>
            'var' ('int' | 'char' | 'boolean' | identifier) identifier (',' identifier)* ';'
        
        return: number of local variables
        """
        count = 0
        while tokens[-1][1] == "var":
            tokens.pop()
            type = tokens.pop()[1]
            name = tokens.pop()[1]
            self.SUBROUTINE.symbols.update(
                {name: Identifier(name, type, "local", self.next_index("local"))}
            )
            count += 1
            while tokens[-1][1] == ",":
                tokens.pop()
                name = tokens.pop()[1]
                self.SUBROUTINE.symbols.update(
                    {name: Identifier(name, type, "local", self.next_index("local"))}
                )
                count += 1
            tokens.pop()
        self.reset_index("local")
        self.reset_index("argument")
        return count

    def compile_statements(self, tokens, result):
        """
        <statements> =>
            ( <letStatement> 
            | <ifStatement> 
            | <whileStatement> 
            | <doStatement> 
            | <returnStatement>
            )*
        """
        while tokens[-1][1] in ("let", "if", "while", "do", "return"):
            _, value = tokens[-1]
            if value == "let":
                self.compile_let_statement(tokens, result)
            elif value == "if":
                self.compile_if_statement(tokens, result)
            elif value == "while":
                self.compile_while_statement(tokens, result)
            elif value == "do":
                self.compile_do_statement(tokens, result)
            elif value == "return":
                self.compile_return_statement(tokens, result)

    def compile_let_statement(self, tokens, result):
        """
        <letStatement> =>
            'let' identifier ('[' <expression> ']')? '=' <expression> ';'
        """
        tokens.pop()
        name = tokens.pop()[1]
        identifier = self.SUBROUTINE.symbols.get(name) or self.CLASS.symbols.get(name)
        is_array = False
        if tokens[-1][1] == "[":
            is_array = True
            tokens.pop()
            self.compile_expression(tokens, result)
            result.append(
                f"push {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
            )
            result.append(f"add")
            # result.append(f"pop pointer 1")
            tokens.pop()
        tokens.pop()
        self.compile_expression(tokens, result)
        if is_array:
            result.append("pop temp 0")
            result.append("pop pointer 1")
            result.append("push temp 0")
            result.append(f"pop that 0")
        else:
            result.append(
                f"pop {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
            )
        tokens.pop()

    def compile_if_statement(self, tokens, result):
        """
        <ifStatement> =>
            'if' '(' <expression> ')' '{' <statements> '}'
            ('else' '{' statements> '}')?
        """

        THEN = self.next_label("THEN")
        ELSE = self.next_label("ELSE")
        tokens.pop()
        tokens.pop()
        self.compile_expression(tokens, result)
        result.append(f"if-goto {THEN}")
        result.append(f"goto {ELSE}")
        tokens.pop()
        tokens.pop()
        result.append(f"label {THEN}")
        self.compile_statements(tokens, result)
        tokens.pop()
        if tokens[-1][1] == "else":
            ENDIF = self.next_label("ENDIF")
            result.append(f"goto {ENDIF}")
            result.append(f"label {ELSE}")
            tokens.pop()
            tokens.pop()
            self.compile_statements(tokens, result)
            tokens.pop()
            result.append(f"label {ENDIF}")
        else:
            result.append(f"label {ELSE}")

    def compile_while_statement(self, tokens, result):
        """
        <whileStatement> =>
            'while' '(' <expression> ')' '{' <statements> '}'
        """
        WHILE = self.next_label("WHILE")
        ENDWHILE = self.next_label("ENDWHILE")
        tokens.pop()
        tokens.pop()
        result.append(f"label {WHILE}")
        self.compile_expression(tokens, result)
        result.append(f"not")
        tokens.pop()
        tokens.pop()
        result.append(f"if-goto {ENDWHILE}")
        self.compile_statements(tokens, result)
        result.append(f"goto {WHILE}")
        tokens.pop()
        result.append(f"label {ENDWHILE}")

    def compile_do_statement(self, tokens, result):
        """
        <doStatement> =>
            'do' (identifier '.')? identifier '(' <expressionList> ')' ';'
        """
        tokens.pop()
        prefix = None
        if tokens[-2][1] == ".":
            prefix = tokens.pop()[1]
            tokens.pop()
        function_name = tokens.pop()[1]
        tokens.pop()
        if prefix:
            identifier = self.SUBROUTINE.symbols.get(prefix) or self.CLASS.symbols.get(
                prefix
            )
            if identifier:
                result.append(
                    f"push {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
                )
                arg_count = self.compile_expression_list(tokens, result)
                result.append(f"call {identifier.type}.{function_name} {arg_count + 1}")
            else:
                arg_count = self.compile_expression_list(tokens, result)
                result.append(f"call {prefix}.{function_name} {arg_count}")
        else:
            result.append(f"push pointer 0")
            arg_count = self.compile_expression_list(tokens, result)
            result.append(f"call {self.CLASS.name}.{function_name} {arg_count + 1}")
        result.append(f"pop temp 0")
        tokens.pop()
        tokens.pop()

    def compile_return_statement(self, tokens, result):
        """
        <returnStatement> =>
            'return' <expression>? ';'
        """
        tokens.pop()
        if tokens[-1][1] == ";":
            result.append(f"push constant 0")
        else:
            self.compile_expression(tokens, result)
        result.append(f"return")
        tokens.pop()

    def compile_expression(self, tokens, result):
        """
        <expression> =>
            <term> (('+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=') <term>)*
        """
        self.compile_term(tokens, result)
        while tokens[-1][1] in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            op = tokens.pop()[1]
            self.compile_term(tokens, result)
            result.append(call(op))

    def compile_term(self, tokens, result):
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
        if tokens[-1][1] == "(":
            tokens.pop()
            self.compile_expression(tokens, result)
            tokens.pop()
        elif tokens[-1][1] in ("-", "~"):
            unary_op = tokens.pop()[1]
            self.compile_term(tokens, result)
            result.append(f"{'neg' if unary_op == '-' else 'not'}")
        elif tokens[-2][1] == "[":
            name = tokens.pop()[1]
            tokens.pop()
            self.compile_expression(tokens, result)
            tokens.pop()
            identifier = self.SUBROUTINE.symbols.get(name) or self.CLASS.symbols.get(
                name
            )
            result.append(
                f"push {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
            )
            result.append(f"add")
            result.append(f"pop pointer 1")
            result.append(f"push that 0")
        elif tokens[-2][1] in ("(", "."):
            prefix = None
            if tokens[-2][1] == ".":
                prefix = tokens.pop()[1]
                tokens.pop()
            function_name = tokens.pop()[1]
            tokens.pop()
            if prefix:
                identifier = self.SUBROUTINE.symbols.get(
                    prefix
                ) or self.CLASS.symbols.get(prefix)
                if identifier:
                    result.append(
                        f"push {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
                    )
                    arg_count = self.compile_expression_list(tokens, result)
                    result.append(
                        f"call {identifier.type}.{function_name} {arg_count + 1}"
                    )
                else:
                    arg_count = self.compile_expression_list(tokens, result)
                    result.append(f"call {prefix}.{function_name} {arg_count}")
            else:
                result.append(f"push pointer 0")
                arg_count = self.compile_expression_list(tokens, result)
                result.append(f"call {self.CLASS.name}.{function_name} {arg_count + 1}")
                self.compile_expression_list(tokens, result)
            tokens.pop()
        else:
            type_, terminal = tokens.pop()
            if terminal in self.SUBROUTINE.symbols:
                identifier = self.SUBROUTINE.symbols.get(terminal)
                result.append(
                    f"push {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
                )
            elif terminal in self.CLASS.symbols:
                identifier = self.CLASS.symbols.get(terminal)
                result.append(
                    f"push {'this' if identifier.kind == 'field' else identifier.kind} {identifier.index}"
                )
            elif terminal in ("false", "null"):
                result.append(f"push constant 0")
            elif terminal == "true":
                result.append(f"push constant 0")
                result.append(f"not")
            elif terminal == "this":
                result.append(f"push pointer 0")
            elif type_ == "integerConstant":
                result.append(f"push constant {terminal}")
            else:
                result.append(f"push constant {len(terminal)}")
                result.append(f"call String.new 1")
                for c in terminal:
                    result.append(f"push constant {ord(c)}")
                    result.append(f"call String.appendChar 2")

    def compile_expression_list(self, tokens, result):
        """
        <expressionList> =>
            (<expression> (',' <expression>)* )?
        """
        count = 0
        if tokens[-1][1] != ")":
            self.compile_expression(tokens, result)
            count += 1
            while tokens[-1][1] == ",":
                tokens.pop()
                self.compile_expression(tokens, result)
                count += 1
        return count
