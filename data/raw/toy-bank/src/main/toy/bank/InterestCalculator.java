package toy.bank;

public class InterestCalculator {
    /** Annual rate in basis points depending on balance tier. */
    public static int rateBps(long balance) {
        if (balance < 1_000) return 50;
        else if (balance < 10_000) return 150;
        else if (balance < 100_000) return 250;
        return 300;
    }

    public static long yearlyInterest(long balance) {
        return balance * rateBps(balance) / 10_000;
    }

    public static long compound(long principal, int years) {
        long p = principal;
        for (int i = 0; i < years; i++) {
            p += yearlyInterest(p);
        }
        return p;
    }

    public static int yearsToDouble(long principal) {
        if (principal <= 0) return -1;
        long p = principal;
        int y = 0;
        while (p < 2 * principal && y < 1000) {
            p += yearlyInterest(p);
            y++;
        }
        return y;
    }
}
