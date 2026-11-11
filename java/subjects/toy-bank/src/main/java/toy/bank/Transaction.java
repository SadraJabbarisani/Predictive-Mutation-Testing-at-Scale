package toy.bank;

public class Transaction {
    final String from;
    final String to;
    final long amount;

    Transaction(String from, String to, long amount) {
        this.from = from;
        this.to = to;
        this.amount = amount;
    }

    public boolean isLarge() { return amount >= 10_000; }

    @Override
    public String toString() { return from + "->" + to + ":" + amount; }
}
