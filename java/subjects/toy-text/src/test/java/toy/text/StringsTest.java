package toy.text;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class StringsTest {
    @Test void reverse() { assertEquals("cba", Strings.reverse("abc")); assertNull(Strings.reverse(null)); }
    @Test void palindrome() { assertTrue(Strings.isPalindrome("A man, a plan, a canal: Panama")); assertFalse(Strings.isPalindrome("abc")); }
    @Test void words() { assertEquals(3, Strings.wordCount(" a b  c ")); assertEquals(0, Strings.wordCount("  ")); }
    @Test void capitalize() { assertEquals("Hello World", Strings.capitalize("hELLO world")); }
    @Test void caesar() { assertEquals("bcd", Strings.caesar("abc", 1)); assertEquals("zab", Strings.caesar("abc", -1)); }
    @Test void truncateRuns() { assertNotNull(Strings.truncate("hello world", 8)); }
}
