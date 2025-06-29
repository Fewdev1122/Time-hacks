document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert('กรุณากรอกอีเมลและรหัสผ่าน');
        return;
    }

      // คุณสามารถเพิ่มการตรวจสอบอีเมลและรหัสผ่านที่ถูกต้องที่นี่
      // หรือส่งข้อมูลไปตรวจสอบใน Backend

    alert('เข้าสู่ระบบสำเร็จ! 🎉');
      // ส่งฟอร์มไป backend
      this.submit();
    });