package toy.geometry;

import java.util.ArrayList;
import java.util.List;

public class Polygon {
    private final List<Point> pts = new ArrayList<>();
    public Polygon add(Point p) { pts.add(p); return this; }
    public int size() { return pts.size(); }

    public double perimeter() {
        double s = 0;
        for (int i = 0; i < pts.size(); i++) {
            s += pts.get(i).distance(pts.get((i + 1) % pts.size()));
        }
        return s;
    }

    /** Shoelace formula. */
    public double area() {
        if (pts.size() < 3) return 0;
        double s = 0;
        for (int i = 0; i < pts.size(); i++) {
            Point a = pts.get(i), b = pts.get((i + 1) % pts.size());
            s += a.x * b.y - b.x * a.y;
        }
        return Math.abs(s) / 2;
    }

    public boolean isConvex() {
        int n = pts.size();
        if (n < 4) return n == 3;
        boolean pos = false, neg = false;
        for (int i = 0; i < n; i++) {
            Point a = pts.get(i), b = pts.get((i + 1) % n), c = pts.get((i + 2) % n);
            double cross = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x);
            if (cross > 0) pos = true;
            if (cross < 0) neg = true;
            if (pos && neg) return false;
        }
        return true;
    }

    public Point centroid() {
        double sx = 0, sy = 0;
        for (Point p : pts) { sx += p.x; sy += p.y; }
        return new Point(sx / pts.size(), sy / pts.size());
    }
}
