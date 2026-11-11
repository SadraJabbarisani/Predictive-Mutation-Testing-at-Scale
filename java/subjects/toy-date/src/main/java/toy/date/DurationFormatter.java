package toy.date;

public class DurationFormatter {
    public static String format(long seconds) {
        if (seconds < 0) throw new IllegalArgumentException();
        if (seconds == 0) return "now";
        long d = seconds / 86400, h = seconds % 86400 / 3600, m = seconds % 3600 / 60, s = seconds % 60;
        StringBuilder sb = new StringBuilder();
        append(sb, d, "day");
        append(sb, h, "hour");
        append(sb, m, "minute");
        append(sb, s, "second");
        return sb.toString().trim();
    }
    private static void append(StringBuilder sb, long v, String unit) {
        if (v == 0) return;
        if (sb.length() > 0) sb.append(", ");
        sb.append(v).append(' ').append(unit);
        if (v > 1) sb.append('s');
    }
    public static long parseHms(String hms) {
        String[] p = hms.split(":");
        if (p.length != 3) throw new IllegalArgumentException(hms);
        long h = Long.parseLong(p[0]), m = Long.parseLong(p[1]), s = Long.parseLong(p[2]);
        if (m >= 60 || s >= 60 || h < 0 || m < 0 || s < 0) throw new IllegalArgumentException(hms);
        return h * 3600 + m * 60 + s;
    }
}
