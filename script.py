from werkzeug.security import generate_password_hash

    
password = "admin123"  # غيرها لكلمة المرور اللي عايزها
hashed = generate_password_hash(password, method="pbkdf2:sha256", salt_length=12)

print(hashed)