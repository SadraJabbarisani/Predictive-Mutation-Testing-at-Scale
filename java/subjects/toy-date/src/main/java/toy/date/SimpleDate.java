package toy.date;

public final class SimpleDate {
    public final int year, month, day;
    private static final int[] DAYS = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

    public SimpleDate(int y, int m, int d) {
        if (m < 1 || m > 12) throw new IllegalArgumentException("month");
        if (d < 1 || d > daysInMonth(y, m)) throw new IllegalArgumentException("day");
        year = y; month = m; day = d;
    }
    public static boolean isLeap(int y) { return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0; }
    public static int daysInMonth(int y, int m) { return m == 2 && isLeap(y) ? 29 : DAYS[m - 1]; }

    public int dayOfYear() {
        int n = day;
        for (int m = 1; m < month; m++) n += daysInMonth(year, m);
        return n;
    }
    /** 0 = Monday ... 6 = Sunday (Zeller-like). */
    public int dayOfWeek() {
        int y = year, m = month;
        if (m < 3) { m += 12; y--; }
        int k = y % 100, j = y / 100;
        int h = (day + 13 * (m + 1) / 5 + k + k / 4 + j / 4 + 5 * j) % 7;
        return (h + 5) % 7;
    }
    public SimpleDate plusDays(int n) {
        int y = year, m = month, d = day;
        while (n > 0) {
            int left = daysInMonth(y, m) - d;
            if (n <= left) { d += n; n = 0; }
            else {
                n -= left + 1;
                d = 1;
                m++;
                if (m > 12) { m = 1; y++; }
            }
        }
        return new SimpleDate(y, m, d);
    }
    public boolean isBefore(SimpleDate o) {
        if (year != o.year) return year < o.year;
        if (month != o.month) return month < o.month;
        return day < o.day;
    }
    public boolean isWeekend() { return dayOfWeek() >= 5; }
}
