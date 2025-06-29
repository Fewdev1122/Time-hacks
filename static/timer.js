let workInterval, breakInterval;
let workSeconds = 1500;
let breakSeconds = 300;
let isRunning = false;
let isWorking = true;
let taskTitle = "";

function formatTime(s) {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
}

function updateDisplay() {
    document.getElementById('work-timer').textContent = formatTime(workSeconds);
    document.getElementById('break-timer').textContent = formatTime(breakSeconds);
}

function startWork() {
    if (isRunning && isWorking) return;

    if (!isWorking && breakInterval) {
        clearInterval(breakInterval);
        breakInterval = null;
        isWorking = true;
    }

    const inputTitle = document.getElementById('task-title').value.trim();
    if (inputTitle !== "") taskTitle = inputTitle;

    document.getElementById('current-task').textContent = "⏱️ กำลังทำ: " + (taskTitle || "ไม่ระบุ");

    const w = parseInt(document.getElementById('work-time').value) || 25;
    const b = parseInt(document.getElementById('break-time').value) || 5;

    if (!isRunning) {
        workSeconds = workSeconds > 0 ? workSeconds : w * 60;
        breakSeconds = b * 60;
    }

    updateDisplay();
    isRunning = true;

    workInterval = setInterval(() => {
        workSeconds--;
        updateDisplay();

        if (workSeconds <= 0) {
            clearInterval(workInterval);
            isRunning = false;

            console.log(`🧠 เสร็จงาน "${taskTitle}" ใช้เวลา ${w} นาที`);

            // 🔽 ส่งข้อมูลไปยัง Flask
            fetch("/log_activity", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    skill: taskTitle,
                    minutes: w
                })
            })
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    console.log("✅ บันทึกสำเร็จ:", data);
                })
                .catch(error => {
                    console.error("❌ เกิดข้อผิดพลาดขณะส่งข้อมูล:", error);
                });

            startBreak();
        }
    }, 1000);
}


function startBreak() {
    isWorking = false;
    isRunning = true;

    breakInterval = setInterval(() => {
        breakSeconds--;
        updateDisplay();

        if (breakSeconds <= 0) {
            clearInterval(breakInterval);
            isRunning = false;
        }
    }, 1000);
}

function pauseToBreak() {
    if (!isRunning || !isWorking) return;

    clearInterval(workInterval);
    isRunning = false;
    startBreak();
}

function resetAll() {
    clearInterval(workInterval);
    clearInterval(breakInterval);
    workInterval = null;
    breakInterval = null;

    const w = parseInt(document.getElementById('work-time').value) || 25;
    const b = parseInt(document.getElementById('break-time').value) || 5;

    workSeconds = w * 60;
    breakSeconds = b * 60;

    isRunning = false;
    isWorking = true;
    taskTitle = "";
    document.getElementById('current-task').textContent = "";
    updateDisplay();
}

updateDisplay();

