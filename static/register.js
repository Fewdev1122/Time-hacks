document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault(); // ป้องกันการส่งฟอร์มแบบปกติ

    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const gender = document.getElementById('gender').value;
    const age = parseInt(document.getElementById('age').value);

    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;

    if (!username || !email || !password || !confirmPassword || !gender || isNaN(age)) {
        alert('กรุณากรอกข้อมูลให้ครบทุกช่อง');
        return;
    }

    if (!emailPattern.test(email)) {
        alert('รูปแบบอีเมลไม่ถูกต้อง');
        return;
    }

    if (password.length < 6) {
        alert('รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร');
        return;
    }

    if (password !== confirmPassword) {
        alert('รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน');
        return;
    }

    if (age < 10 || age > 100) {
        alert('อายุต้องอยู่ระหว่าง 10 ถึง 100 ปี');
        return;
    }

      // ✅ ผ่านการตรวจสอบทั้งหมด
    
    this.submit(); // ส่งฟอร์มต่อไปยัง backend (ถ้ามี action="/register")
});