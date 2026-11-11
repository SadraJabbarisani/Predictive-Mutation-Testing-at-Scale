package toy.bank;

import java.util.*;

public class Bank {
    private final Map<String, Account> accounts = new LinkedHashMap<>();
    private final List<Transaction> log = new ArrayList<>();

    public Account open(String id, long initial) {
        if (accounts.containsKey(id)) throw new IllegalArgumentException("exists");
        Account a = new Account(id, initial);
        accounts.put(id, a);
        return a;
    }

    public Account get(String id) {
        Account a = accounts.get(id);
        if (a == null) throw new NoSuchElementException(id);
        return a;
    }

    public void transfer(String from, String to, long amount) {
        if (from.equals(to)) throw new IllegalArgumentException("same");
        Account a = get(from);
        Account b = get(to);
        a.withdraw(amount);
        b.deposit(amount);
        log.add(new Transaction(from, to, amount));
    }

    public long totalAssets() {
        long sum = 0;
        for (Account a : accounts.values()) sum += a.getBalance();
        return sum;
    }

    public List<Account> richest(int n) {
        List<Account> list = new ArrayList<>(accounts.values());
        list.sort((x, y) -> Long.compare(y.getBalance(), x.getBalance()));
        return list.subList(0, Math.min(n, list.size()));
    }

    public int transactionCount() { return log.size(); }

    public long volume() {
        long v = 0;
        for (Transaction t : log) v += t.amount;
        return v;
    }
}
