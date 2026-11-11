package toy.math;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class PrimesStatsTest {
    @Test void primes() { assertTrue(Primes.isPrime(97)); assertFalse(Primes.isPrime(91)); assertTrue(Primes.isPrime(2)); }
    @Test void sieve() { assertEquals(List.of(2, 3, 5, 7), Primes.sieve(10)); }
    @Test void factor() { assertEquals(List.of(2L, 2L, 3L), Primes.factorize(12)); }
    @Test void mean() { assertEquals(2.0, Stats.mean(new double[]{1, 2, 3}), 1e-9); }
    @Test void median() { assertEquals(2.5, Stats.median(new double[]{4, 1, 2, 3}), 1e-9); }
}
