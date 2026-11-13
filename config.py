# ================== الإعدادات (عدّل هذا الملف فقط) ==================
# --- القارئ (اسم المجلد في everyayah.com) ---
RECITER_FOLDER = "Alafasy_128kbps"
RECITER_NAME_AR = "مشاري راشد العفاسي"

# --- الحساب ---
CHANNEL_HANDLE = "@noor.alayat"          # غيّره ليوزر حسابك
HASHTAGS = "#قرآن #القرآن_الكريم #تلاوة #سكينة #آيات #quran #quranrecitation #islam"

# --- حدود المدة ---
MAX_TOTAL_SECONDS = 57.5   # هدف التقسيم (هامش أمان)
HARD_LIMIT = 59.0          # يُرفض أي فيديو عادي أطول من هذا
GAP = 0.40                 # صمت قصير بعد كل آية
ALLOW_LONG = False         # False = تُتخطى الآيات التي لا تتسع في 59 ثانية (مثل البقرة 282) ويُسجَّل ذلك في skipped_long.txt
                           # True  = تُنشر كاملة في فيديو أطول من 59 ثانية

# أوقات النشر تُضبط في .github/workflows/post.yml (توقيت UTC)

# --- التصميم ---
FONT_VERSE_FILE = "AmiriQuran-Regular.ttf"   # خط الآيات (مصحفي)
FONT_TITLE_FILE = "ArefRuqaa-Bold.ttf"       # خط اسم السورة
COLOR_TEXT = "#FFFFFF"                       # لون الآية
COLOR_ACCENT = "#F2D27A"                     # لون ذهبي (اسم السورة ورقم الآية)
BG_BLUR = 2.0                                # تمويه خفيف للخلفية ليبرز النص (0 = بدون)
BG_BRIGHTNESS = -0.20                        # تغميق الخلفية قليلًا
