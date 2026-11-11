package toy.math;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FractionTest {
    @Test void normalize() { assertEquals(new Fraction(1, 2), new Fraction(-2, -4)); }
    @Test void add() { assertEquals(new Fraction(5, 6), new Fraction(1, 2).add(new Fraction(1, 3))); }
    @Test void mul() { assertEquals(new Fraction(1, 6), new Fraction(1, 2).mul(new Fraction(1, 3))); }
    @Test void zero() { assertThrows(ArithmeticException.class, () -> new Fraction(1, 0)); }
    @Test void str() { assertEquals("3", new Fraction(6, 2).toString()); }
}
