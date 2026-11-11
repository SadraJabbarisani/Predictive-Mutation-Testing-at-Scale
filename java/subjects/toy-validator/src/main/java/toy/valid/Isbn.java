package toy.valid;

public class Isbn {
    public static boolean isValid10(String s) {
        s = s.replace("-", "");
        if (s.length() != 10) return false;
        int sum = 0;
        for (int i = 0; i < 10; i++) {
            char c = s.charAt(i);
            int v;
            if (i == 9 && (c == 'X' || c == 'x')) v = 10;
            else if (Character.isDigit(c)) v = c - '0';
            else return false;
            sum += v * (10 - i);
        }
        return sum % 11 == 0;
    }
    public static boolean isValid13(String s) {
        s = s.replace("-", "");
        if (s.length() != 13) return false;
        int sum = 0;
        for (int i = 0; i < 13; i++) {
            char c = s.charAt(i);
            if (!Character.isDigit(c)) return false;
            sum += (c - '0') * (i % 2 == 0 ? 1 : 3);
        }
        return sum % 10 == 0;
    }
}
