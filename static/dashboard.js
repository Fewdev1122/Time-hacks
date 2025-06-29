
let focusMode = false;

function toggleFocusMode() {

  focusMode = !focusMode;
  const messages = document.querySelectorAll('.flash-message');
  const toggleBtn = document.getElementById('focusToggleBtn');

  if (focusMode) {
    alert("โหมดโฟกัสเปิดอยู่: กรุณาปิดเสียงจาก Facebook หรือแท็บอื่นเพื่อความเงียบสูงสุด 🧘‍♀️");
    messages.forEach(msg => msg.style.display = 'none');
    toggleBtn.textContent = 'Focus Off';
  }
  else {
    messages.forEach(msg => msg.style.display = 'block');
    toggleBtn.textContent = 'Mode Focus';
  }
}


let currentSound = '';
let isPlaying = false;

function playMusic(type) {
  const audio = document.getElementById('bg-music');

  // เสียงใหม่หรือกดซ้ำเพื่อหยุด
  if (currentSound === type && isPlaying) {
    audio.pause();
    audio.currentTime = 0;
    isPlaying = false;
    return;
  }

  // ตั้งค่า source
  let soundSrc = '';
  if (type === 'brown_noise') soundSrc = '/static/sounds/brown_noise.mp3';
  else if (type === 'rain') soundSrc = '/static/sounds/rain.mp3';
  else if (type === 'lofi') soundSrc = '/static/sounds/lofi.mp3';

  // โหลดใหม่และเล่น
  audio.src = soundSrc;
  audio.loop = true;
  audio.load();
  audio.play().then(() => {
    currentSound = type;
    isPlaying = true;
  }).catch(err => {
    console.error("Error playing audio:", err);
  });
}

function logActivity() {
  const skill = document.getElementById('task-title').value;
  const minutes = parseInt(document.getElementById('work-time').value);

  fetch('/log_activity', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ skill, minutes })
  });
}

const toggleBtn = document.getElementById("toggle-todo");
const closeBtn = document.getElementById("close-todo");
const todoPanel = document.querySelector(".to-do-list");

toggleBtn.addEventListener("click", () => {
  todoPanel.classList.add("show");
  toggleBtn.classList.add("hidden"); // ซ่อนปุ่มเมื่อเปิด
});

closeBtn.addEventListener("click", () => {
  todoPanel.classList.remove("show");
  toggleBtn.classList.remove("hidden"); // แสดงปุ่มเมื่อปิด
});


let input = document.getElementById('user');
let ok = document.getElementById('ok');
let ul = document.querySelector('.data'); // แก้ตรงนี้
let color = document.getElementById('color_value');
let body = document.querySelector('body');

function change_color() {
    body.style.backgroundColor = color.value;
}

function check_len() {
    return input.value.trim().length;
}

function createTodoItem(text, id, isDone = false) {
    let li = document.createElement('li');
    li.textContent = text;

    if (isDone) {
        li.classList.add("done");
    }

    // ✅ ปุ่มลบ
    let dBtn = document.createElement('button');
    dBtn.textContent = 'X';
    dBtn.className = "delete-btn";
    dBtn.addEventListener("click", () => {
        fetch(`/delete_todo/${id}`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'deleted') {
                    li.remove();
                }
            });
    });

    // ✅ toggle เสร็จ/ยังไม่เสร็จ
    li.addEventListener("click", () => {
        li.classList.toggle("done");
        const done = li.classList.contains("done");

        fetch(`/update_todo/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_done: done })
        });
    });

    li.appendChild(dBtn);
    ul.appendChild(li);
}

function after_click() {
    if (check_len() > 0) {
        const content = input.value.trim();
        fetch('/add_todo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ บันทึกสำเร็จ:", data);
            createTodoItem(content, data.id); // ✅ ใช้ id
            input.value = "";
        })
        .catch(error => {
            console.error("❌ เกิดข้อผิดพลาด:", error);
        });
    }
}

window.addEventListener("DOMContentLoaded", loadTodos);

function loadTodos() {
    fetch("/get_todos")
        .then(res => res.json())
        .then(todos => {
            todos.forEach(todo => {
                createTodoItem(todo.content, todo.id, todo.is_done);
            });
        })
        .catch(err => console.error("❌ โหลด ToDo ไม่สำเร็จ:", err));
}





function after_key(event) {
    if (event.key === "Enter") {
        after_click();
    }
}

ok.addEventListener("click", after_click);
input.addEventListener("keypress", after_key);




const encouragements = [
  "วันนี้ก็สู้ ๆ นะ ✨",
  "ภารกิจรอคุณอยู่ 💪",
  "ทำได้แน่นอน!",
  "อย่าลืมดู ToDo ของคุณล่ะ 🚀",
  "แค่ลงมือทำ ก้าวแรกก็สำเร็จแล้ว!"
];

function showToast(message) {
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toast-message");
  toastMsg.textContent = message;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 4000);
}

function fetchUndoneTodos() {
  fetch('/get_todos')
    .then(res => res.json())
    .then(todos => {
      if (Array.isArray(todos) && todos.length > 0) {
        const todo = todos[Math.floor(Math.random() * todos.length)];
        const encouragement = encouragements[Math.floor(Math.random() * encouragements.length)];
        const message = `📌 "${todo.content}"\n${encouragement}`;
        showToast(message);
      }
    })
    .catch(err => console.error("ไม่สามารถโหลด ToDo:", err));
}

// เรียกเมื่อโหลดเสร็จ และทุก 1 นาที
document.addEventListener("DOMContentLoaded", () => {
  fetchUndoneTodos(); // แสดงครั้งแรก
  setInterval(fetchUndoneTodos, 60000); // แสดงทุก 1 นาที
});


// hamberger menu
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('menu-toggle');
    const menu = document.getElementById('menu-list');

    toggle.addEventListener('click', () => {
        menu.classList.toggle('show');
    });
});
