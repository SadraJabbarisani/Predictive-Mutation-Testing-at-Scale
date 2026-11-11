package toy.coll;

import java.util.ArrayList;
import java.util.List;

public class SortedList {
    private final List<Integer> xs = new ArrayList<>();

    public void insert(int v) {
        int lo = 0, hi = xs.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (xs.get(mid) < v) lo = mid + 1; else hi = mid;
        }
        xs.add(lo, v);
    }
    public boolean contains(int v) {
        int lo = 0, hi = xs.size() - 1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            int x = xs.get(mid);
            if (x == v) return true;
            if (x < v) lo = mid + 1; else hi = mid - 1;
        }
        return false;
    }
    public int get(int i) { return xs.get(i); }
    public int size() { return xs.size(); }
    public double median() {
        int n = xs.size();
        if (n == 0) throw new IllegalStateException();
        if (n % 2 == 1) return xs.get(n / 2);
        return (xs.get(n / 2 - 1) + xs.get(n / 2)) / 2.0;
    }
}
