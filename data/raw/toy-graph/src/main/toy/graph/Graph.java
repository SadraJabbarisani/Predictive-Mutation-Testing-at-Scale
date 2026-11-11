package toy.graph;

import java.util.*;

public class Graph {
    private final int n;
    private final List<List<int[]>> adj = new ArrayList<>();
    private final boolean directed;

    public Graph(int n, boolean directed) {
        this.n = n;
        this.directed = directed;
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
    }
    public void edge(int u, int v, int w) {
        if (u < 0 || v < 0 || u >= n || v >= n) throw new IndexOutOfBoundsException();
        if (w < 0) throw new IllegalArgumentException("negative weight");
        adj.get(u).add(new int[]{v, w});
        if (!directed) adj.get(v).add(new int[]{u, w});
    }
    public int edgeCount() {
        int c = 0;
        for (List<int[]> l : adj) c += l.size();
        return directed ? c : c / 2;
    }
    public List<Integer> bfs(int s) {
        boolean[] seen = new boolean[n];
        List<Integer> order = new ArrayList<>();
        Deque<Integer> q = new ArrayDeque<>();
        q.add(s);
        seen[s] = true;
        while (!q.isEmpty()) {
            int u = q.poll();
            order.add(u);
            for (int[] e : adj.get(u)) if (!seen[e[0]]) { seen[e[0]] = true; q.add(e[0]); }
        }
        return order;
    }
    public long[] dijkstra(int s) {
        long[] d = new long[n];
        Arrays.fill(d, Long.MAX_VALUE);
        d[s] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(a -> a[1]));
        pq.add(new long[]{s, 0});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            int u = (int) cur[0];
            if (cur[1] > d[u]) continue;
            for (int[] e : adj.get(u)) {
                long nd = d[u] + e[1];
                if (nd < d[e[0]]) { d[e[0]] = nd; pq.add(new long[]{e[0], nd}); }
            }
        }
        return d;
    }
    public List<Integer> topoSort() {
        if (!directed) throw new IllegalStateException("undirected");
        int[] indeg = new int[n];
        for (List<int[]> l : adj) for (int[] e : l) indeg[e[0]]++;
        Deque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
        List<Integer> out = new ArrayList<>();
        while (!q.isEmpty()) {
            int u = q.poll();
            out.add(u);
            for (int[] e : adj.get(u)) if (--indeg[e[0]] == 0) q.add(e[0]);
        }
        if (out.size() != n) throw new IllegalStateException("cycle");
        return out;
    }
    public int components() {
        UnionFind uf = new UnionFind(n);
        for (int u = 0; u < n; u++) for (int[] e : adj.get(u)) uf.union(u, e[0]);
        return uf.count();
    }
}
