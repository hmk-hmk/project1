import tkinter as tk
from PIL import Image, ImageTk
import os
import logging

# تنظیمات لاگ
logging.basicConfig(filename="G:/tachra_project/back6/main_log.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")
logging.info("شروع اسکریپت main.py")

# مسیر بک‌گراند
BG_PATH = "G:/tachra_project/back6/backgerand"
DEFAULT_BG = os.path.join(BG_PATH, "t1.jpg")

# چک کردن فایل
if not os.path.exists(DEFAULT_BG):
    logging.error(f"فایل بک‌گراند {DEFAULT_BG} پیدا نشد. لطفاً مسیر یا اسم فایل رو چک کنید!")

# پنجره اصلی
root = tk.Tk()
logging.info("پنجره اصلی ساخته شد")
root.title("تست بک‌گراند")
root.attributes('-fullscreen', True)
root.configure(bg="#2F2F2F")

# Canvas برای بک‌گراند
canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), highlightthickness=0)
canvas.place(relx=0.5, rely=0.5, anchor="center")

try:
    img = Image.open(DEFAULT_BG)
    img = img.resize((2000, 1200), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(img)
    canvas.create_image(root.winfo_screenwidth()//2, root.winfo_screenheight()//2, image=bg_image)
    canvas.image = bg_image  # مرجع رو توی Canvas نگه می‌دارم
    logging.info("بک‌گراند با موفقیت لود شد")
except Exception as e:
    logging.error(f"خطا در لود بک‌گراند: {e}")
    canvas.configure(bg="#1E88E5")

# دکمه خروج برای تست
exit_btn = tk.Button(root, text="خروج", font=("Arial", 12, "bold"), 
                     bg="#E53935", fg="white", width=5, height=1, relief="raised", bd=4, 
                     command=root.quit)
exit_btn.place(x=root.winfo_screenwidth()-80, y=210, anchor="ne")

# حلقه اصلی
logging.info("شروع حلقه اصلی")
root.mainloop()
logging.info("پایان اسکریپت main.py")