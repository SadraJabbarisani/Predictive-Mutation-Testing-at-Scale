package toy.math;

import java.util.ArrayList;
import java.util.List;

public class Primes {
    public static boolean isPrime(long n) {
        if (n < 2) return false;
        if (n % 2 == 0) return n == 2;
        for (long i = 3; i * i <= n; i += 2) if (n % i == 0) return false;
        return true;
    }
    public static List<Integer> sieve(int n) {
        boolean[] comp = new boolean[n + 1];
        List<Integer> r = new ArrayList<>();
        for (int i = 2; i <= n; i++) {
            if (!comp[i]) {
                r.add(i);
                for (long j = (long) i * i; j <= n; j += i) comp[(int) j] = true;
            }
        }
        return r;
    }
    public static List<Long> factorize(long n) {
        List<Long> f = new ArrayList<>();
        for (long p = 2; p * p <= n; p++) {
            while (n % p == 0) { f.add(p); n /= p; }
        }
        if (n > 1) f.add(n);
        return f;
    }
}
