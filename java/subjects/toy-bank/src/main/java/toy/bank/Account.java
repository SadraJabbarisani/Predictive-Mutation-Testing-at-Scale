package toy.bank;

public class Account {
    private final String id;
    private long balance;
    private boolean frozen;
    private int withdrawalsToday;
    public static final int MAX_DAILY_WITHDRAWALS = 3;

    public Account(String id, long initial) {
        if (id == null || id.isEmpty()) throw new IllegalArgumentException("id");
        if (initial < 0) throw new IllegalArgumentException("negative");
        this.id = id;
        this.balance = initial;
    }

    public String getId() { return id; }
    public long getBalance() { return balance; }
    public boolean isFrozen() { return frozen; }
    public void freeze() { frozen = true; }
    public void unfreeze() { frozen = false; }

    public void deposit(long amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount");
        if (frozen) throw new IllegalStateException("frozen");
        balance += amount;
    }

    public void withdraw(long amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount");
        if (frozen) throw new IllegalStateException("frozen");
        if (withdrawalsToday >= MAX_DAILY_WITHDRAWALS) throw new IllegalStateException("limit");
        if (amount > balance) throw new IllegalStateException("insufficient");
        balance -= amount;
        withdrawalsToday++;
    }

    public void resetDay() { withdrawalsToday = 0; }
    public int getWithdrawalsToday() { return withdrawalsToday; }
}
