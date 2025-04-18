# برنامه مدیریت کارها

این برنامه یک برنامه مدیریت کارهای روزانه است که با استفاده از Python و PyQt6 ساخته شده است.

## ویژگی‌ها

- تقویم شمسی برای انتخاب تاریخ
- امکان اضافه کردن کارهای جدید با عنوان و توضیحات
- امکان حذف بصورت تکی و یکجای تسک ها
- اولویت‌بندی کارها (کم، متوسط، زیاد)
- تم لایت و دارک
- رابط کاربری مناسب و راست‌چین
- استفاده از فونت وزیر
- ذخیره‌سازی اطلاعات در دیتابیس SQLite

## نصب و راه‌اندازی

1. ابتدا Python را از [python.org](https://www.python.org/downloads/) نصب کنید.

2. وابستگی‌های مورد نیاز را نصب کنید:
```bash
pip install -r requirements.txt
```

3. فونت وزیر را نصب کنید:
   - فایل فونت وزیر را از [این لینک](https://github.com/rastikerdar/vazir-font) دانلود کنید
   - فایل‌های فونت را در پوشه فونت‌های ویندوز کپی کنید

4. برنامه را اجرا کنید:
```bash
python main.py
```

## تبدیل به فایل اجرایی

برای تبدیل برنامه به فایل اجرایی (.exe)، دستور زیر را اجرا کنید:
```bash
pyinstaller --onefile --windowed main.py
```

فایل اجرایی در پوشه `dist` ایجاد خواهد شد. 
