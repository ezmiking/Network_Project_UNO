import psycopg2

# اطلاعات اتصال به پایگاه داده
try:
    connection = psycopg2.connect(
        dbname="your_database_name",     # نام پایگاه داده
        user="your_username",            # نام کاربری
        password="2325",        # رمز عبور
        host="localhost",                # آدرس سرور
        port="5432"                      # پورت پیش‌فرض PostgreSQL
    )

    # ایجاد یک cursor برای اجرای کوئری‌ها
    cursor = connection.cursor()

    # تست اتصال با نمایش نسخه PostgreSQL
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connected to: {db_version[0]}")

except Exception as error:
    print(f"Error connecting to PostgreSQL: {error}")

finally:
    # بستن اتصال
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed.")
