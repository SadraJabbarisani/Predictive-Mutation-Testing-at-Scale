package toy.parser;

public class Roman {
    private static final int[] V = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
    private static final String[] S = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};

    public static String toRoman(int n) {
        if (n <= 0 || n >= 4000) throw new IllegalArgumentException();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < V.length; i++) {
            while (n >= V[i]) { sb.append(S[i]); n -= V[i]; }
        }
        return sb.toString();
    }
    public static int fromRoman(String r) {
        int total = 0, prev = 0;
        for (int i = r.length() - 1; i >= 0; i--) {
            int v = value(r.charAt(i));
            if (v < prev) total -= v; else { total += v; prev = v; }
        }
        return total;
    }
    static int value(char c) {
        switch (c) {
            case 'I': return 1;
            case 'V': return 5;
            case 'X': return 10;
            case 'L': return 50;
            case 'C': return 100;
            case 'D': return 500;
            case 'M': return 1000;
            default: throw new IllegalArgumentException("" + c);
        }
    }
}
