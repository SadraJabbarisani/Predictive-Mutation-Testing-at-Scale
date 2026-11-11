package toy.valid;

public class Luhn {
    public static boolean isValid(String digits) {
        if (digits == null || digits.length() < 2) return false;
        int sum = 0;
        boolean dbl = false;
        for (int i = digits.length() - 1; i >= 0; i--) {
            char c = digits.charAt(i);
            if (c < '0' || c > '9') return false;
            int d = c - '0';
            if (dbl) { d *= 2; if (d > 9) d -= 9; }
            sum += d;
            dbl = !dbl;
        }
        return sum % 10 == 0;
    }
    public static int checkDigit(String payload) {
        for (int d = 0; d <= 9; d++) if (isValid(payload + d)) return d;
        throw new IllegalStateException();
    }
}
