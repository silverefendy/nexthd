(function () {
"use strict";

var main = document.getElementById("nx-main");
var content = document.getElementById("nx-content");
if (!main || !content) return;

// Get ticket ID from query string
var urlParams = new URLSearchParams(window.location.search);
var ticketId = urlParams.get("id");

if (!ticketId) {
NX.ui.empty(content, "ID tiket tidak ditemukan");
return;
}

function loadTicket() {
NX.ui.setLoading(content, true);

NX.api.get("nexthd.next_helpdesk.api.portal.get_ticket", { name: ticketId }).then(function (ticket) {
content.textContent = "";
renderTicket(ticket);
}).catch(function (err) {
content.textContent = "";
if (err.message === "Anda tidak memiliki izin untuk aksi ini" || err.message.includes("tidak ditemukan")) {
NX.ui.empty(content, err.message);
} else {
NX.ui.empty(content, "Gagal memuat: " + err.message);
}
var backBtn = document.createElement("button");
backBtn.className = "nx-btn";
backBtn.textContent = "Kembali ke antrian";
backBtn.addEventListener("click", function () {
window.location.href = "/nexthd/kerja";
});
content.appendChild(backBtn);
});
}

function renderTicket(ticket) {
var wrap = document.createElement("div");
wrap.className = "nx-wrap";

// Header
var header = document.createElement("div");
header.className = "nx-page-head";
var h1 = document.createElement("h1");
h1.textContent = ticket.subject;
header.appendChild(h1);

var meta = document.createElement("div");
meta.className = "nx-card";
meta.style.marginBottom = "1rem";

var idSpan = document.createElement("span");
idSpan.textContent = ticket.name;
meta.appendChild(document.createTextNode("ID: "));
meta.appendChild(idSpan);
meta.appendChild(document.createTextNode(" | "));

var statusBadge = NX.ui.badge(ticket.status, getStatusColor(ticket.status));
meta.appendChild(statusBadge);
meta.appendChild(document.createTextNode(" "));

var priorityBadge = NX.ui.badge(ticket.priority, getPriorityColor(ticket.priority));
meta.appendChild(priorityBadge);
meta.appendChild(document.createTextNode(" "));

var typeBadge = NX.ui.badge(ticket.ticket_type, ticket.ticket_type === "Insiden" ? "red" : "blue");
meta.appendChild(typeBadge);

header.appendChild(meta);
wrap.appendChild(header);

// Info block
var infoCard = document.createElement("div");
infoCard.className = "nx-card";
infoCard.innerHTML = "<h3>Informasi</h3>";

var infoTable = document.createElement("table");
infoTable.className = "nx-table";

var infoFields = [
{ label: "Pelapor", value: ticket.requested_by },
{ label: "Ditugaskan ke", value: ticket.assigned_to || "-" },
{ label: "Tim", value: ticket.team || "-" },
{ label: "Kategori", value: ticket.category || "-" },
{ label: "Impact", value: ticket.impact || "-" },
{ label: "Urgency", value: ticket.urgency || "-" },
{ label: "Aset Terkait", value: ticket.affected_asset || "-" },
{ label: "Problem Terkait", value: ticket.related_problem || "-" }
];

infoFields.forEach(function (field) {
var tr = document.createElement("tr");
var th = document.createElement("th");
th.textContent = field.label;
var td = document.createElement("td");
td.textContent = field.value;
tr.appendChild(th);
tr.appendChild(td);
infoTable.appendChild(tr);
});

infoCard.appendChild(infoTable);
wrap.appendChild(infoCard);

// SLA block
var slaCard = document.createElement("div");
slaCard.className = "nx-card";
slaCard.innerHTML = "<h3>SLA</h3>";

var slaTable = document.createElement("table");
slaTable.className = "nx-table";

var slaFields = [
{ label: "SLA Respon", value: ticket.sla_response_by ? NX.ui.fmtDateTime(ticket.sla_response_by) : "-" },
{ label: "SLA Resolusi", value: ticket.sla_resolution_by ? NX.ui.fmtDateTime(ticket.sla_resolution_by) : "-" },
{ label: "Direspon Pada", value: ticket.responded_on ? NX.ui.fmtDateTime(ticket.responded_on) : "-" },
{ label: "Selesai Pada", value: ticket.resolved_on ? NX.ui.fmtDateTime(ticket.resolved_on) : "-" },
{ label: "Ditutup Pada", value: ticket.closed_on ? NX.ui.fmtDateTime(ticket.closed_on) : "-" }
];

slaFields.forEach(function (field) {
var tr = document.createElement("tr");
var th = document.createElement("th");
th.textContent = field.label;
var td = document.createElement("td");
td.textContent = field.value;
tr.appendChild(th);
tr.appendChild(td);
slaTable.appendChild(tr);
});

slaCard.appendChild(slaTable);
wrap.appendChild(slaCard);

// Description
if (ticket.description) {
var descCard = document.createElement("div");
descCard.className = "nx-card";
descCard.innerHTML = "<h3>Deskripsi</h3>";
var descDiv = document.createElement("div");
descDiv.id = "nx-description";
// Safe: description already sanitized by server
descDiv.innerHTML = ticket.description;
descCard.appendChild(descDiv);
wrap.appendChild(descCard);
}

// Worklog
if (ticket.worklog && ticket.worklog.length > 0) {
var worklogCard = document.createElement("div");
worklogCard.className = "nx-card";
worklogCard.innerHTML = "<h3>Riwayat Progress</h3>";

var worklogTable = document.createElement("table");
worklogTable.className = "nx-table";
var worklogThead = document.createElement("thead");
var worklogHeaderRow = document.createElement("tr");
["Waktu", "Teknisi", "Aktivitas", "Hasil", "Durasi (menit)"].forEach(function (col) {
var th = document.createElement("th");
th.textContent = col;
worklogHeaderRow.appendChild(th);
});
worklogThead.appendChild(worklogHeaderRow);
worklogTable.appendChild(worklogThead);

var worklogTbody = document.createElement("tbody");
ticket.worklog.forEach(function (row) {
var tr = document.createElement("tr");
[row.waktu, row.teknisi, row.aktivitas, row.hasil, row.durasi_menit].forEach(function (cell) {
var td = document.createElement("td");
td.textContent = cell || "-";
tr.appendChild(td);
});
worklogTbody.appendChild(tr);
});
worklogTable.appendChild(worklogTbody);
worklogCard.appendChild(worklogTable);
wrap.appendChild(worklogCard);
}

// Waiting Log
if (ticket.waiting_log && ticket.waiting_log.length > 0) {
var waitingCard = document.createElement("div");
waitingCard.className = "nx-card";
waitingCard.innerHTML = "<h3>Riwayat Menunggu User</h3>";

var waitingTable = document.createElement("table");
waitingTable.className = "nx-table";
var waitingThead = document.createElement("thead");
var waitingHeaderRow = document.createElement("tr");
["Ditanyakan Pada", "Ditanyakan Oleh", "Alasan", "Dibalas Pada", "Balasan"].forEach(function (col) {
var th = document.createElement("th");
th.textContent = col;
waitingHeaderRow.appendChild(th);
});
waitingThead.appendChild(waitingHeaderRow);
waitingTable.appendChild(waitingThead);

var waitingTbody = document.createElement("tbody");
ticket.waiting_log.forEach(function (row) {
var tr = document.createElement("tr");
[row.asked_on, row.asked_by, row.question, row.replied_on, row.reply].forEach(function (cell) {
var td = document.createElement("td");
td.textContent = cell || "-";
tr.appendChild(td);
});
waitingTbody.appendChild(tr);
});
waitingTable.appendChild(waitingTbody);
waitingCard.appendChild(waitingTable);
wrap.appendChild(waitingCard);
}

// Back button
var backBtn = document.createElement("button");
backBtn.className = "nx-btn";
backBtn.textContent = "Kembali ke antrian";
backBtn.addEventListener("click", function () {
window.location.href = "/nexthd/kerja";
});
wrap.appendChild(backBtn);

content.appendChild(wrap);
}

function getStatusColor(status) {
switch (status) {
case "Baru": return "blue";
case "Sedang Dikerjakan": return "orange";
case "Menunggu User": return "yellow";
case "Selesai": return "green";
case "Ditutup": return "grey";
default: return "";
}
}

function getPriorityColor(priority) {
switch (priority) {
case "Kritis": return "red";
case "Tinggi": return "orange";
case "Sedang": return "yellow";
case "Rendah": return "grey";
default: return "";
}
}

// Load session first
NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info").then(function (session) {
NX.ui.renderNav(session);
loadTicket();
}).catch(function (err) {
content.textContent = "";
NX.ui.empty(content, "Gagal memuat: " + err.message);
});
})();
