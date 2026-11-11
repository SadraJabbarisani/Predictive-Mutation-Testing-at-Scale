package toy.coll;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CollTest {
    @Test void stack() {
        IntStack s = new IntStack();
        for (int i = 0; i < 10; i++) s.push(i);
        assertEquals(9, s.pop());
        assertEquals(8, s.peek());
        assertEquals(9, s.size());
        assertEquals(8, s.max());
    }
    @Test void queue() {
        BoundedQueue<String> q = new BoundedQueue<>(2);
        assertTrue(q.offer("a"));
        assertTrue(q.offer("b"));
        assertFalse(q.offer("c"));
        assertEquals("a", q.poll());
    }
    @Test void heap() {
        MinHeap h = new MinHeap();
        h.add(5); h.add(1); h.add(3);
        assertEquals(1, h.poll());
    }
    @Test void sorted() {
        SortedList l = new SortedList();
        l.insert(3); l.insert(1); l.insert(2);
        assertEquals(1, l.get(0));
        assertTrue(l.contains(2));
    }
}
