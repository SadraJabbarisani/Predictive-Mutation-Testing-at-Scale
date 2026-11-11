package toy.coll;

public class BoundedQueue<T> {
    private final Object[] buf;
    private int head, tail, count;

    public BoundedQueue(int capacity) {
        if (capacity < 1) throw new IllegalArgumentException();
        buf = new Object[capacity];
    }
    public boolean offer(T x) {
        if (count == buf.length) return false;
        buf[tail] = x;
        tail = (tail + 1) % buf.length;
        count++;
        return true;
    }
    @SuppressWarnings("unchecked")
    public T poll() {
        if (count == 0) return null;
        T x = (T) buf[head];
        buf[head] = null;
        head = (head + 1) % buf.length;
        count--;
        return x;
    }
    public int size() { return count; }
    public boolean isFull() { return count == buf.length; }
    public int remaining() { return buf.length - count; }
}
