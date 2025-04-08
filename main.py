import sys
import jdatetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QCalendarWidget, QListWidget, QListWidgetItem, QPushButton, 
                            QLineEdit, QTextEdit, QComboBox, QLabel, QMessageBox, QCheckBox, QDialog)
from PyQt6.QtCore import Qt, QDate, QLocale
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
import sqlite3
from datetime import datetime
import os
from PyQt6.QtWidgets import QStyle

class JalaliCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_jalali_calendar()
        self.selectionChanged.connect(self.update_header)
        self.is_dark_mode = False
        
    def setup_jalali_calendar(self):
        # تنظیم تقویم به فارسی
        self.setLocale(QLocale(QLocale.Language.Persian, QLocale.Country.Iran))
        
        # مخفی کردن نوار بالایی تقویم
        self.setNavigationBarVisible(False)
        
        # تنظیم نام‌های ماه‌های شمسی
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        
        # تنظیم نام‌های ماه‌ها
        self.setFirstDayOfWeek(Qt.DayOfWeek.Saturday)
        
        # ایجاد لیبل برای نمایش تاریخ شمسی
        self.header_label = QLabel()
        self.header_label.setFont(QFont("Vazir", 12))
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("""
            QLabel {
                background-color: #6A1B9A;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
        """)
        self.update_header()
        
    def update_header(self):
        date = self.selectedDate()
        month_names = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                      "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
        month_name = month_names[date.month - 1]
        self.header_label.setText(f"{month_name} {date.year}")
        
    def selectedDate(self):
        date = super().selectedDate()
        jdate = jdatetime.date.fromgregorian(date=date.toPyDate())
        return jdate
        
    def paintCell(self, painter, rect, date):
        # تبدیل تاریخ میلادی به شمسی
        jdate = jdatetime.date.fromgregorian(date=date.toPyDate())
        
        # تنظیم رنگ و فونت
        painter.setFont(QFont("Vazir", 9))
        
        # تعیین رنگ متن بر اساس تم برنامه
        if self.is_dark_mode:
            text_color = QColor(200, 200, 200)  # رنگ روشن برای تم تیره
        else:
            text_color = QColor(0, 0, 0)  # رنگ تیره برای تم روشن
        
        # اگر روز جمعه است، رنگ قرمز استفاده کن
        if date.dayOfWeek() == 5:  # 5 معادل جمعه در Qt است
            painter.setPen(QColor(255, 0, 0))
        else:
            painter.setPen(text_color)
        
        # رسم عدد روز
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(jdate.day))
        
        # اگر روز اول ماه است، نام ماه را نمایش بده
        if jdate.day == 1:
            month_names = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            month_name = month_names[jdate.month - 1]
            painter.setFont(QFont("Vazir", 7))
            painter.drawText(rect.adjusted(2, 2, -2, -2), 
                           Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, 
                           month_name)

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("برنامه مدیریت کارها")
        self.setMinimumSize(1000, 600)
        
        # تنظیم فونت وزیر برای کل برنامه
        self.vazir_font = QFont("Vazir", 10)
        self.vazir_font.setBold(True)
        self.setFont(self.vazir_font)
        
        # ایجاد دیتابیس
        self.recreate_database()
        
        # تنظیم تم پیش‌فرض
        self.is_dark_mode = False
        self.setup_ui()
        self.apply_light_theme()
        
        # تنظیم تاریخ امروز
        today = jdatetime.date.today()
        gregorian_date = today.togregorian()
        self.calendar.setSelectedDate(QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day))
        self.load_todos(self.calendar.selectedDate())
        
    def recreate_database(self):
        # ایجاد دیتابیس جدید فقط در صورت عدم وجود
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS todos
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date TEXT,
                     title TEXT,
                     description TEXT,
                     priority INTEGER,
                     completed INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()
        
    def setup_ui(self):
        # ویجت اصلی
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # سمت راست: تقویم
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # ایجاد تقویم
        self.calendar = JalaliCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.load_todos)
        
        # اضافه کردن لیبل تاریخ شمسی
        self.calendar.header_label.setFont(self.vazir_font)
        right_layout.addWidget(self.calendar.header_label)
        right_layout.addWidget(self.calendar)
        
        # دکمه‌های عملیات
        button_layout = QHBoxLayout()
        
        # دکمه افزودن
        add_button = QPushButton("افزودن")
        add_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        add_button.clicked.connect(self.add_todo)
        add_button.setFont(self.vazir_font)
        
        # دکمه ویرایش
        edit_button = QPushButton("ویرایش")
        edit_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        edit_button.clicked.connect(self.edit_todo)
        edit_button.setFont(self.vazir_font)
        
        # دکمه حذف
        delete_button = QPushButton("حذف")
        delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        delete_button.clicked.connect(self.delete_todo)
        delete_button.setFont(self.vazir_font)
        
        # دکمه حذف همه
        delete_all_button = QPushButton("حذف همه")
        delete_all_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        delete_all_button.clicked.connect(self.delete_all_todos)
        delete_all_button.setFont(self.vazir_font)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(delete_all_button)
        button_layout.addStretch()
        
        # دکمه تغییر تم
        theme_button = QPushButton("تغییر تم")
        theme_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        theme_button.clicked.connect(self.toggle_theme)
        theme_button.setFont(self.vazir_font)
        button_layout.addWidget(theme_button)
        
        right_layout.addLayout(button_layout)
        
        layout.addWidget(right_panel)
        
        # سمت چپ: لیست کارها و فرم
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # لیست کارها
        self.todo_list = QListWidget()
        self.todo_list.setFont(self.vazir_font)
        left_layout.addWidget(QLabel("کارهای امروز:"))
        left_layout.addWidget(self.todo_list)
        
        # فرم اضافه کردن کار جدید
        form_layout = QVBoxLayout()
        
        # عنوان
        title_layout = QHBoxLayout()
        title_label = QLabel("عنوان:")
        title_label.setFont(self.vazir_font)
        title_layout.addWidget(title_label)
        self.title_input = QLineEdit()
        self.title_input.setFont(self.vazir_font)
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)
        
        # توضیحات
        desc_layout = QVBoxLayout()
        desc_label = QLabel("توضیحات:")
        desc_label.setFont(self.vazir_font)
        desc_layout.addWidget(desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setFont(self.vazir_font)
        desc_layout.addWidget(self.desc_input)
        form_layout.addLayout(desc_layout)
        
        # اولویت
        priority_layout = QHBoxLayout()
        priority_label = QLabel("اولویت:")
        priority_label.setFont(self.vazir_font)
        priority_layout.addWidget(priority_label)
        self.priority_combo = QComboBox()
        self.priority_combo.setFont(self.vazir_font)
        self.priority_combo.addItems(["کم", "متوسط", "زیاد"])
        priority_layout.addWidget(self.priority_combo)
        form_layout.addLayout(priority_layout)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("اضافه کردن")
        self.add_btn.setFont(self.vazir_font)
        self.add_btn.clicked.connect(self.add_todo)
        buttons_layout.addWidget(self.add_btn)
        
        left_layout.addLayout(form_layout)
        layout.addWidget(left_panel)
        
        # تنظیم راست به چپ
        main_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
    def apply_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 233, 233))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        self.setPalette(palette)
        
    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        self.setPalette(palette)
        
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.calendar.is_dark_mode = self.is_dark_mode
        if self.is_dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
            
    def load_todos(self, date):
        self.todo_list.clear()
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        
        # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
        jdate = self.calendar.selectedDate()
        date_str = f"{jdate.year}-{jdate.month:02d}-{jdate.day:02d}"
        
        c.execute('SELECT * FROM todos WHERE date = ?', (date_str,))
        todos = c.fetchall()
        conn.close()
        
        for todo in todos:
            # ایجاد ویجت برای هر تسک
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # ایجاد چک‌باکس
            checkbox = QCheckBox()
            checkbox.setFont(self.vazir_font)
            # تنظیم وضعیت چک‌باکس بر اساس مقدار completed در دیتابیس
            checkbox.setChecked(todo[5] == 1)  # todo[5] مقدار completed است
            checkbox.stateChanged.connect(lambda state, todo_id=todo[0]: self.toggle_todo_status(todo_id, state))
            
            # ایجاد لیبل برای متن تسک
            label = QLabel(todo[2])
            label.setFont(self.vazir_font)
            label.mousePressEvent = lambda event, desc=todo[3]: self.show_description(desc)
            
            # ایجاد آیکون‌های ستاره برای اولویت
            stars_layout = QHBoxLayout()
            stars_layout.setSpacing(0)
            priority = todo[4]
            for i in range(3):
                star_label = QLabel()
                if priority == 2:  # اولویت زیاد
                    star_label.setText("★")
                elif priority == 1:  # اولویت متوسط
                    star_label.setText("★" if i < 2 else "☆")
                elif priority == 0:  # اولویت کم
                    star_label.setText("★" if i < 1 else "☆")
                else:  # بدون اولویت
                    star_label.setText("☆")
                star_label.setFont(QFont("Arial", 12))
                stars_layout.addWidget(star_label)
            
            # اضافه کردن چک‌باکس، لیبل و ستاره‌ها به ویجت
            layout.addWidget(checkbox)
            layout.addWidget(label)
            layout.addStretch()
            layout.addLayout(stars_layout)
            
            # ایجاد آیتم لیست و تنظیم ویجت
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.todo_list.addItem(item)
            self.todo_list.setItemWidget(item, widget)
            
    def show_description(self, description):
        if not description:
            return
            
        # ایجاد پنجره نمایش توضیحات
        dialog = QDialog(self)
        dialog.setWindowTitle("توضیحات تسک")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)
        
        # ایجاد لیبل برای نمایش توضیحات
        desc_label = QTextEdit(description)
        desc_label.setReadOnly(True)
        desc_label.setFont(self.vazir_font)
        
        # ایجاد دکمه بستن
        close_btn = QPushButton("بستن")
        close_btn.setFont(self.vazir_font)
        close_btn.clicked.connect(dialog.close)
        
        # تنظیم لایه‌بندی
        layout = QVBoxLayout(dialog)
        layout.addWidget(desc_label)
        layout.addWidget(close_btn)
        
        # نمایش پنجره
        dialog.exec()
        
    def toggle_todo_status(self, todo_id, state):
        try:
            conn = sqlite3.connect('todos.db')
            c = conn.cursor()
            # تبدیل state به مقدار صحیح برای ذخیره در دیتابیس
            completed = 1 if state == Qt.CheckState.Checked.value else 0
            c.execute('UPDATE todos SET completed = ? WHERE id = ?', (completed, todo_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطا در ذخیره وضعیت تسک: {e}")
        
    def add_todo(self):
        jdate = self.calendar.selectedDate()
        date_str = f"{jdate.year}-{jdate.month:02d}-{jdate.day:02d}"
        title = self.title_input.text()
        description = self.desc_input.toPlainText()
        priority = self.priority_combo.currentIndex()
        
        if not title:
            QMessageBox.warning(self, "خطا", "لطفا عنوان را وارد کنید")
            return
            
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        c.execute('INSERT INTO todos (date, title, description, priority) VALUES (?, ?, ?, ?)',
                 (date_str, title, description, priority))
        conn.commit()
        conn.close()
        
        self.title_input.clear()
        self.desc_input.clear()
        self.load_todos(self.calendar.selectedDate())
        
    def delete_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            return
            
        # دریافت ویجت تسک انتخاب شده
        widget = self.todo_list.itemWidget(current_item)
        if not widget:
            return
            
        # دریافت عنوان تسک از لیبل
        title_label = widget.findChild(QLabel)
        if not title_label:
            return
            
        title = title_label.text()
        
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        
        jdate = self.calendar.selectedDate()
        date_str = f"{jdate.year}-{jdate.month:02d}-{jdate.day:02d}"
        
        c.execute('DELETE FROM todos WHERE title = ? AND date = ?',
                 (title, date_str))
        conn.commit()
        conn.close()
        
        self.load_todos(self.calendar.selectedDate())

    def delete_all_todos(self):
        reply = QMessageBox.question(self, 'تایید حذف', 
                                   'آیا از حذف تمام تسک‌های این روز اطمینان دارید؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect('todos.db')
            c = conn.cursor()
            
            jdate = self.calendar.selectedDate()
            date_str = f"{jdate.year}-{jdate.month:02d}-{jdate.day:02d}"
            
            c.execute('DELETE FROM todos WHERE date = ?', (date_str,))
            conn.commit()
            conn.close()
            
            self.load_todos(self.calendar.selectedDate())

    def edit_todo(self):
        current_item = self.todo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "خطا", "لطفا یک تسک را برای ویرایش انتخاب کنید")
            return
            
        # دریافت ویجت تسک انتخاب شده
        widget = self.todo_list.itemWidget(current_item)
        if not widget:
            return
            
        # دریافت عنوان تسک از لیبل
        title_label = widget.findChild(QLabel)
        if not title_label:
            return
            
        title = title_label.text()
        
        # دریافت اطلاعات تسک از دیتابیس
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        
        jdate = self.calendar.selectedDate()
        date_str = f"{jdate.year}-{jdate.month:02d}-{jdate.day:02d}"
        
        c.execute('SELECT * FROM todos WHERE title = ? AND date = ?', (title, date_str))
        todo = c.fetchone()
        conn.close()
        
        if not todo:
            return
            
        # ایجاد پنجره ویرایش
        dialog = QDialog(self)
        dialog.setWindowTitle("ویرایش تسک")
        dialog.setMinimumWidth(400)
        
        # ایجاد فرم ویرایش
        form_layout = QVBoxLayout(dialog)
        
        # عنوان
        title_layout = QHBoxLayout()
        title_label = QLabel("عنوان:")
        title_label.setFont(self.vazir_font)
        title_layout.addWidget(title_label)
        title_input = QLineEdit(todo[2])
        title_input.setFont(self.vazir_font)
        title_layout.addWidget(title_input)
        form_layout.addLayout(title_layout)
        
        # توضیحات
        desc_layout = QVBoxLayout()
        desc_label = QLabel("توضیحات:")
        desc_label.setFont(self.vazir_font)
        desc_layout.addWidget(desc_label)
        desc_input = QTextEdit(todo[3])
        desc_input.setFont(self.vazir_font)
        desc_layout.addWidget(desc_input)
        form_layout.addLayout(desc_layout)
        
        # اولویت
        priority_layout = QHBoxLayout()
        priority_label = QLabel("اولویت:")
        priority_label.setFont(self.vazir_font)
        priority_layout.addWidget(priority_label)
        priority_combo = QComboBox()
        priority_combo.setFont(self.vazir_font)
        priority_combo.addItems(["کم", "متوسط", "زیاد"])
        priority_combo.setCurrentIndex(todo[4])
        priority_layout.addWidget(priority_combo)
        form_layout.addLayout(priority_layout)
        
        # دکمه‌های ذخیره و انصراف
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("ذخیره")
        save_button.setFont(self.vazir_font)
        cancel_button = QPushButton("انصراف")
        cancel_button.setFont(self.vazir_font)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        form_layout.addLayout(buttons_layout)
        
        # اتصال دکمه‌ها
        save_button.clicked.connect(lambda: self.save_edited_todo(dialog, todo[0], title_input.text(), 
                                                                desc_input.toPlainText(), 
                                                                priority_combo.currentIndex()))
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec()
        
    def save_edited_todo(self, dialog, todo_id, title, description, priority):
        if not title:
            QMessageBox.warning(self, "خطا", "لطفا عنوان را وارد کنید")
            return
            
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        c.execute('UPDATE todos SET title = ?, description = ?, priority = ? WHERE id = ?',
                 (title, description, priority, todo_id))
        conn.commit()
        conn.close()
        
        dialog.accept()
        self.load_todos(self.calendar.selectedDate())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TodoApp()
    window.show()
    sys.exit(app.exec()) 
