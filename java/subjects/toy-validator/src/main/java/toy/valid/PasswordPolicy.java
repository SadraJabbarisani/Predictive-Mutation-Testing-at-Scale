package toy.valid;

import java.util.ArrayList;
import java.util.List;

public class PasswordPolicy {
    private final int minLength;
    private final boolean requireSymbol;

    public PasswordPolicy(int minLength, boolean requireSymbol) {
        this.minLength = minLength;
        this.requireSymbol = requireSymbol;
    }
    public List<String> violations(String p) {
        List<String> v = new ArrayList<>();
        if (p.length() < minLength) v.add("too short");
        boolean up = false, low = false, dig = false, sym = false;
        for (char c : p.toCharArray()) {
            if (Character.isUpperCase(c)) up = true;
            else if (Character.isLowerCase(c)) low = true;
            else if (Character.isDigit(c)) dig = true;
            else sym = true;
        }
        if (!up) v.add("no uppercase");
        if (!low) v.add("no lowercase");
        if (!dig) v.add("no digit");
        if (requireSymbol && !sym) v.add("no symbol");
        return v;
    }
    public int strength(String p) {
        int s = Math.min(p.length(), 20);
        s += (4 - violations(p).size()) * 5;
        return Math.max(0, s);
    }
}
