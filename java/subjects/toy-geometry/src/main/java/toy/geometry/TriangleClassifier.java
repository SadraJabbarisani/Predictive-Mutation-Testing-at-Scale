package toy.geometry;

public class TriangleClassifier {
    public enum Kind { INVALID, EQUILATERAL, ISOSCELES, SCALENE }

    public static Kind classify(int a, int b, int c) {
        if (a <= 0 || b <= 0 || c <= 0) return Kind.INVALID;
        if (a + b <= c || a + c <= b || b + c <= a) return Kind.INVALID;
        if (a == b && b == c) return Kind.EQUILATERAL;
        if (a == b || b == c || a == c) return Kind.ISOSCELES;
        return Kind.SCALENE;
    }

    public static boolean isRight(int a, int b, int c) {
        int[] s = {a, b, c};
        java.util.Arrays.sort(s);
        return s[0] * s[0] + s[1] * s[1] == s[2] * s[2];
    }

    public static double area(int a, int b, int c) {
        if (classify(a, b, c) == Kind.INVALID) return 0;
        double s = (a + b + c) / 2.0;
        return Math.sqrt(s * (s - a) * (s - b) * (s - c));
    }
}
