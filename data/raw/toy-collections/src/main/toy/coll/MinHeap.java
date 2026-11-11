package toy.coll;

import java.util.ArrayList;
import java.util.List;

public class MinHeap {
    private final List<Integer> h = new ArrayList<>();

    public void add(int v) {
        h.add(v);
        int i = h.size() - 1;
        while (i > 0) {
            int p = (i - 1) / 2;
            if (h.get(p) <= h.get(i)) break;
            swap(i, p);
            i = p;
        }
    }
    public int poll() {
        int top = h.get(0);
        int last = h.remove(h.size() - 1);
        if (!h.isEmpty()) {
            h.set(0, last);
            int i = 0;
            while (true) {
                int l = 2 * i + 1, r = l + 1, m = i;
                if (l < h.size() && h.get(l) < h.get(m)) m = l;
                if (r < h.size() && h.get(r) < h.get(m)) m = r;
                if (m == i) break;
                swap(i, m);
                i = m;
            }
        }
        return top;
    }
    public int size() { return h.size(); }
    private void swap(int a, int b) { int t = h.get(a); h.set(a, h.get(b)); h.set(b, t); }
}
