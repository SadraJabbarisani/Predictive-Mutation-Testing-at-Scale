package toy.date;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DateTest {
    @Test void leap() { assertTrue(SimpleDate.isLeap(2000)); assertFalse(SimpleDate.isLeap(1900)); assertTrue(SimpleDate.isLeap(2024)); }
    @Test void doy() { assertEquals(60, new SimpleDate(2024, 2, 29).dayOfYear()); }
    @Test void plus() {
        SimpleDate d = new SimpleDate(2023, 12, 30).plusDays(3);
        assertEquals(2024, d.year);
        assertEquals(1, d.month);
    }
    @Test void before() { assertTrue(new SimpleDate(2020, 1, 1).isBefore(new SimpleDate(2020, 1, 2))); }
    @Test void fmt() { assertEquals("1 hour, 1 second", DurationFormatter.format(3601)); }
}
