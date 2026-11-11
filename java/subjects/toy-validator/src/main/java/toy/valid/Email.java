package toy.valid;

public class Email {
    public static boolean isValid(String e) {
        int at = e.indexOf('@');
        if (at <= 0 || at != e.lastIndexOf('@')) return false;
        String local = e.substring(0, at), domain = e.substring(at + 1);
        if (local.length() > 64 || domain.length() < 3) return false;
        if (local.startsWith(".") || local.endsWith(".")) return false;
        int dot = domain.lastIndexOf('.');
        if (dot <= 0 || dot >= domain.length() - 2) return false;
        for (char c : domain.toCharArray()) {
            if (!(Character.isLetterOrDigit(c) || c == '.' || c == '-')) return false;
        }
        return true;
    }
}
