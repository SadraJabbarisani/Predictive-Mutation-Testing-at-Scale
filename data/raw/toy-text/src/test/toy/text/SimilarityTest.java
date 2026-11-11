package toy.text;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SimilarityTest {
    @Test void lev() { assertEquals(3, Similarity.levenshtein("kitten", "sitting")); }
    @Test void jaccardSame() { assertEquals(1.0, Similarity.jaccard("abc", "abc"), 1e-9); }
}
