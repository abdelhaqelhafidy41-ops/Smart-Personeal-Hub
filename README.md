# المركز الشخصي الذكي - Smart Personal Hub

تطبيق Desktop متكامل بلغة Python باستخدام مكتبة Flet v0.86.5، يعمل 100% أوفلاين بدون الحاجة للإنترنت.

## المميزات الرئيسية

### 10 أقسام شاملة:

1. **منظم المهام (To-Do)** - إضافة وتتبع المهام اليومية مع الأولويات
2. **حاسبة المصاريف** - إدارة الدخل والمصاريف مع رسوم بيانية وتصدير Excel
3. **مكتبة الكتب** - تتبع الكتب المقروءة مع نسب التقدم والتقييمات
4. **مدير كلمات السر** - تخزين آمن مع تشفير Fernet وتوليد كلمات قوية
5. **محول الوحدات** - تحويل الطول، الوزن، الحرارة، الوقت، والعملات
6. **الجدول الدراسي** - تنظيم الامتحانات والواجبات مع تصدير PDF
7. **مخزن الوصفات** - حفظ وصفات الطعام مع البحث وقوائم التسوق
8. **برنامج الفواتير** - إنشاء الفواتير وحساب الربح مع تصدير PDF
9. **تطبيق القرآن** - 114 سورة مع متابعة الورد اليومي والاختبارات
10. **منظم الملفات** - ترتيب الصور وإعادة تسمية دفعية وحذف المكررات

## المتطلبات

- Python 3.8+
- pip (مدير الحزم)

## التثبيت والتشغيل

### 1. الدخول إلى مجلد المشروع

```bash
cd "Smart Personeal Hub"
cd smart_personeal/src
```

### 2. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 3. تشغيل التطبيق

```bash
python main.py
```

أو استخدام Flet مباشرة:

```bash
flet run main.py
```

## الميزات التقنية

✅ **قاعدة بيانات SQLite محلية** - حفظ جميع البيانات محلياً بدون الحاجة للإنترنت

✅ **واجهة ثنائية اللغة** - دعم كامل للعربية (RTL) والإنجليزية (LTR)

✅ **Dark Mode و Light Mode** - تبديل سهل بين الثيمات

✅ **تشفير البيانات** - حماية كلمات السر باستخدام Fernet

✅ **رسوم بيانية** - عرض البيانات برسوم Pie Chart

✅ **تصدير البيانات** - Excel و PDF و TXT

✅ **تصميم عصري** - واجهة مستخدم سهلة وجميلة مع Karo وظلال

✅ **بدون إنترنت** - يعمل 100% أوفلاين

## التحويل إلى ملف تنفيذي (EXE)

لتحويل التطبيق إلى ملف EXE قابل للتشغيل على Windows:

```bash
flet pack main.py
```

سيتم إنشاء ملف `.exe` جاهز للتشغيل على أي جهاز Windows بدون الحاجة لتثبيت Python.

## هيكل المشروع

```
smart_personeal/
├── src/
│   ├── main.py              # الملف الرئيسي الوحيد (كل الكود هنا)
│   ├── quran.json          # بيانات القرآن الكريم
│   ├── requirements.txt      # المكتبات المطلوبة
│   └── hub.db              # قاعدة البيانات (تُنشأ تلقائياً)
├── assets/
│   ├── covers/             # صور أغلفة الكتب
│   ├── recipes/            # صور الوصفات
│   └── charts/             # الرسوم البيانية
└── exports/                # الملفات المصدّرة (Excel, PDF)
```

## قاعدة البيانات

التطبيق يستخدم SQLite محلي بملف `hub.db` يحتوي على الجداول التالية:

- `tasks` - المهام
- `expenses` - المصاريف
- `books` - الكتب
- `passwords` - كلمات السر
- `rates` - أسعار العملات
- `history` - سجل التحويلات
- `schedule` - الجدول الدراسي
- `recipes` - الوصفات
- `products` - المنتجات
- `invoices` - الفواتير
- `quran_progress` - تقدم القرآن

## الملفات المهمة

### main.py
ملف واحد يحتوي على:
- 10 classes لكل قسم من الأقسام
- دوال مساعدة لقاعدة البيانات
- دوال التشفير
- الواجهة الرئيسية كاملة
- جميع الإجراءات مع الـ page.update()

### quran.json
ملف JSON يحتوي على 114 سورة من القرآن الكريم مع عدد الآيات.

### requirements.txt
المكتبات المطلوبة:
- flet==0.86.5
- cryptography
- Pillow
- matplotlib
- openpyxl
- reportlab

## التعليقات في الكود

جميع الدوال والـ Classes مزودة بتعليقات بالعربية توضح وظيفتها.

## المميزات الإضافية

- ✅ عرض الإحصائيات (عدد المهام المنجزة، الرصيد الحالي، إلخ)
- ✅ فلترة البيانات (اليوم، الأسبوع، المنجزة)
- ✅ تنبيهات (قبل الامتحان بـ 3 أيام)
- ✅ نسخ لكليبورد بنقرة واحدة
- ✅ معاينة الصور
- ✅ تحديث البيانات في الوقت الفعلي

## ملاحظات مهمة

1. **التطبيق يعمل أوفلاين بالكامل** - جميع البيانات محفوظة محلياً
2. **البيانات محفوظة تلقائياً** - لا داعي لحفظ يدوي
3. **قاعدة البيانات تُنشأ تلقائياً** - عند أول تشغيل
4. **الإعدادات محفوظة** - اللغة والثيم يُحفظان تلقائياً

## الترخيص

هذا المشروع مفتوح المصدر ومتاح للاستخدام الشخصي والتجاري.

---

**تم الإنشاء بواسطة:** فريق التطوير
**الإصدار:** 1.0
**تاريخ:** 2026

Run as a web app:

```bash
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/).

## Build the app

### Android

```bash
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).
