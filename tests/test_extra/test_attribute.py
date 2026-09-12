"""Test attribute selectors."""
import signal
import time
from .. import util
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_syntax_error_in_time(self, selector, timeout=3):
        """Assert the selector fails with a syntax error instead of hanging the parser."""

        if hasattr(signal, 'SIGALRM'):
            # POSIX: interrupt a runaway pattern with an alarm.
            def timeout_handler(signum, frame):
                """Raise a timeout error when the alarm fires."""

                raise TimeoutError

            original = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            passed = False
            try:
                with self.assertRaises(sv.SelectorSyntaxError):
                    sv.compile(selector)
                passed = True
            except TimeoutError:
                pass
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original)
            self.assertTrue(passed)
        else:
            # Windows has no `SIGALRM`, so just time the (failing) compile.
            start = time.time()
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile(selector)
            self.assertTrue((time.time() - start) < timeout)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_in_time('[a="' + ('x' * 300))

    def test_bad_attribute_unclused_single_quote(self):
        """Test bad attribute (single quote) fails for syntax error, not timeout error."""

        self.assert_syntax_error_in_time("[a='" + ('x' * 300))
