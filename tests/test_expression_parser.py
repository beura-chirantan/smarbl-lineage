import unittest

from lineage import ExpressionParser, ParseFailure, ParseSuccess


class ExpressionParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ExpressionParser()

    def assert_variables(self, expression: str, expected: set[str]) -> None:
        result = self.parser.parse(expression)
        self.assertIsInstance(result, ParseSuccess, result)
        assert isinstance(result, ParseSuccess)
        self.assertEqual(result.variables, expected)
        self.assertTrue(result.ok)

    def assert_failure(self, expression: str) -> ParseFailure:
        result = self.parser.parse(expression)
        self.assertIsInstance(result, ParseFailure, result)
        assert isinstance(result, ParseFailure)
        self.assertEqual(result.expression, expression)
        self.assertTrue(result.message)
        self.assertTrue(result.issues)
        self.assertFalse(result.ok)
        return result

    def test_assignment_examples(self) -> None:
        cases = {
            "revenue - cost": {"revenue", "cost"},
            "(price * qty) / 100": {"price", "qty"},
            "if (score >= threshold) then bonus else 0": {
                "score",
                "threshold",
                "bonus",
            },
            "if (x > 0) then x * rate else base + offset": {
                "x",
                "rate",
                "base",
                "offset",
            },
            "42": set(),
        }
        for expression, variables in cases.items():
            with self.subTest(expression=expression):
                self.assert_variables(expression, variables)

    def test_nested_if_decimal_whitespace_and_identifier_forms(self) -> None:
        self.assert_variables(
            """
            if (_score2 >= 10.5) then
              if (flag != 0) then _score2 * rate_1 else fallback
            else base
            """,
            {"_score2", "flag", "rate_1", "fallback", "base"},
        )

    def test_repeated_reference_is_deduplicated(self) -> None:
        self.assert_variables("x + x * x", {"x"})

    def test_long_flat_expression_does_not_hit_recursion_limit(self) -> None:
        variables = [f"x{index}" for index in range(1_200)]
        self.assert_variables(" + ".join(variables), set(variables))

    def test_incomplete_expression_is_recoverable(self) -> None:
        failure = self.assert_failure("if (a +")
        self.assertIn("line 1", failure.message)

    def test_whole_input_must_be_consumed(self) -> None:
        failure = self.assert_failure("a b")
        self.assertIn("trailing token", failure.message)

    def test_lexer_errors_are_not_silently_skipped(self) -> None:
        failure = self.assert_failure("a + $b")
        self.assertIn("token recognition error", failure.message)

    def test_unsupported_language_constructs_fail(self) -> None:
        for expression in ("", "-1", ".5", "1.", "a > b", "sum(a)"):
            with self.subTest(expression=expression):
                self.assert_failure(expression)

    def test_parser_remains_usable_after_a_failure(self) -> None:
        self.assert_failure("if (")
        self.assert_variables("healthy + value", {"healthy", "value"})

    def test_non_string_input_becomes_failure_instead_of_throwing(self) -> None:
        result = self.parser.parse(None)  # type: ignore[arg-type]
        self.assertIsInstance(result, ParseFailure)
        self.assertIn("must be a string", result.message)


if __name__ == "__main__":
    unittest.main()
