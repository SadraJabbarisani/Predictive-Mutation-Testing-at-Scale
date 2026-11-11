package toy.inv;

public class Shipping {
    public static long cost(long amount, int items) {
        if (amount >= 10_000) return 0;
        long base = 500;
        if (items > 5) base += (items - 5) * 50L;
        return base;
    }
}
