package toy.geometry;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static toy.geometry.TriangleClassifier.Kind.*;

class TriangleClassifierTest {
    @Test void equilateral() { assertEquals(EQUILATERAL, TriangleClassifier.classify(3, 3, 3)); }
    @Test void isosceles() { assertEquals(ISOSCELES, TriangleClassifier.classify(3, 3, 5)); }
    @Test void scalene() { assertEquals(SCALENE, TriangleClassifier.classify(3, 4, 5)); }
    @Test void invalidZero() { assertEquals(INVALID, TriangleClassifier.classify(0, 4, 5)); }
    @Test void invalidInequality() { assertEquals(INVALID, TriangleClassifier.classify(1, 2, 3)); }
    @Test void rightTriangle() { assertTrue(TriangleClassifier.isRight(5, 3, 4)); assertFalse(TriangleClassifier.isRight(2, 3, 4)); }
    @Test void area() { assertEquals(6.0, TriangleClassifier.area(3, 4, 5), 1e-9); }
}
