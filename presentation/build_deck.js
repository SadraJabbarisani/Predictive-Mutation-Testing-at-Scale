// فارسی: ساخت فایل ارائه از results/summary.json؛ متن‌ها را در همین فایل ویرایش کنید، نه اعداد را.
// Builds presentation/team8_pmt_presentation.pptx from results/summary.json.
// Usage (from repo root):  node presentation/build_deck.js
// All slide text is Persian (RTL). Every number comes from results/summary.json or
// data/processed/projects_meta.json — edit the TEXT constants below, never the numbers.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "results/summary.json"), "utf8"));
const META = JSON.parse(fs.readFileSync(path.join(ROOT, "data/processed/projects_meta.json"), "utf8"));
const OUT = path.join(__dirname, "team8_pmt_presentation.pptx");

// ---------------------------------------------------------------- theme
const THEME = {
  name: "Team8 Mutation",
  headFontFace: "Vazirmatn",
  bodyFontFace: "Vazirmatn",
  colors: {
    dk1: "14232E", lt1: "FFFFFF", dk2: "1F3A4D", lt2: "EEF2F4",
    accent1: "EB6834", accent2: "2A78D6", accent3: "1BAF7A", accent4: "EDA100",
    accent5: "6250D6", accent6: "52514E", hlink: "2A78D6", folHlink: "6250D6",
  },
};
const HEX = THEME.colors;
const INK = HEX.dk1, MUTED = "52606B", CARD = "F3F6F8", ORANGE = HEX.accent1, NAVY = HEX.dk2;
const METHOD_COLOR = { ace: ORANGE, random: "2A78D6", stratified: "1BAF7A", selective: "EDA100",
  pmt: "6250D6", model_only: "008300", active_topk: "52514E", seshat_lite: "E87BA4" };
const METHOD_FA = { ace: "ACE-MT", random: "نمونه‌گیری تصادفی", stratified: "نمونه‌گیری طبقه‌ای",
  selective: "جهش انتخابی", pmt: "PMT", model_only: "فقط مدل", active_topk: "Active top-k", seshat_lite: "Seshat-lite" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.rtlMode = true;
pres.title = "Predictive Mutation Testing at Scale — Team 8";
pres.author = "Team 8";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333, H = 7.5, M = 0.6;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "DARK",
  background: { color: INK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.2, w: W - 2 * M, h: 1.5, align: "right",
      fontSize: 40, bold: true, color: "FFFFFF", rtlMode: true, valign: "bottom" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: "FFFFFF" },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.9, align: "right",
      fontSize: 30, bold: true, color: INK, rtlMode: true, valign: "middle" }, text: "" } },
  ],
  slideNumber: { x: 0.35, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: MUTED, fontFace: "Vazirmatn" },
});

// ---------------------------------------------------------------- helpers
const fa = (t, o = {}) => ({ text: t, options: { rtlMode: true, align: "right", lang: "fa-IR", ...o } });
function title(slide, t) { slide.addText(t, { placeholder: "title", rtlMode: true, lang: "fa-IR" }); }
function para(slide, items, x, y, w, h, o = {}) {
  // items: array of strings (bulleted) or {t, b} objects
  const runs = items.map((it, i) => {
    const t = typeof it === "string" ? it : it.t;
    return { text: t, options: { bullet: o.bullet === false ? false : { indent: 18 }, rtlMode: true, align: "right",
      lang: "fa-IR", bold: !!it.b, color: it.c || INK, breakLine: i < items.length - 1, paraSpaceAfter: 8 } };
  });
  slide.addText(runs, { x, y, w, h, fontSize: o.size || 16, valign: "top", isTextBox: true, margin: 4, ...o.box });
}
function card(slide, x, y, w, h, fill = CARD) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill },
    rectRadius: 0.12, objectName: "card" });
}
function badge(slide, x, y, label, fill = ORANGE, size = 0.55) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: size, h: size, fill: { color: fill }, line: { color: fill } });
  slide.addText(label, { x, y, w: size, h: size, align: "center", valign: "middle", fontSize: 16, bold: true,
    color: "FFFFFF", isTextBox: true, margin: 0 });
}
function stat(slide, x, y, w, value, label, color = ORANGE) {
  slide.addText(value, { x, y, w, h: 0.9, fontSize: 40, bold: true, color, align: "center", isTextBox: true,
    margin: 0, fontFace: "Vazirmatn" });
  slide.addText([fa(label, { align: "center" })], { x, y: y + 0.9, w, h: 0.6, fontSize: 13, color: MUTED,
    isTextBox: true, margin: 0, align: "center", valign: "top" });
}
const pct = (v, d = 0) => `${(100 * v).toFixed(d)}%`;
const f3 = (v) => Number(v).toFixed(3);

// ---------------------------------------------------------------- numbers
const ds = S.dataset;
const pitSeconds = Object.values(META).reduce((a, m) => a + (m.pit_seconds || 0), 0);
const overall = S.rq2_overall;
const get = (b, m, k = "mae") => (overall.find((r) => r.budget === b && r.method === m) || {})[k];
const budgets = [...new Set(overall.map((r) => r.budget))].sort((a, b) => a - b);
const redu = budgets.map((b) => 1 - get(b, "ace") / get(b, "random"));
const stats = S.rq2_stats || [];
const statFor = (b, base) => stats.filter((r) => r.budget === b && r.baseline === base);
const rq1 = S.rq1 || [];
const auc = (setting, model) => (rq1.find((r) => r.setting === setting && r.model === model) || {}).auc;
const rq4 = S.rq4 || [];
const tau = (m) => (rq4.find((r) => r.method === m) || {}).kendall_tau;
const rq3 = S.rq3 || [];
const cost = (m, b) => rq3.find((r) => r.method === m && r.budget === b) || {};

// ================================================================ slides
// 1. title
{
  const s = pres.addSlide({ masterName: "DARK" });
  title(s, "آزمون جهش کم‌هزینه با پیش‌بینی یادگرفته‌شده");
  s.addText("Predictive Mutation Testing at Scale", { x: M, y: 3.8, w: W - 2 * M, h: 0.6, fontSize: 22,
    color: "CADCFC", align: "right", isTextBox: true, margin: 0 });
  s.addText([fa("تیم ۸ · ارائه‌ی روش، baselineها و نتایج pilot")], { x: M, y: 4.6, w: W - 2 * M, h: 0.5,
    fontSize: 16, color: "AFC3CF", isTextBox: true, margin: 0 });
  badge(s, M, 6.3, "8", ORANGE, 0.7);
  s.addNotes("سلام. موضوع ما آزمون جهش کم‌هزینه است: چطور نمره‌ی جهش را بدون اجرای همه‌ی mutantها، با دقت و بازه‌ی اطمینان تخمین بزنیم.");
}

// 2. problem
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "مسئله: آزمون جهش معیار خوبی است ولی گران");
  para(s, [
    "آزمون جهش (mutation testing) خطاهای کوچک عمدی (mutant) در کد می‌کارد و می‌سنجد تست‌ها چندتا را «می‌کشند».",
    "نمره‌ی جهش = تعداد mutantهای کشته‌شده ÷ تعداد کل mutantها؛ معیاری قوی‌تر از پوشش کد.",
    "هزینه: هر mutant باید با همه‌ی تست‌های پوشش‌دهنده اجرا شود؛ در پروژه‌های واقعی هزاران mutant داریم.",
    { t: "سؤال: آیا می‌توان بیشتر نتیجه‌ها را پیش‌بینی کرد و فقط درصد کمی را واقعاً اجرا کرد، بی‌آن‌که دقت زیاد کم شود؟", b: true },
  ], 4.9, 1.5, 7.8, 4.6);
  card(s, M, 1.55, 3.9, 5.1);
  stat(s, M, 1.8, 3.9, ds.mutants.toLocaleString("en-US"), `mutant در ${ds.projects} پروژه‌ی Java`);
  stat(s, M, 3.4, 3.9, `${Math.round(pitSeconds / 60)} min`, "زمان PIT با ماتریس کامل (۴ هسته)", NAVY);
  stat(s, M, 5.0, 3.9, "5–20%", "بودجه‌ی اجرای مجاز در روش ما", "1BAF7A");
  s.addNotes("در دیتاست خودمان PIT با ماتریس کامل برای همین پروژه‌های کوچک هم چند دقیقه طول کشید؛ در پروژه‌های واقعی ساعت‌ها.");
}

// 3. idea + RQs
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "ایده و سؤال‌های پژوهشی");
  card(s, M, 1.45, W - 2 * M, 1.05, "FDEEE7");
  s.addText([fa("ایده: مدل یادگیری ماشین کالیبره‌شده احتمال کشته‌شدن هر mutant را پیش‌بینی می‌کند؛ یک سیاست فعال، آموزنده‌ترین mutantها را برای اجرای واقعی انتخاب می‌کند؛ و یک تخمین‌گر نااریب، نمره‌ی جهش را با بازه‌ی اطمینان ۹۵٪ می‌دهد.")],
    { x: M + 0.2, y: 1.5, w: W - 2 * M - 0.4, h: 0.95, fontSize: 15, color: INK, valign: "middle", isTextBox: true });
  const rqs = [
    ["RQ1", "دقت پیش‌بینی", "Precision، Recall، MCC و AUC؛ درون‌پروژه‌ای و بین‌پروژه‌ای"],
    ["RQ2", "دقت تخمین نمره", "MAE در بودجه‌های ۵، ۱۰ و ۲۰٪ و پوشش بازه‌ی اطمینان"],
    ["RQ3", "صرفه‌جویی", "درصد mutant و اجرای تست، و زمان صرفه‌جویی‌شده"],
    ["RQ4", "کاربرد", "رتبه‌بندی مجموعه‌تست‌ها (Kendall τ)"],
    ["RQ5", "Ablation", "حذف گروه‌های ویژگی و اجزای روش"],
  ];
  const cw = (W - 2 * M - 4 * 0.25) / 5;
  rqs.forEach(([k, t, d], i) => {
    const x = W - M - (i + 1) * cw - i * 0.25; // right-to-left order
    card(s, x, 2.85, cw, 3.7);
    badge(s, x + cw / 2 - 0.35, 3.05, k, i === 1 ? ORANGE : NAVY, 0.7);
    s.addText([fa(t, { align: "center", bold: true })], { x: x + 0.1, y: 3.9, w: cw - 0.2, h: 0.6, fontSize: 16,
      color: INK, isTextBox: true, margin: 0 });
    s.addText([fa(d, { align: "center" })], { x: x + 0.15, y: 4.55, w: cw - 0.3, h: 1.8, fontSize: 13,
      color: MUTED, valign: "top", isTextBox: true, margin: 0 });
  });
  s.addNotes("پنج سؤال پژوهشی دقیقاً همان‌هایی است که در راهنمای پروژه آمده؛ سؤال اصلی RQ2 است.");
}

// 4. data
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "داده: ۱۰ پروژه‌ی Java و ماتریس کامل PIT");
  const pp = ds.per_project.slice().sort((a, b) => a.score - b.score);
  s.addChart(pres.charts.BAR, [{ name: "mutation score", labels: pp.map((r) => r.project.replace("toy-", "") +
      (r.setting === "held-out" ? " *" : "")), values: pp.map((r) => +(100 * r.score).toFixed(1)) }], {
    x: M, y: 1.4, w: 6.6, h: 5.4, barDir: "bar", chartColors: [NAVY], showValue: true, dataLabelPosition: "outEnd",
    dataLabelFontSize: 10, dataLabelColor: MUTED, dataLabelFormatCode: "0", catAxisLabelFontSize: 11,
    valAxisLabelFontSize: 10, catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, valAxisMaxVal: 100,
    valGridLine: { color: "E4E3DF", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false,
    showTitle: true, title: "نمره‌ی جهش واقعی هر پروژه (درصد)", titleFontSize: 12, titleColor: INK,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
  });
  para(s, [
    "۱۰ پروژه‌ی کوچک Java با تست JUnit 5 (بانک، هندسه، متن، ساختمان‌داده، ریاضی، تاریخ، parser، انبار، گراف، اعتبارسنجی).",
    `PIT 1.30.1 با fullMutationMatrix و همه‌ی عملگرها: ${ds.mutants.toLocaleString("en-US")} mutant، برای هر mutant فهرست تست‌های کشنده.`,
    "۸ پروژه برای آموزش و ارزیابی leave-one-project-out؛ ۲ پروژه‌ی ستاره‌دار (graph و validator) تا ارزیابی نهایی دست‌نخورده می‌مانند.",
    "پروژه‌های واقعی Apache Commons در java/subjects.csv آماده‌اند و با یک دستور اضافه می‌شوند.",
  ], 7.5, 1.5, 5.2, 5.2, { size: 15 });
  s.addNotes("تقسیم داده بر اساس پروژه است، نه mutant؛ این همان اشتباه رایجی است که راهنما گفته بود.");
}

// 5. features
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "ویژگی‌های هر mutant (بدون اجرای آن)");
  const groups = [
    ["عملگر", "نوع عملگر PIT و خانواده‌ی آن (شرط، ریاضی، return، حذف فراخوانی، ثابت…)"],
    ["ساختار کد", "نوع دستور، عمق تودرتو، اندازه و پیچیدگی متد، موقعیت در متد، اندازه‌ی کلاس، تعداد mutant هم‌خط"],
    ["پوشش", "تعداد تست‌های پوشش‌دهنده و کلاس‌های تست (از فاز coverage در PIT، پیش از اجرای mutant)"],
    ["قدرت تست (oracle)", "تعداد assertها، تست‌هایی که متد جهش‌یافته را مستقیم صدا می‌زنند یا روی آن assert دارند"],
  ];
  const gw = (W - 2 * M - 0.4) / 2, gh = 2.35;
  groups.forEach(([t, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = W - M - (col + 1) * gw - col * 0.4, y = 1.5 + row * (gh + 0.3);
    card(s, x, y, gw, gh);
    badge(s, x + gw - 0.85, y + 0.3, String(i + 1), i === 3 ? ORANGE : NAVY, 0.6);
    s.addText([fa(t, { bold: true })], { x: x + 0.3, y: y + 0.3, w: gw - 1.3, h: 0.6, fontSize: 18, color: INK,
      isTextBox: true, margin: 0, valign: "middle" });
    s.addText([fa(d)], { x: x + 0.3, y: y + 1.0, w: gw - 0.6, h: gh - 1.15, fontSize: 14, color: MUTED,
      isTextBox: true, margin: 0, valign: "top" });
  });
  s.addNotes("قانون ضدنشت: هیچ چیزی که از اجرای mutant به دست می‌آید (status، تست کشنده، تعداد تست اجراشده) ویژگی نیست.");
}

// 6. baselines (single slide)
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "Baselineها: همه با همان داده و همان بودجه");
  const hdr = ["Baseline", "چیست", "اجرای mutant"].map((t) => ({ text: t, options: { bold: true, color: "FFFFFF",
    fill: { color: NAVY }, align: "right", rtlMode: true } }));
  const rows = [
    ["اجرای کامل PIT", "مرجع طلایی، برای محاسبه‌ی خطا", "۱۰۰٪"],
    ["نمونه‌گیری تصادفی", "اجرای تصادفی به اندازه‌ی بودجه، بازه‌ی اطمینان با تصحیح جمعیت محدود", "بودجه"],
    ["نمونه‌گیری طبقه‌ای", "طبقه‌بندی بر اساس خانواده‌ی عملگر، تخصیص متناسب", "بودجه"],
    ["جهش انتخابی (Selective)", "فقط چند عملگر پرکاربرد تا سقف بودجه", "حداکثر بودجه"],
    ["PMT (Zhang و همکاران)", "Random Forest با ویژگی‌های PMT، پیش‌بینی همه بدون اجرا", "۰٪"],
    ["Seshat-lite", "تقریب Seshat: توکن‌های خط جهش‌یافته + رگرسیون لجستیک", "۰٪"],
    ["فقط مدل / Active top-k", "جمع احتمال‌های کالیبره / اجرای نامطمئن‌ترین‌ها به اندازه‌ی بودجه", "۰ / بودجه"],
  ].map((r) => r.map((t, j) => ({ text: t, options: { align: j === 2 ? "center" : "right", rtlMode: true,
    color: INK, fill: { color: "FFFFFF" } } })));
  s.addTable([hdr, ...rows], { x: M, y: 1.45, w: W - 2 * M, colW: [3.2, 6.8, 2.13], fontSize: 14, fontFace: "Vazirmatn",
    border: { type: "solid", color: "D9DEE2", pt: 0.75 }, rowH: 0.62, valign: "middle" });
  s.addText([fa("نام و نسخه‌ی PMT و Seshat را ابتدای کار با مقاله و مخزن اصلی تطبیق دهید؛ اینجا بازپیاده‌سازی شده‌اند.")],
    { x: M, y: 6.6, w: W - 2 * M, h: 0.4, fontSize: 12, color: MUTED, isTextBox: true, margin: 0 });
  s.addNotes("ستون اول: نام baseline؛ ستون آخر: چه درصدی از mutantها واقعاً اجرا می‌شوند.");
}

// 7. algorithm overview
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "روش پیشنهادی ACE-MT: نمای کلی");
  s.addText([fa("Active, Calibrated, model-assisted Estimation of Mutation score", { align: "right" })],
    { x: M, y: 1.2, w: W - 2 * M, h: 0.4, fontSize: 14, color: MUTED, italic: true, isTextBox: true, margin: 0 });
  const steps = [
    ["مدل کالیبره", "XGBoost بین‌پروژه‌ای + کالیبراسیون isotonic ⟵ احتمال p برای هر mutant"],
    ["اطلاعات رایگان", "mutant بدون پوشش = زنده، بدون اجرا"],
    ["نمونه‌گیری فعال", "انتخاب بر اساس عدم‌قطعیت sqrt(p(1−p)) با ۳۰٪ یکنواخت"],
    ["تطبیق با پروژه", "بعد از هر دور، کالیبراسیون Platt روی برچسب‌های واقعی"],
    ["تخمین + بازه", "تخمین‌گر تفاضلی نااریب، ترکیب empirical-Bayes، بازه‌ی ۹۵٪"],
  ];
  const bw = 2.15, gap = 0.37, y = 2.2;
  steps.forEach(([t, d], i) => {
    const x = W - M - (i + 1) * bw - i * gap;
    card(s, x, y, bw, 3.6, i === 2 || i === 4 ? "FDEEE7" : CARD);
    badge(s, x + bw / 2 - 0.3, y + 0.25, String(i + 1), i === 2 || i === 4 ? ORANGE : NAVY, 0.6);
    s.addText([fa(t, { align: "center", bold: true })], { x: x + 0.1, y: y + 1.0, w: bw - 0.2, h: 0.55, fontSize: 16,
      color: INK, isTextBox: true, margin: 0 });
    s.addText([fa(d, { align: "center" })], { x: x + 0.12, y: y + 1.6, w: bw - 0.24, h: 1.9, fontSize: 13, color: MUTED,
      isTextBox: true, margin: 0, valign: "top" });
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LEFT_ARROW, { x: x - gap + 0.05, y: y + 1.65, w: gap - 0.1, h: 0.3,
        fill: { color: "B8C4CC" }, line: { color: "B8C4CC" } });
    }
  });
  s.addText([fa("نوآوری: گام‌های ۳ تا ۵ با هم. انتخاب فعال تخمین را اریب نمی‌کند، چون احتمال انتخاب هر mutant معلوم است و فقط به برچسب‌های قبلی بستگی دارد.")],
    { x: M, y: 6.1, w: W - 2 * M, h: 0.7, fontSize: 15, color: INK, bold: true, isTextBox: true, margin: 0 });
  s.addNotes("در اسلایدهای بعد هر گام را جدا توضیح می‌دهیم.");
}

// 8. step 1-2
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "گام ۱ و ۲: مدل بین‌پروژه‌ای کالیبره و اطلاعات رایگان");
  para(s, [
    { t: "آموزش روی پروژه‌های دیگر (leave-one-project-out)؛ پروژه‌ی هدف هیچ برچسبی به مدل نمی‌دهد.", b: true },
    "مدل: XGBoost (قابل تعویض با LightGBM، RF و LogReg از فایل YAML).",
    "کالیبراسیون isotonic با foldهای گروه‌بندی‌شده بر اساس پروژه؛ یعنی «احتمال ۰٫۷» واقعاً حدود ۷۰٪ کشته‌شدن باشد.",
    "بدون کالیبراسیون، جمع احتمال‌ها نمره‌ی غلط می‌دهد (یکی از اشتباه‌های رایج در راهنما).",
    "mutantهای بدون پوشش قطعاً زنده‌اند و بدون هزینه کنار گذاشته می‌شوند. این مزیت به همه‌ی روش‌ها، از جمله baselineها، داده شده تا مقایسه منصفانه باشد.",
  ], 5.3, 1.5, 7.4, 5.2, { size: 16 });
  card(s, M, 1.55, 4.3, 5.0);
  s.addText([fa("کیفیت پیش‌بینی (AUC، mutantهای پوشش‌داده‌شده)", { align: "center", bold: true })],
    { x: M + 0.2, y: 1.75, w: 3.9, h: 0.6, fontSize: 14, color: INK, isTextBox: true, margin: 0 });
  stat(s, M + 0.2, 2.5, 3.9, f3(auc("cross-project", "xgboost")), "بین‌پروژه‌ای (LOPO)", NAVY);
  stat(s, M + 0.2, 4.2, 3.9, f3(auc("held-out", "xgboost")), "پروژه‌های held-out", ORANGE);
  s.addNotes("AUC روی mutantهای پوشش‌داده‌شده گزارش شده، چون تشخیص بدون پوشش‌ها کار ساده‌ای است و عدد را بی‌جهت بالا می‌برد.");
}

// 9. step 3
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "گام ۳: نمونه‌گیری فعال و تخمین‌گر تفاضلی");
  para(s, [
    "در هر قدم یک mutant اجرانشده با احتمال q انتخاب و واقعاً اجرا می‌شود.",
    "mutantهای نامطمئن (p نزدیک ۰٫۵) شانس بیشتری دارند؛ ۳۰٪ یکنواخت تضمین می‌کند هر mutant شانس انتخاب داشته باشد.",
    "هر انتخاب یک تخمین نااریب از تعداد کشته‌ها می‌دهد: «پیش‌بینی مدل + خطای مدل روی نمونه، وزن‌دار با ۱/q».",
    "اگر مدل خوب باشد، خطا کوچک است و واریانس پایین می‌آید. اگر بد باشد، تخمین باز هم نااریب می‌ماند.",
  ], 6.6, 1.5, 6.1, 5.2, { size: 16 });
  card(s, M, 1.6, 5.7, 4.9, "1F3A4D");
  const fx = [
    "q_i ∝ 0.7·sqrt(p_i(1−p_i)) + 0.3·(1/n)",
    "",
    "T_j = Σ_executed y + Σ_unexecuted p",
    "        + (y_j − p_j) / q_j",
    "",
    "E[T_j] = #killed   (unbiased)",
  ];
  s.addText(fx.map((t, i) => ({ text: t, options: { breakLine: i < fx.length - 1 } })), { x: M + 0.3, y: 1.9, w: 5.1,
    h: 4.3, fontFace: "Courier New", fontSize: 16, color: "FFFFFF", valign: "middle", align: "left", isTextBox: true,
    margin: 0 });
  s.addNotes("این ایده شبیه active testing در یادگیری ماشین است: نمونه‌گیری وزن‌دار با اصلاح importance weight.");
}

// 10. step 4-5
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "گام ۴ و ۵: تطبیق، ترکیب و بازه‌ی اطمینان");
  card(s, M, 1.6, 5.7, 4.9, "1F3A4D");
  const fx = [
    "after each round r = 1..4:",
    "  p ← Platt(logit p_base ; labels so far)",
    "",
    "T̂ = mean_j T_j      V = s²(T_j) / n",
    "M  = Σ_executed y + Σ_unexecuted p",
    "w  = V / (V + max(0, (T̂ − M)² − V))",
    "score = (w·M + (1−w)·T̂) / N",
    "CI95  = score ± 1.96·sqrt(V) / N",
  ];
  s.addText(fx.map((t, i) => ({ text: t, options: { breakLine: i < fx.length - 1 } })), { x: M + 0.3, y: 1.9, w: 5.2,
    h: 4.3, fontFace: "Courier New", fontSize: 15, color: "FFFFFF", valign: "middle", align: "left", isTextBox: true,
    margin: 0 });
  para(s, [
    { t: "تطبیق: مدل بین‌پروژه‌ای ممکن است برای پروژه‌ی جدید اریب سراسری داشته باشد؛ با برچسب‌های اجراشده دوباره کالیبره می‌شود.", b: false },
    "چون p و q فقط به برچسب‌های قبلی وابسته‌اند، نااریبی حفظ می‌شود.",
    "ترکیب empirical-Bayes: به پیش‌بینی مدل فقط تا جایی اعتماد می‌کنیم که داده نشان ندهد اریب است. این ترکیب در بودجه‌ی خیلی کم (۵٪) بیشترین سود را دارد.",
    "بازه‌ی اطمینان از واریانس تخمین‌های T_j به دست می‌آید؛ پوشش ۹۵٪ آن در نتایج بررسی شده است.",
  ], 6.6, 1.5, 6.1, 5.2, { size: 15 });
  s.addNotes("وزن w خودکار است: اگر تفاوت مدل و نمونه کمتر از نویز باشد، به مدل تکیه می‌کنیم؛ در غیر این صورت به نمونه.");
}

// 11. pseudocode
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "شبه‌کد و پیاده‌سازی");
  card(s, M, 1.45, 7.6, 5.3, "14232E");
  const code = [
    "def ace(project, budget):",
    "    p = calibrated_cross_project_model(project)",
    "    pool = covered_mutants(project)      # uncovered = survived",
    "    for r in range(4):                   # rounds",
    "        for _ in range(budget // 4):",
    "            q = 0.7*unc(p) + 0.3*uniform  # unexecuted only",
    "            j = sample(pool, q); y[j] = run_pit(j)",
    "            T.append(known_y + sum(p_unknown) + (y[j]-p[j])/q[j])",
    "        p = platt_adapt(p_base, executed, y)",
    "    est, V = mean(T), var(T)/len(T)",
    "    return eb_combine(est, model_pred(p), V), ci(V)",
  ];
  s.addText(code.map((t, i) => ({ text: t, options: { breakLine: i < code.length - 1 } })), { x: M + 0.25, y: 1.65,
    w: 7.2, h: 4.9, fontFace: "Courier New", fontSize: 13, color: "E8EEF2", valign: "top", align: "left",
    isTextBox: true, margin: 0 });
  para(s, [
    { t: "کد: pmt/estimators.py → ace()", b: true },
    "همه‌ی پارامترها در configs/default.yaml",
    "دستور اجرا: python -m pmt all",
    "تست واحد نااریبی: pytest -q",
    "Java/PIT، Python/mutmut، CSV عمومی و داده‌ی مصنوعی",
  ], 8.5, 1.5, 4.2, 5.2, { size: 15 });
  s.addNotes("کد ماژولار است؛ CONTEXT.md نقشه‌ی همه‌ی فایل‌هاست.");
}

// 12. results (last slide) | فارسی: اسلاید نتایج - اعداد خودکار از summary.json
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  title(s, "نتایج");
  const ms = ["ace", "random", "stratified", "model_only", "selective"];
  const chartData = ms.map((m) => ({ name: METHOD_FA[m], labels: budgets.map((b) => `${Math.round(b * 100)}%`),
    values: budgets.map((b) => +get(b, m).toFixed(4)) }));
  s.addChart(pres.charts.LINE, chartData, {
    x: M, y: 1.3, w: 6.3, h: 5.15, chartColors: ms.map((m) => METHOD_COLOR[m]), lineSize: 2, lineDataSymbolSize: 7,
    showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: "+mn-lt",
    valAxisLabelFormatCode: "0.00", valAxisMinVal: 0, catAxisLabelColor: MUTED, valAxisLabelColor: MUTED,
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E4E3DF", size: 0.5 }, catGridLine: { style: "none" }, showTitle: true,
    title: "خطای مطلق نمره‌ی جهش (MAE) در برابر بودجه", titleFontSize: 12, titleColor: INK, titleFontFace: "+mn-lt",
  });
  s.addText([fa("میانگین روی ۱۰ پروژه و ۳۰ تکرار. «فقط مدل» هیچ mutantی اجرا نمی‌کند.", { align: "center" })],
    { x: M, y: 6.45, w: 6.3, h: 0.45, fontSize: 10, color: MUTED, isTextBox: true, margin: 0 });
  // KPI tiles (right side)
  const kx = 7.2, kw = (W - M - kx - 0.25) / 2;
  const tiles = [
    [pct(redu[0]), `کاهش خطا نسبت به تصادفی در بودجه‌ی ${Math.round(budgets[0] * 100)}٪`, ORANGE],
    [pct(redu[1]), `کاهش خطا نسبت به تصادفی در بودجه‌ی ${Math.round(budgets[1] * 100)}٪`, ORANGE],
    [pct(get(budgets[1], "ace", "ci_coverage")), "پوشش بازه‌ی ۹۵٪ ACE-MT (بودجه ۱۰٪)", NAVY],
    [pct(cost("ace", budgets[1]).test_run_frac || 0), "سهم اجرای تست لازم در بودجه‌ی ۱۰٪ (RQ3)", NAVY],
  ];
  tiles.forEach(([v, l, c], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = W - M - (col + 1) * kw - col * 0.25, y = 1.35 + row * 1.75;
    card(s, x, y, kw, 1.55);
    s.addText(v, { x, y: y + 0.1, w: kw, h: 0.75, fontSize: 30, bold: true, color: c, align: "center", isTextBox: true, margin: 0 });
    s.addText([fa(l, { align: "center" })], { x: x + 0.1, y: y + 0.85, w: kw - 0.2, h: 0.65, fontSize: 11, color: MUTED,
      isTextBox: true, margin: 0, valign: "top" });
  });
  const b10 = budgets[1];
  const sr = statFor(b10, "random");
  const pv = sr.length ? Math.min(...sr.map((r) => r.wilcoxon_p)) : NaN;
  const c10 = cost("ace", b10);
  const rq5 = S.rq5_policies || [];
  const ab = (v) => (rq5.find((r) => r.variant === v) || {}).mae;
  para(s, [
    `RQ1: AUC بین‌پروژه‌ای ${f3(auc("cross-project", "xgboost"))} و درون‌پروژه‌ای ${f3(auc("within-project", "xgboost"))}. PMT و Seshat-lite بدون اجرا خطای ${f3(get(b10, "pmt"))} و ${f3(get(b10, "seshat_lite"))} دارند.`,
    `RQ2: در مقایسه با تصادفی در ۱۰٪، Wilcoxon p = ${isFinite(pv) ? pv.toPrecision(2) : "n/a"}. «فقط مدل» بازه‌ی نامعتبر دارد (پوشش ${pct(get(b10, "model_only", "ci_coverage"))}).`,
    `RQ4: τ برای ACE-MT ${f3(tau("ace"))} و برای تصادفی ${f3(tau("random"))}؛ PMT در رتبه‌بندی بهتر است (${f3(tau("pmt"))}).`,
    `RQ5: مؤثرترین جزء ترکیب empirical-Bayes است (بدون آن MAE = ${f3(ab("ace_no_combination"))} در برابر ${f3(ab("ace (default)"))}).`,
  ], kx, 4.95, W - M - kx, 2.15, { size: 11 });
  s.addNotes("همه‌ی اعداد این اسلاید از results/summary.json خوانده می‌شوند. جدول کامل در results/summary.md است.");
}

// فارسی: pptxgenjs فونت «complex script» (cs) تم را خالی می‌گذارد؛ متن فارسی از اسلات cs فونت می‌گیرد،
// پس آن را (و ea را) روی Vazirmatn می‌گذاریم تا همه‌ی متن‌های فارسی با وزیرمتن نمایش داده شوند.
async function setComplexScriptFont(file, font) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  for (const name of Object.keys(zip.files).filter((n) => /^ppt\/theme\/theme\d+\.xml$/.test(n))) {
    let xml = await zip.file(name).async("string");
    xml = xml.replace(/<a:(cs|ea) typeface=""/g, `<a:$1 typeface="${font}"`);
    zip.file(name, xml);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

pres.writeFile({ fileName: OUT }).then(async () => {
  const apply = process.env.APPLY_THEME;
  if (apply && fs.existsSync(apply)) {
    const { applyTheme } = require(apply);
    await applyTheme(OUT, THEME);
  }
  await setComplexScriptFont(OUT, THEME.bodyFontFace);
  console.log("written", OUT);
});
