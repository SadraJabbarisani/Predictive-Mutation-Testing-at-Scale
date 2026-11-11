package toy.bank;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class InterestCalculatorTest {
    @Test void tiers() {
        assertEquals(50, InterestCalculator.rateBps(10));
        assertEquals(250, InterestCalculator.rateBps(50_000));
    }
    @Test void compoundGrows() {
        assertTrue(InterestCalculator.compound(1000, 3) > 1000);
    }
}
