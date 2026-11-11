package toy.inv;

import java.util.LinkedHashMap;
import java.util.Map;

public class Order {
    private final Map<String, Integer> lines = new LinkedHashMap<>();
    private final Inventory inv;
    private boolean placed;

    public Order(Inventory inv) { this.inv = inv; }

    public Order add(String sku, int qty) {
        if (placed) throw new IllegalStateException("placed");
        lines.merge(sku, qty, Integer::sum);
        return this;
    }
    public long subtotal() {
        long s = 0;
        for (Map.Entry<String, Integer> e : lines.entrySet()) s += inv.price(e.getKey()) * e.getValue();
        return s;
    }
    public int itemCount() {
        int n = 0;
        for (int q : lines.values()) n += q;
        return n;
    }
    public long total(DiscountPolicy policy) {
        long sub = subtotal();
        long disc = policy.discount(sub, itemCount());
        long ship = Shipping.cost(sub - disc, itemCount());
        return sub - disc + ship;
    }
    public boolean place() {
        for (Map.Entry<String, Integer> e : lines.entrySet()) {
            if (inv.quantity(e.getKey()) < e.getValue()) return false;
        }
        for (Map.Entry<String, Integer> e : lines.entrySet()) inv.reserve(e.getKey(), e.getValue());
        placed = true;
        return true;
    }
}
