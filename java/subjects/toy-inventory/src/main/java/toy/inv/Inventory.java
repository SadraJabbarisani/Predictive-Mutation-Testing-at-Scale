package toy.inv;

import java.util.HashMap;
import java.util.Map;

public class Inventory {
    private final Map<String, Integer> stock = new HashMap<>();
    private final Map<String, Long> price = new HashMap<>();
    private final int reorderLevel;

    public Inventory(int reorderLevel) { this.reorderLevel = reorderLevel; }

    public void addItem(String sku, long unitPrice, int qty) {
        if (qty < 0 || unitPrice < 0) throw new IllegalArgumentException();
        stock.merge(sku, qty, Integer::sum);
        price.put(sku, unitPrice);
    }
    public int quantity(String sku) { return stock.getOrDefault(sku, 0); }
    public long price(String sku) {
        Long p = price.get(sku);
        if (p == null) throw new IllegalArgumentException("unknown " + sku);
        return p;
    }
    public boolean reserve(String sku, int qty) {
        int have = quantity(sku);
        if (qty <= 0 || have < qty) return false;
        stock.put(sku, have - qty);
        return true;
    }
    public boolean needsReorder(String sku) { return quantity(sku) <= reorderLevel; }
    public long stockValue() {
        long v = 0;
        for (Map.Entry<String, Integer> e : stock.entrySet()) v += e.getValue() * price.get(e.getKey());
        return v;
    }
}
