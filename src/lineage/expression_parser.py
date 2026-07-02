"""Recoverable parsing and variable extraction using generated ANTLR code."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from antlr4 import CommonTokenStream, InputStream, Token
from antlr4.error.ErrorListener import ErrorListener

from .generated.LineageLexer import LineageLexer
from .generated.LineageParser import LineageParser
from .generated.LineageVisitor import LineageVisitor


@dataclass(frozen=True, slots=True)
class SyntaxIssue:
    """One lexer/parser diagnostic; columns use ANTLR's zero-based convention."""

    line: int
    column: int
    offending_token: str | None
    message: str

    def render(self) -> str:
        token = (
            f" near {self.offending_token!r}"
            if self.offending_token is not None
            else ""
        )
        return f"line {self.line}, column {self.column}{token}: {self.message}"


@dataclass(frozen=True, slots=True)
class ParseSuccess:
    """A valid expression and its distinct referenced identifiers."""

    expression: str
    variables: frozenset[str]

    @property
    def ok(self) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class ParseFailure:
    """A recoverable failure that preserves the offending input and details."""

    expression: str
    message: str
    issues: tuple[SyntaxIssue, ...]

    @property
    def ok(self) -> bool:
        return False


ParseResult: TypeAlias = ParseSuccess | ParseFailure


class _CollectingErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.issues: list[SyntaxIssue] = []

    # Signature is dictated by antlr4.error.ErrorListener.ErrorListener.
    def syntaxError(  # noqa: N802 - ANTLR API name
        self,
        recognizer: object,
        offendingSymbol: object | None,
        line: int,
        column: int,
        msg: str,
        e: Exception | None,
    ) -> None:
        del recognizer, e
        token_text = getattr(offendingSymbol, "text", None)
        self.issues.append(
            SyntaxIssue(
                line=line,
                column=column,
                offending_token=token_text,
                message=msg,
            )
        )


class _VariableCollector(LineageVisitor):
    """Iteratively visits grammar ``Var`` alternatives; constants add nothing.

    ANTLR's default visitor recursively follows the parse tree. A long flat
    expression produces a left-deep tree and can exceed Python's recursion
    limit even though the expression is valid, so this visitor keeps its own
    explicit stack.
    """

    def __init__(self) -> None:
        super().__init__()
        self.variables: set[str] = set()

    def visit(self, tree: object) -> set[str]:
        stack = [tree]
        while stack:
            current = stack.pop()
            if isinstance(current, LineageParser.VarContext):
                self.visitVar(current)
                continue

            children = getattr(current, "children", None)
            if children:
                stack.extend(reversed(children))
        return self.variables

    def visitVar(self, ctx: LineageParser.VarContext) -> None:  # noqa: N802
        self.variables.add(ctx.IDENTIFIER().getText())


class ExpressionParser:
    """Stateless facade around a fresh ANTLR lexer/parser per expression."""

    def parse(self, expression: str) -> ParseResult:
        if not isinstance(expression, str):
            rendered = "" if expression is None else str(expression)
            issue = SyntaxIssue(
                line=1,
                column=0,
                offending_token=None,
                message="expression must be a string",
            )
            return ParseFailure(rendered, issue.render(), (issue,))

        lexer_errors = _CollectingErrorListener()
        parser_errors = _CollectingErrorListener()

        try:
            lexer = LineageLexer(InputStream(expression))
            lexer.removeErrorListeners()
            lexer.addErrorListener(lexer_errors)

            tokens = CommonTokenStream(lexer)
            # Lex the complete input now, so an illegal character after a valid
            # prefix cannot escape detection.
            tokens.fill()
            tokens.seek(0)

            parser = LineageParser(tokens)
            parser.removeErrorListeners()
            parser.addErrorListener(parser_errors)
            tree = parser.expr()

            issues = [*lexer_errors.issues, *parser_errors.issues]

            # The supplied grammar deliberately has no ``expr EOF`` root rule.
            # ANTLR would otherwise accept a valid prefix such as ``a b``.
            if tokens.LA(1) != Token.EOF:
                token = tokens.LT(1)
                issues.append(
                    SyntaxIssue(
                        line=token.line,
                        column=token.column,
                        offending_token=token.text,
                        message="unexpected trailing token",
                    )
                )

            if issues:
                rendered = "; ".join(issue.render() for issue in issues)
                return ParseFailure(expression, rendered, tuple(issues))

            collector = _VariableCollector()
            collector.visit(tree)
            return ParseSuccess(expression, frozenset(collector.variables))
        except Exception as exc:  # ANTLR failures must not cross this boundary.
            issue = SyntaxIssue(
                line=1,
                column=0,
                offending_token=None,
                message=f"parser failed safely: {type(exc).__name__}: {exc}",
            )
            return ParseFailure(expression, issue.render(), (issue,))
