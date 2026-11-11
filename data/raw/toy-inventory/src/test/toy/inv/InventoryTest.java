package toy.inv;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class InventoryTest {
    @Test void reserve() {
        Inventory inv = new Inventory(2);
        inv.addItem("a", 100, 5);
        assertTrue(inv.reserve("a", 3));
        assertEquals(2, inv.quantity("a"));
        assertTrue(inv.needsReorder("a"));
        assertFalse(inv.reserve("a", 3));
    }
    @Test void orderTotal() {
        Inventory inv = new Inventory(0);
        inv.addItem("a", 1000, 10);
        Order o = new Order(inv).add("a", 2);
        assertEquals(2000, o.subtotal());
        assertTrue(o.total(DiscountPolicy.none()) > 2000);
        assertTrue(o.place());
    }
}
