const SUBJECTS = ["python", "mathematics", "statistics", "data_science", "database"];
let students = [];
let subjectChart = null;
let distributionChart = null;

const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));

function showToast(message) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function setView(view) {
  document.querySelectorAll(".view").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(el => el.classList.toggle("active", el.dataset.view === view));
  $(`${view}View`).classList.add("active");
  const label = view.charAt(0).toUpperCase() + view.slice(1);
  $("pageName").textContent = label;
  $("headingTitle").textContent = view === "overview" ? "Student performance" : view === "students" ? "Student directory" : "Academic analytics";
  $("sidebar").classList.remove("open");
  if (view === "students") renderStudents();
  if (view === "analytics") loadAnalytics();
}

function studentStatus(student) {
  return SUBJECTS.every(subject => student.marks[subject] >= 50);
}

function average(student) {
  return SUBJECTS.reduce((sum, subject) => sum + Number(student.marks[subject]), 0) / SUBJECTS.length;
}

function initials(name) {
  return name.split(/\s+/).slice(0, 2).map(part => part[0] || "").join("").toUpperCase();
}

async function loadStudents() {
  students = await api("/api/students");
  renderStudents();
}

function renderStudents(filter = "") {
  const filtered = students.filter(student =>
    `${student.name} ${student.roll_no}`.toLowerCase().includes(filter.toLowerCase())
  );
  $("studentsBody").innerHTML = filtered.map(student => {
    const avg = average(student);
    const pass = studentStatus(student);
    return `<tr>
      <td><div class="student-cell"><span class="student-mini">${escapeHtml(initials(student.name))}</span>${escapeHtml(student.name)}</div></td>
      <td>${escapeHtml(student.roll_no)}</td>
      ${SUBJECTS.map(subject => `<td>${student.marks[subject]}</td>`).join("")}
      <td><strong>${avg.toFixed(1)}</strong></td>
      <td><span class="status ${pass ? "pass" : "fail"}">${pass ? "Pass" : "Improve"}</span></td>
      <td><button class="action-btn" onclick="editStudent(${student.id})">Edit</button><button class="action-btn delete" onclick="removeStudent(${student.id})">Delete</button></td>
    </tr>`;
  }).join("");
  $("studentCount").textContent = `Showing ${filtered.length} of ${students.length} students`;
}

async function loadDashboard() {
  const data = await api("/api/analytics");
  const s = data.summary;
  $("totalStudents").textContent = s.total_students;
  $("classAverage").textContent = `${s.class_average.toFixed(1)}%`;
  $("passRate").textContent = `${s.pass_rate}%`;
  $("highestMark").textContent = s.highest_mark;
  $("medianValue").textContent = s.median;
  $("stdValue").textContent = s.standard_deviation;
  $("passedCount").textContent = s.passed_students;
  $("failedCount").textContent = s.failed_students;
  $("analyticsMedian").textContent = s.median;
  $("analyticsStd").textContent = s.standard_deviation;
  $("analyticsPassed").textContent = s.passed_students;
  $("analyticsFailed").textContent = s.failed_students;

  $("topStudentsBody").innerHTML = data.top_students.slice(0, 5).map((student, index) => `
    <tr><td><div class="student-cell"><span class="student-mini">${index + 1}</span>${escapeHtml(student.name)}</div></td>
    <td>${escapeHtml(student.roll_no)}</td><td><strong>${student.average.toFixed(1)}%</strong></td>
    <td><span class="status ${student.status === "Pass" ? "pass" : "fail"}">${student.status}</span></td></tr>
  `).join("");

  drawCharts(data);
  $("subjectStatsBody").innerHTML = data.subjects.map(subject => `
    <tr><td><strong>${escapeHtml(subject.name)}</strong></td><td>${subject.average.toFixed(1)}</td><td>${subject.highest}</td><td>${subject.lowest}</td></tr>
  `).join("");
}

function drawCharts(data) {
  if (typeof Chart === "undefined") return;
  const subjectCanvas = $("subjectChart");
  const distributionCanvas = $("distributionChart");
  if (subjectChart) subjectChart.destroy();
  if (distributionChart) distributionChart.destroy();

  subjectChart = new Chart(subjectCanvas, {
    type: "bar",
    data: {
      labels: data.subjects.map(item => item.name),
      datasets: [{
        label: "Average marks",
        data: data.subjects.map(item => item.average),
        backgroundColor: ["#3478f6", "#6b8ff0", "#22b8cf", "#7c70dc", "#4c9f89"],
        borderRadius: 6,
        maxBarThickness: 34
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100, grid: { color: "#eef1f6" }, ticks: { font: { size: 9 } } },
        x: { grid: { display: false }, ticks: { font: { size: 9 } } }
      }
    }
  });

  distributionChart = new Chart(distributionCanvas, {
    type: "doughnut",
    data: {
      labels: data.distribution.labels,
      datasets: [{
        data: data.distribution.values,
        backgroundColor: ["#e58a55", "#e9b65c", "#8da8e9", "#547fe0", "#24a9b8", "#4b9c82"],
        borderWidth: 0,
        hoverOffset: 5
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: "68%",
      plugins: { legend: { position: "bottom", labels: { boxWidth: 9, boxHeight: 9, padding: 12, font: { size: 9 } } } }
    }
  });
}

async function loadAnalytics() {
  await loadDashboard();
}

function openModal(student = null) {
  $("studentForm").reset();
  $("formError").textContent = "";
  $("studentId").value = student ? student.id : "";
  $("modalTitle").textContent = student ? "Edit student" : "Add student";
  $("studentName").value = student ? student.name : "";
  $("rollNo").value = student ? student.roll_no : "";
  document.querySelectorAll(".mark-input").forEach(input => {
    input.value = student ? student.marks[input.dataset.subject] : 0;
  });
  $("studentModal").classList.add("open");
  $("studentModal").setAttribute("aria-hidden", "false");
}

function closeModal() {
  $("studentModal").classList.remove("open");
  $("studentModal").setAttribute("aria-hidden", "true");
}

window.editStudent = (id) => {
  const student = students.find(item => item.id === id);
  if (student) openModal(student);
};

window.removeStudent = async (id) => {
  const student = students.find(item => item.id === id);
  if (!student || !confirm(`Delete ${student.name}? This cannot be undone.`)) return;
  try {
    await api(`/api/students/${id}`, { method: "DELETE" });
    await refreshAll();
    showToast("Student deleted.");
  } catch (error) {
    showToast(error.message);
  }
};

async function refreshAll() {
  await loadStudents();
  await loadDashboard();
}

$("studentForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = $("studentId").value;
  const payload = {
    name: $("studentName").value.trim(),
    roll_no: $("rollNo").value.trim(),
    marks: {}
  };
  document.querySelectorAll(".mark-input").forEach(input => {
    payload.marks[input.dataset.subject] = Number(input.value);
  });

  try {
    await api(id ? `/api/students/${id}` : "/api/students", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(payload)
    });
    closeModal();
    await refreshAll();
    showToast(id ? "Student updated successfully." : "Student added successfully.");
  } catch (error) {
    $("formError").textContent = error.message;
  }
});

document.querySelectorAll(".nav-link").forEach(button =>
  button.addEventListener("click", () => setView(button.dataset.view))
);
document.querySelectorAll("[data-goto]").forEach(button =>
  button.addEventListener("click", () => setView(button.dataset.goto))
);
$("addStudent").addEventListener("click", () => openModal());
$("addStudentTop").addEventListener("click", () => openModal());
$("closeModal").addEventListener("click", closeModal);
$("cancelModal").addEventListener("click", closeModal);
$("studentModal").addEventListener("click", event => {
  if (event.target === $("studentModal")) closeModal();
});
$("studentSearch").addEventListener("input", event => renderStudents(event.target.value));
$("mobileMenu").addEventListener("click", () => $("sidebar").classList.toggle("open"));

refreshAll().catch(error => showToast(error.message));
