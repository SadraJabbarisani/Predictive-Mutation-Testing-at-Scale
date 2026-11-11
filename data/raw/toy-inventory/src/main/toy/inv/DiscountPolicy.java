package toy.inv;

public interface DiscountPolicy {
    long discount(long subtotal, int items);

    static DiscountPolicy none() { return (s, n) -> 0; }

    static DiscountPolicy percentOver(long threshold, int percent) {
        return (s, n) -> s >= threshold ? s * percent / 100 : 0;
    }

    static DiscountPolicy bulk(int minItems, long perItem) {
        return (s, n) -> n >= minItems ? Math.min(s, n * perItem) : 0;
    }
}
