package toy.math;

import java.util.Arrays;

public class Stats {
    public static double mean(double[] x) {
        if (x.length == 0) throw new IllegalArgumentException();
        double s = 0;
        for (double v : x) s += v;
        return s / x.length;
    }
    public static double variance(double[] x) {
        double m = mean(x), s = 0;
        for (double v : x) s += (v - m) * (v - m);
        return x.length > 1 ? s / (x.length - 1) : 0;
    }
    public static double median(double[] x) {
        double[] c = x.clone();
        Arrays.sort(c);
        int n = c.length;
        return n % 2 == 1 ? c[n / 2] : (c[n / 2 - 1] + c[n / 2]) / 2;
    }
    public static double pearson(double[] a, double[] b) {
        if (a.length != b.length) throw new IllegalArgumentException();
        double ma = mean(a), mb = mean(b), num = 0, da = 0, db = 0;
        for (int i = 0; i < a.length; i++) {
            num += (a[i] - ma) * (b[i] - mb);
            da += (a[i] - ma) * (a[i] - ma);
            db += (b[i] - mb) * (b[i] - mb);
        }
        if (da == 0 || db == 0) return 0;
        return num / Math.sqrt(da * db);
    }
    public static double clamp(double v, double lo, double hi) {
        if (v < lo) return lo;
        if (v > hi) return hi;
        return v;
    }
}
