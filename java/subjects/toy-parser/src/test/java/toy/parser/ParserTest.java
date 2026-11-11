package toy.parser;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class ParserTest {
    @Test void calc() {
        Calculator c = new Calculator();
        assertEquals(7, c.eval("1 + 2 * 3"));
        assertEquals(9, c.eval("(1+2)*3"));
        assertEquals(-1, c.eval("2-3"));
        assertThrows(ArithmeticException.class, () -> c.eval("1/0"));
    }
    @Test void roman() {
        assertEquals("MCMXCIV", Roman.toRoman(1994));
        assertEquals(1994, Roman.fromRoman("MCMXCIV"));
    }
    @Test void csv() {
        assertEquals(List.of("a", "b,c", ""), CsvLine.parse("a,\"b,c\",", ','));
    }
}
