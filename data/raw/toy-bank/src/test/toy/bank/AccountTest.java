package toy.bank;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class AccountTest {
    @Test void depositIncreasesBalance() {
        Account a = new Account("a", 100);
        a.deposit(50);
        assertEquals(150, a.getBalance());
    }
    @Test void withdrawDecreasesBalance() {
        Account a = new Account("a", 100);
        a.withdraw(30);
        assertEquals(70, a.getBalance());
        assertEquals(1, a.getWithdrawalsToday());
    }
    @Test void cannotOverdraw() {
        Account a = new Account("a", 10);
        assertThrows(IllegalStateException.class, () -> a.withdraw(11));
    }
    @Test void frozenRejectsDeposit() {
        Account a = new Account("a", 10);
        a.freeze();
        assertThrows(IllegalStateException.class, () -> a.deposit(1));
    }
    @Test void dailyLimit() {
        Account a = new Account("a", 100);
        a.withdraw(1); a.withdraw(1); a.withdraw(1);
        assertThrows(IllegalStateException.class, () -> a.withdraw(1));
        a.resetDay();
        a.withdraw(1);
    }
    @Test void badId() {
        assertThrows(IllegalArgumentException.class, () -> new Account("", 1));
    }
}
