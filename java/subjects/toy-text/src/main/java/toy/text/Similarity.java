package toy.text;

import java.util.HashSet;
import java.util.Set;

public class Similarity {
    public static int levenshtein(String a, String b) {
        int[][] d = new int[a.length() + 1][b.length() + 1];
        for (int i = 0; i <= a.length(); i++) d[i][0] = i;
        for (int j = 0; j <= b.length(); j++) d[0][j] = j;
        for (int i = 1; i <= a.length(); i++) {
            for (int j = 1; j <= b.length(); j++) {
                int cost = a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1;
                d[i][j] = Math.min(Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1), d[i - 1][j - 1] + cost);
            }
        }
        return d[a.length()][b.length()];
    }

    public static double jaccard(String a, String b) {
        Set<String> x = bigrams(a), y = bigrams(b);
        if (x.isEmpty() && y.isEmpty()) return 1.0;
        Set<String> inter = new HashSet<>(x);
        inter.retainAll(y);
        Set<String> uni = new HashSet<>(x);
        uni.addAll(y);
        return (double) inter.size() / uni.size();
    }

    static Set<String> bigrams(String s) {
        Set<String> r = new HashSet<>();
        for (int i = 0; i + 1 < s.length(); i++) r.add(s.substring(i, i + 2));
        return r;
    }

    public static int hamming(String a, String b) {
        if (a.length() != b.length()) throw new IllegalArgumentException("length");
        int d = 0;
        for (int i = 0; i < a.length(); i++) if (a.charAt(i) != b.charAt(i)) d++;
        return d;
    }
}
