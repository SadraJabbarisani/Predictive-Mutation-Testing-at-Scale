package toy.parser;

/** Recursive-descent evaluator for + - * / ( ) and integers. */
public class Calculator {
    private String s;
    private int pos;

    public long eval(String expr) {
        s = expr.replace(" ", "");
        pos = 0;
        long v = expr();
        if (pos != s.length()) throw new IllegalArgumentException("trailing at " + pos);
        return v;
    }
    private long expr() {
        long v = term();
        while (pos < s.length()) {
            char c = s.charAt(pos);
            if (c == '+') { pos++; v += term(); }
            else if (c == '-') { pos++; v -= term(); }
            else break;
        }
        return v;
    }
    private long term() {
        long v = factor();
        while (pos < s.length()) {
            char c = s.charAt(pos);
            if (c == '*') { pos++; v *= factor(); }
            else if (c == '/') {
                pos++;
                long d = factor();
                if (d == 0) throw new ArithmeticException("div by zero");
                v /= d;
            } else break;
        }
        return v;
    }
    private long factor() {
        if (pos >= s.length()) throw new IllegalArgumentException("eof");
        char c = s.charAt(pos);
        if (c == '-') { pos++; return -factor(); }
        if (c == '(') {
            pos++;
            long v = expr();
            if (pos >= s.length() || s.charAt(pos) != ')') throw new IllegalArgumentException("missing )");
            pos++;
            return v;
        }
        int start = pos;
        while (pos < s.length() && Character.isDigit(s.charAt(pos))) pos++;
        if (start == pos) throw new IllegalArgumentException("number expected at " + pos);
        return Long.parseLong(s.substring(start, pos));
    }
}
