package toy.valid;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ValidTest {
    @Test void luhn() { assertTrue(Luhn.isValid("79927398713")); assertFalse(Luhn.isValid("79927398710")); }
    @Test void isbn10() { assertTrue(Isbn.isValid10("0-306-40615-2")); }
    @Test void isbn13() { assertTrue(Isbn.isValid13("978-0-306-40615-7")); assertFalse(Isbn.isValid13("978-0-306-40615-8")); }
    @Test void email() { assertTrue(Email.isValid("a.b@example.com")); assertFalse(Email.isValid("a@b")); }
    @Test void password() { assertTrue(new PasswordPolicy(8, true).violations("Abcdef1!").isEmpty()); }
}
