package toy.text;

public class Strings {
    public static String reverse(String s) {
        if (s == null) return null;
        return new StringBuilder(s).reverse().toString();
    }

    public static boolean isPalindrome(String s) {
        String t = s.replaceAll("[^A-Za-z0-9]", "").toLowerCase();
        int i = 0, j = t.length() - 1;
        while (i < j) {
            if (t.charAt(i) != t.charAt(j)) return false;
            i++;
            j--;
        }
        return true;
    }

    public static int wordCount(String s) {
        if (s == null || s.isBlank()) return 0;
        return s.trim().split("\\s+").length;
    }

    public static String capitalize(String s) {
        if (s == null || s.isEmpty()) return s;
        StringBuilder sb = new StringBuilder();
        boolean up = true;
        for (char c : s.toCharArray()) {
            if (Character.isWhitespace(c)) { up = true; sb.append(c); }
            else if (up) { sb.append(Character.toUpperCase(c)); up = false; }
            else sb.append(Character.toLowerCase(c));
        }
        return sb.toString();
    }

    public static String caesar(String s, int shift) {
        StringBuilder sb = new StringBuilder();
        int k = ((shift % 26) + 26) % 26;
        for (char c : s.toCharArray()) {
            if (c >= 'a' && c <= 'z') sb.append((char) ('a' + (c - 'a' + k) % 26));
            else if (c >= 'A' && c <= 'Z') sb.append((char) ('A' + (c - 'A' + k) % 26));
            else sb.append(c);
        }
        return sb.toString();
    }

    public static String truncate(String s, int max) {
        if (max < 3) throw new IllegalArgumentException("max");
        if (s.length() <= max) return s;
        return s.substring(0, max - 3) + "...";
    }
}
