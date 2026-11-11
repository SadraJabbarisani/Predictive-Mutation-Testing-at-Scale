package toy.math;

public final class Fraction implements Comparable<Fraction> {
    public final long num, den;

    public Fraction(long n, long d) {
        if (d == 0) throw new ArithmeticException("zero denominator");
        if (d < 0) { n = -n; d = -d; }
        long g = gcd(Math.abs(n), d);
        num = n / g;
        den = d / g;
    }
    static long gcd(long a, long b) { return b == 0 ? (a == 0 ? 1 : a) : gcd(b, a % b); }
    public Fraction add(Fraction o) { return new Fraction(num * o.den + o.num * den, den * o.den); }
    public Fraction sub(Fraction o) { return new Fraction(num * o.den - o.num * den, den * o.den); }
    public Fraction mul(Fraction o) { return new Fraction(num * o.num, den * o.den); }
    public Fraction div(Fraction o) { return new Fraction(num * o.den, den * o.num); }
    public double value() { return (double) num / den; }
    @Override public int compareTo(Fraction o) { return Long.compare(num * o.den, o.num * den); }
    @Override public boolean equals(Object o) {
        if (!(o instanceof Fraction)) return false;
        Fraction f = (Fraction) o;
        return num == f.num && den == f.den;
    }
    @Override public int hashCode() { return Long.hashCode(num) * 31 + Long.hashCode(den); }
    @Override public String toString() { return den == 1 ? "" + num : num + "/" + den; }
}
