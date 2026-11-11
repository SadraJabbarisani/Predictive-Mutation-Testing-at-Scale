package toy.bank;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class BankTest {
    @Test void transferMovesMoney() {
        Bank b = new Bank();
        b.open("x", 100);
        b.open("y", 0);
        b.transfer("x", "y", 40);
        assertEquals(60, b.get("x").getBalance());
        assertEquals(40, b.get("y").getBalance());
        assertEquals(1, b.transactionCount());
    }
    @Test void totalAssets() {
        Bank b = new Bank();
        b.open("x", 100);
        b.open("y", 5);
        assertTrue(b.totalAssets() > 0);
    }
    @Test void richestRuns() {
        Bank b = new Bank();
        b.open("x", 1);
        b.open("y", 9);
        assertEquals("y", b.richest(1).get(0).getId());
    }
}
