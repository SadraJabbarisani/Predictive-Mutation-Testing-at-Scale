package toy.coll;

import java.util.Arrays;
import java.util.NoSuchElementException;

public class IntStack {
    private int[] data = new int[4];
    private int size;

    public void push(int v) {
        if (size == data.length) data = Arrays.copyOf(data, data.length * 2);
        data[size++] = v;
    }
    public int pop() {
        if (size == 0) throw new NoSuchElementException();
        return data[--size];
    }
    public int peek() {
        if (size == 0) throw new NoSuchElementException();
        return data[size - 1];
    }
    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
    public int max() {
        if (size == 0) throw new NoSuchElementException();
        int m = data[0];
        for (int i = 1; i < size; i++) if (data[i] > m) m = data[i];
        return m;
    }
}
