package toy.graph;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class GraphTest {
    @Test void dijkstra() {
        Graph g = new Graph(4, true);
        g.edge(0, 1, 5); g.edge(0, 2, 1); g.edge(2, 1, 1); g.edge(1, 3, 2);
        long[] d = g.dijkstra(0);
        assertEquals(2, d[1]);
        assertEquals(4, d[3]);
    }
    @Test void topo() {
        Graph g = new Graph(3, true);
        g.edge(0, 1, 1); g.edge(1, 2, 1);
        assertEquals(List.of(0, 1, 2), g.topoSort());
    }
    @Test void bfsRuns() {
        Graph g = new Graph(3, false);
        g.edge(0, 1, 1);
        assertEquals(2, g.bfs(0).size());
        assertEquals(2, g.components());
    }
}
