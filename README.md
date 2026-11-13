# ريلز القرآن الكريم — يعمل بالكامل على GitHub (بدون سيرفر ولا جهاز)

GitHub Actions يشغّل المهمة في أوقاتها: ينتج الفيديو التالي، وينشره على إنستغرام، ويحفظ التقدم.
بعد سورة الناس يعود إلى الفاتحة تلقائيًا. الرمز يُجدَّد أسبوعيًا تلقائيًا.

## الإعداد (مرة واحدة)

### 1) حساب إنستغرام والـ API
1. حوّل الحساب إلى **احترافي (Business/Creator)**.
2. على https://developers.facebook.com/apps أنشئ تطبيقًا → أضف المنتج **Instagram API with Instagram Login**.
3. أضف حسابك كـ Instagram tester، ثم من صفحة Instagram API setup اضغط **Generate token**.
   احفظ **رقم الحساب** و**الرمز**.

### 2) مستودع GitHub
1. أنشئ مستودعًا جديدًا (يُفضَّل **Private**) وارفع إليه كل محتويات هذا المجلد (بما فيها `.github/`):
   ```
   git init && git add . && git commit -m init
   git branch -M main && git remote add origin https://github.com/USER/REPO.git && git push -u origin main
   ```
   (أو استعمل تطبيق GitHub Desktop.)
2. عدّل `config.py` (اسم القارئ، اليوزر، الهاشتاقات) ثم ارفع التعديل.

### 3) الأسرار (Settings → Secrets and variables → Actions → New repository secret)
| الاسم | القيمة |
|---|---|
| `IG_USER_ID` | رقم حساب إنستغرام |
| `IG_ACCESS_TOKEN` | الرمز من الخطوة 1 |
| `GH_PAT` | رمز GitHub الشخصي (لتجديد الرمز تلقائيًا): Settings → Developer settings → Fine-grained tokens → اختر هذا المستودع فقط → Permissions → **Secrets: Read and write** |

وفي Settings → Actions → General → Workflow permissions اختر **Read and write permissions**.

### 4) الخلفيات
فيديو طويل واحد أو أكثر (يُفضَّل عمودي 1080×1920). في كل فيديو يختار السكربت ملفًا ومقطعًا **عشوائيًا**.
- **الأفضل:** Releases → Draft a new release → اكتب الوسم `backgrounds` → ارفع الفيديوهات (حتى 2 GB للملف) → Publish.
- **أو:** ضع ملفات أقل من 100 MB في مجلد `backgrounds/` وارفعها مع المستودع.

مصادر مجانية: pexels.com/videos و pixabay.com/videos (طبيعة/سماء/بحر، بدون أشخاص ولا موسيقى).

### 5) التشغيل الأول
1. تبويب **Actions** → **1 - Build plan (run once)** → Run workflow. (يحمّل المصحف ويبني الخطة ويحفظ `plan.json`.)
2. **2 - Post next Reel** → Run workflow مع تفعيل **dry_run**: يُنتج 3 فيديوهات للمراجعة ولا ينشر شيئًا.
   نزّلها من قسم Artifacts أسفل صفحة التشغيل وراجعها.
3. بعد رضاك لا تفعل شيئًا: النشر يبدأ تلقائيًا في المواعيد المحددة في `.github/workflows/post.yml`.

## مواعيد النشر
في `post.yml` تحت `cron` بتوقيت **UTC** (المغرب = UTC+1، وUTC+0 في رمضان). الافتراضي 3 مرات يوميًا.
GitHub قد يؤخر التشغيل عدة دقائق وأحيانًا أكثر.

## ملاحظات
- **التكلفة:** المستودعات العامة مجانية بلا حد. الخاصة لها حصة شهرية مجانية (قد تتغير، راجع خطتك). كل تشغيل نحو 4–6 دقائق.
- **التنبيهات:** إذا فشل النشر يرسل لك GitHub بريدًا، ويُعاد المحاولة في الموعد التالي دون تخطي الآية.
- **توقف الجدولة:** GitHub قد يوقف الأعمال المجدولة في المستودعات غير النشطة. التقدم يُحفَظ بالالتزام (commit) يوميًا فغالبًا لا تُوقَف، وإن حدث فاضغط Enable في تبويب Actions.
- **الآيات الأطول من 59 ثانية:** تُتخطى وتُسجَّل في `skipped_long.txt` (غيّر `ALLOW_LONG` في config.py لنشرها كاملة).
- **المصادر:** https://api.quran.com/api/v4 • https://everyayah.com • https://developers.facebook.com/documentation/instagram-platform/content-publishing
