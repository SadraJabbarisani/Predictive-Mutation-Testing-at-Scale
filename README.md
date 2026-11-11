# تیم ۸ — آزمون جهش کم‌هزینه با پیش‌بینی یادگرفته‌شده
## Predictive Mutation Testing at Scale — ACE-MT

بسته‌ی کامل کد، داده و ارائه برای پروژه‌ی هشتم راهنمای «۱۵ پروژه‌ی آزمون نرم‌افزار».

**ایده در یک جمله:** به‌جای اجرای همه‌ی mutantها با PIT، فقط ۵ تا ۲۰ درصد آن‌ها را
هوشمندانه انتخاب و اجرا می‌کنیم. یک مدل کالیبره‌شده‌ی cross-project بقیه را پیش‌بینی می‌کند
و یک تخمین‌گر نااریب (difference estimator) نمره‌ی جهش را با بازه‌ی اطمینان ۹۵٪ می‌دهد.

| بخش | محتوا |
|---|---|
| `java/` | ۱۰ پروژه‌ی Java با تست JUnit 5 (`java/subjects/toy-*`)، اسکریپت اجرای PIT با full matrix، فهرست پروژه‌های واقعی Apache Commons (`java/subjects.csv`) |
| `data/raw/` | خروجی واقعی PIT 1.30.1 برای ۱۰ پروژه: ۲٬۴۵۱ mutant همراه با ماتریس کامل mutant × test |
| `data/processed/` | دیتاست نهایی، یک سطر برای هر mutant (ویژگی‌ها + برچسب) در قالب `mutants.csv` و `.pkl` |
| `pmt/` | کتابخانه‌ی Python: ویژگی‌ها، مدل‌ها، baselineها، ACE-MT، RQ1 تا RQ5، گزارش |
| `configs/` | همه‌ی پارامترها در YAML (`default.yaml`، و `quick.yaml` برای اجرای سریع) |
| `results/` | نتایج خام (CSV)، جدول‌ها (`summary.md`)، نمودارها، `environment.json` |
| `presentation/` | فایل ارائه (`.pptx` و `.pdf`) با فونت وزیرمتن، اسکریپت ساخت آن از `results/summary.json`، و فایل‌های فونت در `presentation/fonts/` (قبل از باز کردن pptx نصب کنید) |
| `python_mutmut/` | مسیر اختیاری Python (تبدیل خروجی mutmut به CSV عمومی) |
| `notebooks/` | نوت‌بوک اجرا روی Google Colab |
| `docs/` | توضیح روش (`METHOD.md`)، قالب داده (`DATA_FORMAT.md`)، دستورالعمل‌های تغییر (`EXTENDING.md`) |
| `CONTEXT.md` | **نقشه‌ی پروژه برای چت جدید**. فقط همین فایل را بدهید تا هوش مصنوعی بداند کجا را تغییر دهد |

## اجرا (Quick start)
```bash
pip install -r requirements.txt          # یا: bash scripts/setup.sh
python -m pmt all --config configs/quick.yaml   # تست سریع (~۳ دقیقه)
python -m pmt all                                # اجرای کامل، ۳۰ تکرار (~۲۰ تا ۳۰ دقیقه روی ۴ CPU)
pytest -q                                         # تست‌های واحد
```
خروجی‌ها: `results/summary.md` و `results/figures/*.png`.

بازتولید کامل از صفر، از جمله اجرای دوباره‌ی PIT (به Java 11+ و Maven نیاز دارد):
```bash
bash scripts/run_all.sh
```
اضافه کردن پروژه‌ی واقعی: در `java/subjects.csv` مقدار `enabled=1` بگذارید و دستور
`bash java/scripts/collect_all.sh commons-cli` را اجرا کنید.

## گزینه‌ها (همه از طریق YAML یا `--set`)
* **زبان / منبع داده:** Java+PIT (پیش‌فرض)، Python+mutmut یا هر زبان دیگر از راه CSV عمومی (`dataset.source=generic_csv`)، داده‌ی مصنوعی برای مطالعه‌ی مقیاس (`dataset.source=synthetic`)
* **مدل:** `xgboost | lightgbm | rf | logreg | hgb`، کالیبراسیون `isotonic | sigmoid | none`
* **سیاست انتخاب:** `hybrid | uncertainty | uniform`، تطبیق `platt | refit | none`، همسایه‌ها `line/method`، ترکیب empirical-Bayes
* **بودجه‌ها و تکرارها:** `budgets`، `seeds`

## پرسش‌های پژوهشی ↔ فایل نتیجه
RQ1 `rq1_prediction.csv` · RQ2 `rq2_estimates.csv` و `rq2_stats.csv` · RQ3 `rq3_cost.csv` ·
RQ4 `rq4_ranking.csv` · RQ5 `rq5_ablation.csv`

## English summary
Self-contained replication package. PIT full-matrix ground truth for 10 bundled Java subjects
(2,451 mutants). Cross-project calibrated gradient-boosting model plus **ACE-MT**:
uncertainty-weighted active sampling, a difference estimator that stays unbiased under adaptive
sampling, per-round Platt adaptation to the target project, and an empirical-Bayes combination
with the model prediction. Compared against full PIT, random, stratified, selective mutation,
PMT, Seshat-lite, model-only and active top-k under the same budget, with Wilcoxon/A12 tests.
See `CONTEXT.md` for the code map and `docs/METHOD.md` for the algorithm.

> نکته‌ی صداقت علمی: پروژه‌های بسته کوچک و خودنوشته‌اند (برای اجرای مطمئن روی CPU/Colab).
> برای مقاله، طبق راهنما ۸ تا ۱۲ پروژه‌ی واقعی (مثلاً Apache Commons از `java/subjects.csv`) اضافه کنید.
> نام و دسترسی baselineها (PMT، Seshat) را هم در ابتدای کار بررسی کنید.
