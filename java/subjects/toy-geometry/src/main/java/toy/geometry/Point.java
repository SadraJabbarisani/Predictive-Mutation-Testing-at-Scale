package toy.geometry;

public final class Point {
    public final double x, y;
    public Point(double x, double y) { this.x = x; this.y = y; }
    public double distance(Point o) {
        double dx = x - o.x, dy = y - o.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    public Point translate(double dx, double dy) { return new Point(x + dx, y + dy); }
    public int quadrant() {
        if (x == 0 || y == 0) return 0;
        if (x > 0) return y > 0 ? 1 : 4;
        return y > 0 ? 2 : 3;
    }
}
