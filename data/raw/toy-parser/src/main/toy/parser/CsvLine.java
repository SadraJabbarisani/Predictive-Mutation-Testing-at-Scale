package toy.parser;

import java.util.ArrayList;
import java.util.List;

public class CsvLine {
    public static List<String> parse(String line, char sep) {
        List<String> out = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (quoted) {
                if (c == '"') {
                    if (i + 1 < line.length() && line.charAt(i + 1) == '"') { cur.append('"'); i++; }
                    else quoted = false;
                } else cur.append(c);
            } else if (c == '"') quoted = true;
            else if (c == sep) { out.add(cur.toString()); cur.setLength(0); }
            else cur.append(c);
        }
        if (quoted) throw new IllegalArgumentException("unterminated quote");
        out.add(cur.toString());
        return out;
    }
}
