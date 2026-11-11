package toy.geometry;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class PolygonTest {
    private Polygon square() {
        return new Polygon().add(new Point(0, 0)).add(new Point(2, 0)).add(new Point(2, 2)).add(new Point(0, 2));
    }
    @Test void squareArea() { assertEquals(4.0, square().area(), 1e-9); }
    @Test void squarePerimeter() { assertTrue(square().perimeter() > 0); }
    @Test void convex() { assertTrue(square().isConvex()); }
    @Test void quadrant() { assertEquals(1, new Point(1, 1).quadrant()); }
}
