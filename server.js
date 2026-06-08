// 한국 시간대 설정 (KST, UTC+9)
process.env.TZ = 'Asia/Seoul';

// KST 날짜/시간 헬퍼
function kstNow() {
  const d = new Date(Date.now() + 9 * 60 * 60 * 1000);
  return d;
}
function kstDate() {
  const d = kstNow();
  return d.getUTCFullYear() + '-' +
    String(d.getUTCMonth() + 1).padStart(2, '0') + '-' +
    String(d.getUTCDate()).padStart(2, '0');
}
function kstMonth() { return kstDate().slice(0, 7); }
function kstTime() {
  const d = kstNow();
  return String(d.getUTCHours()).padStart(2, '0') + ':' +
    String(d.getUTCMinutes()).padStart(2, '0');
}

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const initSqlJs = require('sql.js');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// 캐시 방지 헤더 (HTML, JS, CSS)
app.use((req, res, next) => {
  if (req.path.endsWith('.html') || req.path.endsWith('.js') || req.path.endsWith('.css') || req.path === '/') {
    res.set('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
  }
  next();
});

// Static files
app.use(express.static(__dirname, { maxAge: 0, etag: false }));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, path.join(__dirname, 'uploads')),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname) || '.jpg';
    cb(null, `${Date.now()}_${uuidv4().slice(0, 8)}${ext}`);
  }
});
const upload = multer({ storage, limits: { fileSize: 20 * 1024 * 1024 } });

// Database
const DB_PATH = path.join(__dirname, 'data.db');
let db;

async function initDB() {
  const SQL = await initSqlJs();
  if (fs.existsSync(DB_PATH)) {
    const buf = fs.readFileSync(DB_PATH);
    db = new SQL.Database(buf);
  } else {
    db = new SQL.Database();
  }

  db.run(`CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT DEFAULT '',
    address TEXT DEFAULT '',
    bank_name TEXT DEFAULT '',
    account_no TEXT DEFAULT '',
    account_holder TEXT DEFAULT '',
    hourly_rate INTEGER DEFAULT 13500,
    transport_fee INTEGER DEFAULT 9000,
    memo TEXT DEFAULT '',
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth TEXT DEFAULT '',
    gender TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    address TEXT DEFAULT '',
    grade TEXT DEFAULT '',
    income_tier TEXT DEFAULT 'basic',
    guardian_name TEXT DEFAULT '',
    guardian_phone TEXT DEFAULT '',
    service_type TEXT DEFAULT '가사지원',
    memo TEXT DEFAULT '',
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    date TEXT,
    clock_in TEXT,
    clock_out TEXT,
    hours REAL DEFAULT 0,
    clock_in_photo TEXT DEFAULT '',
    clock_out_photo TEXT DEFAULT '',
    memo TEXT DEFAULT '',
    memo_out TEXT DEFAULT '',
    status TEXT DEFAULT 'working',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attendance_id INTEGER,
    manager_id INTEGER,
    client_id INTEGER,
    date TEXT,
    data TEXT DEFAULT '{}',
    photo TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    month TEXT,
    form_type TEXT DEFAULT 'user',
    data TEXT DEFAULT '{}',
    photo TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS gov_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    month TEXT,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  // 서식10 - 기본서비스 결과보고서
  db.run(`CREATE TABLE IF NOT EXISTS service_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    month TEXT,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  // 서식11 - 기본서비스 비용청구서
  db.run(`CREATE TABLE IF NOT EXISTS cost_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    month TEXT,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS dispatch_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS transport_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    month TEXT,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS monitoring_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER,
    client_id INTEGER,
    month TEXT,
    data TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now','localtime'))
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT DEFAULT ''
  )`);

  // Default settings
  const defaultSettings = {
    org_name: '산청군 통합돌봄',
    org_rep: '',
    org_phone: '',
    org_addr: '',
    org_biz_no: '',
    org_staff: '',
    hourly_rate: '13500',
    transport_fee: '9000',
    admin_password: '1234',
    gov_rate_table: JSON.stringify({
      60: { normal: 19000, s30: 25000, s50: 29000 },
      90: { normal: 28500, s30: 37000, s50: 43000 },
      120: { normal: 38000, s30: 49000, s50: 57000 },
      150: { normal: 47500, s30: 62000, s50: 71000 },
      180: { normal: 57000, s30: 74000, s50: 86000 },
      210: { normal: 66500, s30: 86000, s50: 100000 },
      240: { normal: 76000, s30: 99000, s50: 114000 },
      270: { normal: 85500, s30: 111000, s50: 128000 },
      300: { normal: 95000, s30: 124000, s50: 143000 },
      330: { normal: 104500, s30: 136000, s50: 157000 },
      360: { normal: 114000, s30: 148000, s50: 171000 },
      390: { normal: 123500, s30: 161000, s50: 185000 },
      420: { normal: 133000, s30: 173000, s50: 200000 },
      450: { normal: 142500, s30: 185000, s50: 214000 },
      480: { normal: 152000, s30: 198000, s50: 228000 }
    })
  };

  const existCheck = db.exec("SELECT count(*) as c FROM settings");
  if (existCheck[0] && existCheck[0].values[0][0] === 0) {
    const stmt = db.prepare("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)");
    for (const [k, v] of Object.entries(defaultSettings)) {
      stmt.run([k, v]);
    }
    stmt.free();
  }

  saveDB();
  console.log('Database initialized');
}

function saveDB() {
  const data = db.export();
  const buffer = Buffer.from(data);
  fs.writeFileSync(DB_PATH, buffer);
}

function allRows(sql, params = []) {
  try {
    const stmt = db.prepare(sql);
    if (params.length) stmt.bind(params);
    const rows = [];
    while (stmt.step()) rows.push(stmt.getAsObject());
    stmt.free();
    return rows;
  } catch (e) { console.error('SQL error:', e.message, sql); return []; }
}

function oneRow(sql, params = []) {
  const rows = allRows(sql, params);
  return rows.length ? rows[0] : null;
}

let _lastInsertId = 0;

function runSql(sql, params = []) {
  try {
    db.run(sql, params);
    // Capture last_insert_rowid immediately after INSERT, before saveDB
    try {
      const stmt = db.prepare("SELECT last_insert_rowid()");
      stmt.step();
      _lastInsertId = stmt.get()[0] || 0;
      stmt.free();
    } catch(e) { _lastInsertId = 0; }
    saveDB();
  } catch (e) { console.error('SQL run error:', e.message, sql); }
}

function getLastInsertId() {
  return _lastInsertId;
}

// ─── Socket.IO ───
let connectedUsers = 0;
io.on('connection', (socket) => {
  connectedUsers++;
  io.emit('user_count', connectedUsers);
  socket.on('disconnect', () => {
    connectedUsers--;
    io.emit('user_count', connectedUsers);
  });
});

// ─── Upload ───
app.post('/api/upload', upload.single('photo'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file' });
  res.json({ path: `/uploads/${req.file.filename}` });
});

// ─── Settings ───
app.get('/api/settings', (req, res) => {
  const rows = allRows("SELECT key, value FROM settings");
  const obj = {};
  rows.forEach(r => { obj[r.key] = r.value; });
  res.json(obj);
});

app.put('/api/settings', (req, res) => {
  const data = req.body;
  for (const [k, v] of Object.entries(data)) {
    runSql("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", [k, String(v)]);
  }
  io.emit('settings_updated', data);
  res.json({ success: true });
});

// ─── Managers ───
app.get('/api/managers', (req, res) => {
  res.json(allRows("SELECT * FROM managers WHERE active=1 ORDER BY name"));
});

app.post('/api/managers', (req, res) => {
  const d = req.body;
  runSql(`INSERT INTO managers (name, phone, address, bank_name, account_no, account_holder, hourly_rate, transport_fee, memo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [d.name, d.phone||'', d.address||'', d.bank_name||'', d.account_no||'', d.account_holder||'', d.hourly_rate||13500, d.transport_fee||9000, d.memo||'']);
  io.emit('manager_added');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/managers/:id', (req, res) => {
  const d = req.body;
  runSql(`UPDATE managers SET name=?, phone=?, address=?, bank_name=?, account_no=?, account_holder=?, hourly_rate=?, transport_fee=?, memo=? WHERE id=?`,
    [d.name, d.phone||'', d.address||'', d.bank_name||'', d.account_no||'', d.account_holder||'', d.hourly_rate||13500, d.transport_fee||9000, d.memo||'', req.params.id]);
  io.emit('manager_updated');
  res.json({ success: true });
});

app.delete('/api/managers/:id', (req, res) => {
  runSql("UPDATE managers SET active=0 WHERE id=?", [req.params.id]);
  io.emit('manager_deleted');
  res.json({ success: true });
});

// ─── Clients ───
app.get('/api/clients', (req, res) => {
  const rows = allRows("SELECT * FROM clients WHERE active=1 ORDER BY name");
  rows.forEach(r => { r.birth_date = r.birth || ''; });
  res.json(rows);
});

app.post('/api/clients', (req, res) => {
  const d = req.body;
  runSql(`INSERT INTO clients (name, birth, gender, phone, address, grade, income_tier, guardian_name, guardian_phone, service_type, memo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [d.name, d.birth_date||d.birth||'', d.gender||'', d.phone||'', d.address||'', d.grade||'', d.income_tier||'basic', d.guardian_name||'', d.guardian_phone||'', d.service_type||'가사지원', d.memo||'']);
  io.emit('client_added');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/clients/:id', (req, res) => {
  const d = req.body;
  runSql(`UPDATE clients SET name=?, birth=?, gender=?, phone=?, address=?, grade=?, income_tier=?, guardian_name=?, guardian_phone=?, service_type=?, memo=? WHERE id=?`,
    [d.name, d.birth_date||d.birth||'', d.gender||'', d.phone||'', d.address||'', d.grade||'', d.income_tier||'basic', d.guardian_name||'', d.guardian_phone||'', d.service_type||'가사지원', d.memo||'', req.params.id]);
  io.emit('client_updated');
  res.json({ success: true });
});

app.delete('/api/clients/:id', (req, res) => {
  runSql("UPDATE clients SET active=0 WHERE id=?", [req.params.id]);
  io.emit('client_deleted');
  res.json({ success: true });
});

// ─── Attendance ───
app.get('/api/attendance', (req, res) => {
  let sql = `SELECT a.*, m.name as manager_name, m.hourly_rate, m.transport_fee, c.name as client_name, c.address as client_address
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.date) { sql += " AND a.date=?"; params.push(req.query.date); }
  if (req.query.month) { sql += " AND a.date LIKE ?"; params.push(req.query.month + '%'); }
  if (req.query.manager_id) { sql += " AND a.manager_id=?"; params.push(req.query.manager_id); }
  sql += " ORDER BY a.date DESC, a.clock_in DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => {
    r.hours_worked = r.hours || 0;
    r.total_pay = Math.round((r.hours || 0) * (r.hourly_rate || 13500));
    r.work_date = r.date;
  });
  res.json(rows);
});

app.post('/api/attendance/clock-in', (req, res) => {
  const d = req.body;
  const now = new Date();
  const date = kstDate();
  const time = kstTime();
  runSql(`INSERT INTO attendance (manager_id, client_id, date, clock_in, clock_in_photo, memo, status)
    VALUES (?, ?, ?, ?, ?, ?, 'working')`,
    [d.manager_id, d.client_id, date, time, d.photo||'', d.memo||'']);
  io.emit('attendance_updated');
  res.json({ success: true, id: getLastInsertId() });
});

app.post('/api/attendance/clock-out/:id', (req, res) => {
  const d = req.body;
  const now = new Date();
  const time = kstTime();
  const rec = oneRow("SELECT * FROM attendance WHERE id=?", [req.params.id]);
  let hours = 0;
  if (rec && rec.clock_in) {
    const [ih, im] = rec.clock_in.split(':').map(Number);
    const [oh, om] = time.split(':').map(Number);
    hours = Math.max(0, (oh * 60 + om - ih * 60 - im) / 60);
    hours = Math.round(hours * 100) / 100;
  }
  runSql(`UPDATE attendance SET clock_out=?, clock_out_photo=?, memo_out=?, hours=?, status='done' WHERE id=?`,
    [time, d.photo||'', d.memo||'', hours, req.params.id]);
  io.emit('attendance_updated');
  res.json({ success: true });
});

app.put('/api/attendance/:id', (req, res) => {
  const d = req.body;
  let hours = d.hours || 0;
  if (d.clock_in && d.clock_out) {
    const [ih, im] = d.clock_in.split(':').map(Number);
    const [oh, om] = d.clock_out.split(':').map(Number);
    hours = Math.max(0, (oh * 60 + om - ih * 60 - im) / 60);
    hours = Math.round(hours * 100) / 100;
  }
  runSql(`UPDATE attendance SET manager_id=?, client_id=?, date=?, clock_in=?, clock_out=?, hours=?, clock_in_photo=?, clock_out_photo=?, memo=?, memo_out=?, status=? WHERE id=?`,
    [d.manager_id, d.client_id, d.date, d.clock_in||'', d.clock_out||'', hours, d.clock_in_photo||'', d.clock_out_photo||'', d.memo||'', d.memo_out||'', d.status||'done', req.params.id]);
  io.emit('attendance_updated');
  res.json({ success: true });
});

app.delete('/api/attendance/:id', (req, res) => {
  runSql("DELETE FROM attendance WHERE id=?", [req.params.id]);
  io.emit('attendance_deleted');
  res.json({ success: true });
});

// ─── Dashboard ───
app.get('/api/dashboard', (req, res) => {
  const today = kstDate();
  const month = today.slice(0, 7);
  const working = oneRow("SELECT count(*) as c FROM attendance WHERE date=? AND status='working'", [today]);
  const completed = oneRow("SELECT count(*) as c FROM attendance WHERE date=? AND status='done'", [today]);
  const managersCount = oneRow("SELECT count(*) as c FROM managers WHERE active=1");
  const clientsCount = oneRow("SELECT count(*) as c FROM clients WHERE active=1");
  const monthData = oneRow("SELECT COALESCE(sum(hours),0) as h FROM attendance WHERE date LIKE ? AND status='done'", [month + '%']);
  const hourlyRate = oneRow("SELECT value FROM settings WHERE key='hourly_rate'");
  const rate = hourlyRate ? parseInt(hourlyRate.value) || 13500 : 13500;
  const totalHours = monthData ? monthData.h : 0;
  const totalPay = Math.round(totalHours * rate);
  res.json({
    today: {
      working_now: working ? working.c : 0,
      completed: completed ? completed.c : 0
    },
    totals: {
      managers: managersCount ? managersCount.c : 0,
      clients: clientsCount ? clientsCount.c : 0
    },
    monthly: {
      total_hours: Math.round(totalHours * 10) / 10,
      total_pay: totalPay
    }
  });
});

// ─── Live Status ───
app.get('/api/live-status', (req, res) => {
  const today = kstDate();
  const rows = allRows(`SELECT a.*, m.name as manager_name, m.hourly_rate, c.name as client_name, c.address as client_address
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.date=? ORDER BY a.clock_in DESC`, [today]);
  rows.forEach(r => {
    r.hours_worked = r.hours || 0;
    r.total_pay = Math.round((r.hours || 0) * (r.hourly_rate || 13500));
    r.work_date = r.date;
  });
  res.json(rows);
});

// ─── Monthly Summary ───
app.get('/api/summary/monthly', (req, res) => {
  const month = req.query.month || kstMonth();
  let sql = `SELECT a.manager_id, m.name as manager_name, m.hourly_rate, m.transport_fee,
    count(*) as work_days, COALESCE(sum(a.hours),0) as total_hours
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    WHERE a.date LIKE ? AND a.status='done'`;
  const params = [month + '%'];
  if (req.query.manager_id) { sql += " AND a.manager_id=?"; params.push(req.query.manager_id); }
  sql += " GROUP BY a.manager_id ORDER BY m.name";
  const rows = allRows(sql, params);
  rows.forEach(r => {
    const rate = r.hourly_rate || 13500;
    const tf = r.transport_fee || 9000;
    r.total_wage = Math.round(r.total_hours * rate);
    r.total_transport = r.work_days * tf;
    r.total_pay = r.total_wage + r.total_transport;
    r.total_amount = r.total_pay;
    r.avg_hours_per_day = r.work_days > 0 ? Math.round(r.total_hours / r.work_days * 10) / 10 : 0;
  });
  res.json(rows);
});

// ─── Monthly Report ───
app.get('/api/report/monthly', (req, res) => {
  const month = req.query.month || kstMonth();
  let sql = `SELECT a.*, m.name as manager_name, m.phone as manager_phone, m.hourly_rate, m.transport_fee, c.name as client_name, c.address as client_address
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.date LIKE ? AND a.status='done'`;
  const params = [month + '%'];
  if (req.query.manager_id) { sql += " AND a.manager_id=?"; params.push(req.query.manager_id); }
  sql += " ORDER BY a.date, m.name";
  const rows = allRows(sql, params);
  // 설정값 로드
  const settingsRows = allRows("SELECT key, value FROM settings");
  const s = {};
  settingsRows.forEach(r => { s[r.key] = r.value; });
  const hourlyWage = parseInt(s.hourly_wage) || 13500;
  const dailyTransport = parseInt(s.daily_transport) || 9000;
  rows.forEach(r => {
    r.hours_worked = r.hours || 0;
    const rate = r.hourly_rate || hourlyWage;
    const tf = r.transport_fee || dailyTransport;
    r.wage = Math.round((r.hours || 0) * rate);
    r.transport_fee_calc = tf;
    r.total_pay = r.wage + tf;
    r.work_date = r.date;
  });
  res.json({ records: rows, settings: s });
});

// ─── Daily Reports ───
app.get('/api/daily-reports', (req, res) => {
  let sql = `SELECT d.*, m.name as manager_name, c.name as client_name
    FROM daily_reports d
    LEFT JOIN managers m ON d.manager_id = m.id
    LEFT JOIN clients c ON d.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.date) { sql += " AND d.date=?"; params.push(req.query.date); }
  if (req.query.month) { sql += " AND d.date LIKE ?"; params.push(req.query.month + '%'); }
  if (req.query.manager_id) { sql += " AND d.manager_id=?"; params.push(req.query.manager_id); }
  sql += " ORDER BY d.date DESC, d.id DESC";
  const rows = allRows(sql, params);
  // data JSON 내부 필드를 최상위로 풀어서 프론트엔드에서 바로 접근 가능하게
  rows.forEach(r => {
    try {
      const d = JSON.parse(r.data || '{}');
      r.service_date = d.service_date || r.date || '';
      r.service_content = d.service_content || '';
      r.time_start = d.time_start || '';
      r.time_end = d.time_end || '';
      r.user_name = d.user_name || '';
      r.user_birth = d.user_birth || '';
      r.user_age = d.user_age || '';
      r.user_gender = d.user_gender || '';
      r.user_address = d.user_address || '';
      r.staff_name = d.staff_name || '';
      r.staff_phone = d.staff_phone || '';
      r.service_round = d.service_round || '';
      r.change_type = d.change_type || '';
      r.change_content = d.change_content || '';
      r.change_reason = d.change_reason || '';
      r.goal_type = d.goal_type || '';
      r.stop_type = d.stop_type || '';
      r.stop_detail = d.stop_detail || '';
      r.sign_name = d.sign_name || '';
      r.sign_data = d.sign_data || '';
      r.client_sign_img = d.client_sign_img || '';
      r.submit_date = d.submit_date || '';
      r.reporter_name = d.reporter_name || '';
      r.photo_path = d.photo_path || '';
      r.custom_fields = d.custom_fields || '[]';
    } catch(e) {}
  });
  res.json(rows);
});

app.get('/api/daily-reports/:id', (req, res) => {
  const row = oneRow(`SELECT d.*, m.name as manager_name, c.name as client_name
    FROM daily_reports d
    LEFT JOIN managers m ON d.manager_id = m.id
    LEFT JOIN clients c ON d.client_id = c.id
    WHERE d.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: 'Not found' });
  try {
    const d = JSON.parse(row.data || '{}');
    row.service_date = d.service_date || row.date || '';
    row.service_content = d.service_content || '';
    row.time_start = d.time_start || '';
    row.time_end = d.time_end || '';
    row.user_name = d.user_name || '';
    row.user_birth = d.user_birth || '';
    row.user_age = d.user_age || '';
    row.user_gender = d.user_gender || '';
    row.user_address = d.user_address || '';
    row.staff_name = d.staff_name || '';
    row.staff_phone = d.staff_phone || '';
    row.service_round = d.service_round || '';
    row.change_type = d.change_type || '';
    row.change_content = d.change_content || '';
    row.change_reason = d.change_reason || '';
    row.goal_type = d.goal_type || '';
    row.stop_type = d.stop_type || '';
    row.stop_detail = d.stop_detail || '';
    row.sign_name = d.sign_name || '';
    row.sign_data = d.sign_data || '';
    row.client_sign_img = d.client_sign_img || '';
    row.submit_date = d.submit_date || '';
    row.reporter_name = d.reporter_name || '';
    row.photo_path = d.photo_path || '';
    row.custom_fields = d.custom_fields || '[]';
  } catch(e) {}
  res.json(row);
});

app.post('/api/daily-reports', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, attendance_id, date, photo,
    data, created_at, manager_name, client_name, ...rest } = d;
  const dataJson = JSON.stringify(rest);
  const reportDate = date || rest.service_date || kstDate();
  runSql(`INSERT INTO daily_reports (attendance_id, manager_id, client_id, date, data, photo)
    VALUES (?, ?, ?, ?, ?, ?)`,
    [attendance_id||0, manager_id, client_id, reportDate, dataJson, photo||rest.photo_path||'']);
  io.emit('daily_report_saved');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/daily-reports/:id', (req, res) => {
  const d = req.body;
  // GET에서 풀어진 필드 + data(원본 JSON문자열) 모두 올 수 있으므로
  // DB칼럼/조인필드 제외하고 나머지를 data JSON으로 저장
  const { manager_id, client_id, attendance_id, date, photo, id,
    data, created_at, manager_name, client_name, hours_worked, total_pay, work_date,
    ...rest } = d;
  const dataJson = JSON.stringify(rest);
  const reportDate = date || rest.service_date || '';
  runSql(`UPDATE daily_reports SET attendance_id=?, manager_id=?, client_id=?, date=?, data=?, photo=? WHERE id=?`,
    [attendance_id||0, manager_id, client_id, reportDate, dataJson, photo||rest.photo_path||'', req.params.id]);
  io.emit('daily_report_saved');
  res.json({ success: true });
});

app.delete('/api/daily-reports/:id', (req, res) => {
  runSql("DELETE FROM daily_reports WHERE id=?", [req.params.id]);
  io.emit('daily_report_deleted');
  res.json({ success: true });
});

// ─── Invoices ───
app.get('/api/invoices', (req, res) => {
  let sql = `SELECT i.*, m.name as manager_name, c.name as client_name
    FROM invoices i
    LEFT JOIN managers m ON i.manager_id = m.id
    LEFT JOIN clients c ON i.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.month) { sql += " AND i.month=?"; params.push(req.query.month); }
  if (req.query.manager_id) { sql += " AND i.manager_id=?"; params.push(req.query.manager_id); }
  sql += " ORDER BY i.created_at DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => {
    try {
      const d = JSON.parse(r.data || '{}');
      Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; });
    } catch(e) {}
  });
  res.json(rows);
});

app.get('/api/invoices/:id', (req, res) => {
  const row = oneRow(`SELECT i.*, m.name as manager_name, c.name as client_name
    FROM invoices i
    LEFT JOIN managers m ON i.manager_id = m.id
    LEFT JOIN clients c ON i.client_id = c.id
    WHERE i.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: 'Not found' });
  try {
    const d = JSON.parse(row.data || '{}');
    Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; });
  } catch(e) {}
  res.json(row);
});

app.post('/api/invoices', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, form_type, photo, photo_path, ...rest } = d;
  const month = d.invoice_month || d.month || '';
  const dataJson = d.data ? JSON.stringify(d.data) : JSON.stringify(rest);
  runSql(`INSERT INTO invoices (manager_id, client_id, month, form_type, data, photo)
    VALUES (?, ?, ?, ?, ?, ?)`,
    [manager_id, client_id, month, form_type||'user', dataJson, photo||photo_path||'']);
  io.emit('invoice_saved');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/invoices/:id', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, form_type, photo, photo_path, ...rest } = d;
  const month = d.invoice_month || d.month || '';
  const dataJson = d.data ? JSON.stringify(d.data) : JSON.stringify(rest);
  runSql(`UPDATE invoices SET manager_id=?, client_id=?, month=?, form_type=?, data=?, photo=? WHERE id=?`,
    [manager_id, client_id, month, form_type||'user', dataJson, photo||photo_path||'', req.params.id]);
  io.emit('invoice_saved');
  res.json({ success: true });
});

app.delete('/api/invoices/:id', (req, res) => {
  runSql("DELETE FROM invoices WHERE id=?", [req.params.id]);
  io.emit('invoice_deleted');
  res.json({ success: true });
});

app.post('/api/invoices/auto-generate', (req, res) => {
  const d = req.body;
  const month = d.month || kstMonth();
  const records = allRows(`SELECT a.*, m.name as manager_name, m.hourly_rate, c.name as client_name
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.date LIKE ? AND a.status='done' AND a.manager_id=? AND a.client_id=?`,
    [month + '%', d.manager_id, d.client_id]);
  res.json({ records, month });
});

// ─── Gov Invoices (삭제됨 - 서식11 비용청구서로 대체) ───
// Legacy table remains for data preservation; CRUD endpoints removed.

// ─── 서식10: 기본서비스 결과보고서 ───
app.get('/api/service-reports', (req, res) => {
  let sql = `SELECT s.*, m.name as manager_name, c.name as client_name
    FROM service_reports s LEFT JOIN managers m ON s.manager_id = m.id LEFT JOIN clients c ON s.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.month) { sql += " AND s.month=?"; params.push(req.query.month); }
  sql += " ORDER BY s.created_at DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => { try { const d = JSON.parse(r.data || '{}'); Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; }); } catch(e) {} });
  res.json(rows);
});
app.get('/api/service-reports/:id', (req, res) => {
  const row = oneRow(`SELECT s.*, m.name as manager_name, c.name as client_name FROM service_reports s LEFT JOIN managers m ON s.manager_id = m.id LEFT JOIN clients c ON s.client_id = c.id WHERE s.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: 'Not found' });
  try { const d = JSON.parse(row.data || '{}'); Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; }); } catch(e) {}
  res.json(row);
});
app.post('/api/service-reports', (req, res) => {
  const d = req.body; const { manager_id, client_id, ...rest } = d;
  const month = d.month || d.service_period_start?.slice(0,7) || kstMonth();
  runSql(`INSERT INTO service_reports (manager_id, client_id, month, data) VALUES (?, ?, ?, ?)`, [manager_id, client_id, month, JSON.stringify(rest)]);
  io.emit('service_report_saved'); res.json({ success: true, id: getLastInsertId() });
});
app.put('/api/service-reports/:id', (req, res) => {
  const d = req.body; const { manager_id, client_id, ...rest } = d;
  const month = d.month || d.service_period_start?.slice(0,7) || kstMonth();
  runSql(`UPDATE service_reports SET manager_id=?, client_id=?, month=?, data=? WHERE id=?`, [manager_id, client_id, month, JSON.stringify(rest), req.params.id]);
  io.emit('service_report_saved'); res.json({ success: true });
});
app.delete('/api/service-reports/:id', (req, res) => {
  runSql("DELETE FROM service_reports WHERE id=?", [req.params.id]);
  io.emit('service_report_deleted'); res.json({ success: true });
});

// 서식10 자동생성: 일일결과등록 데이터로부터 결과보고서 생성
app.post('/api/service-reports/auto-generate', (req, res) => {
  const { manager_id, client_id, month: reqMonth } = req.body;
  const month = reqMonth || kstMonth();
  const today = kstDate();
  const settingsRows = allRows("SELECT key, value FROM settings");
  const s = {}; settingsRows.forEach(r => { s[r.key] = r.value; });
  const mgr = oneRow("SELECT * FROM managers WHERE id=?", [manager_id]);
  const cli = oneRow("SELECT * FROM clients WHERE id=?", [client_id]);
  if (!mgr || !cli) return res.status(400).json({ error: '매니저 또는 대상자를 찾을 수 없습니다.' });

  // 일일결과등록 데이터
  const reports = allRows(`SELECT dr.data FROM daily_reports dr WHERE dr.manager_id=? AND dr.client_id=? AND dr.date LIKE ? ORDER BY dr.date`, [manager_id, client_id, month + '%']);
  if (!reports.length) return res.json({ error: '해당 월의 일일결과등록이 없습니다.' });

  const items = reports.map(r => { try { return JSON.parse(r.data || '{}'); } catch(e) { return {}; } });
  const firstDate = items[0].service_date || '';
  const lastDate = items[items.length - 1].service_date || '';

  // 회차별 상세
  const rounds = items.map((it, i) => ({
    round: it.service_round || String(i + 1),
    date: it.service_date || '',
    time_start: it.time_start || '',
    time_end: it.time_end || '',
    content: it.service_content || ''
  }));

  // 기존 삭제 후 재생성
  runSql("DELETE FROM service_reports WHERE manager_id=? AND client_id=? AND month=?", [manager_id, client_id, month]);

  const data = {
    provider_name: s.provider_name || '',
    provider_contact: s.provider_contact || s.claimant_name || '',
    provider_phone: s.provider_phone || '',
    staff_name: mgr.name, staff_phone: mgr.phone || '',
    client_name: cli.name, client_birth: cli.birth || '', client_age: '',
    client_gender: cli.gender || '', client_address: cli.address || '',
    service_name: '가사지원', service_period_start: firstDate, service_period_end: lastDate,
    rounds: rounds,
    change_status: '변경없음', change_content: '', change_reason: '',
    goal_status: '', stop_reason: '', org_opinion: '',
    submit_date: today,
    claim_org: s.provider_name || '', claim_rep: s.provider_rep || ''
  };

  runSql("INSERT INTO service_reports (manager_id, client_id, month, data) VALUES (?, ?, ?, ?)",
    [manager_id, client_id, month, JSON.stringify(data)]);
  io.emit('service_report_saved');
  res.json({ success: true, id: getLastInsertId(), ...data });
});

// ─── 서식11: 기본서비스 비용청구서 ───
app.get('/api/cost-claims', (req, res) => {
  let sql = `SELECT s.*, m.name as manager_name, c.name as client_name
    FROM cost_claims s LEFT JOIN managers m ON s.manager_id = m.id LEFT JOIN clients c ON s.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.month) { sql += " AND s.month=?"; params.push(req.query.month); }
  sql += " ORDER BY s.created_at DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => { try { const d = JSON.parse(r.data || '{}'); Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; }); } catch(e) {} });
  res.json(rows);
});
app.get('/api/cost-claims/:id', (req, res) => {
  const row = oneRow(`SELECT s.*, m.name as manager_name, c.name as client_name FROM cost_claims s LEFT JOIN managers m ON s.manager_id = m.id LEFT JOIN clients c ON s.client_id = c.id WHERE s.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: 'Not found' });
  try { const d = JSON.parse(row.data || '{}'); Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; }); } catch(e) {}
  res.json(row);
});
app.post('/api/cost-claims', (req, res) => {
  const d = req.body; const { manager_id, client_id, ...rest } = d;
  const month = d.month || kstMonth();
  runSql(`INSERT INTO cost_claims (manager_id, client_id, month, data) VALUES (?, ?, ?, ?)`, [manager_id, client_id, month, JSON.stringify(rest)]);
  io.emit('cost_claim_saved'); res.json({ success: true, id: getLastInsertId() });
});
app.put('/api/cost-claims/:id', (req, res) => {
  const d = req.body; const { manager_id, client_id, ...rest } = d;
  const month = d.month || kstMonth();
  runSql(`UPDATE cost_claims SET manager_id=?, client_id=?, month=?, data=? WHERE id=?`, [manager_id, client_id, month, JSON.stringify(rest), req.params.id]);
  io.emit('cost_claim_saved'); res.json({ success: true });
});
app.delete('/api/cost-claims/:id', (req, res) => {
  runSql("DELETE FROM cost_claims WHERE id=?", [req.params.id]);
  io.emit('cost_claim_deleted'); res.json({ success: true });
});

// 서식11 자동생성: 출석+일일결과 데이터로부터 비용청구서 생성
app.post('/api/cost-claims/auto-generate', (req, res) => {
  const { manager_id, client_id, month: reqMonth } = req.body;
  const month = reqMonth || kstMonth();
  const today = kstDate();
  const settingsRows = allRows("SELECT key, value FROM settings");
  const s = {}; settingsRows.forEach(r => { s[r.key] = r.value; });
  const mgr = oneRow("SELECT * FROM managers WHERE id=?", [manager_id]);
  const cli = oneRow("SELECT * FROM clients WHERE id=?", [client_id]);
  if (!mgr || !cli) return res.status(400).json({ error: '매니저 또는 대상자를 찾을 수 없습니다.' });

  // 출석 + 일일결과 데이터
  const attRows = allRows(`SELECT * FROM attendance WHERE manager_id=? AND client_id=? AND date LIKE ? AND status='done' ORDER BY date`,
    [manager_id, client_id, month + '%']);
  const drRows = allRows(`SELECT * FROM daily_reports WHERE manager_id=? AND client_id=? AND date LIKE ? ORDER BY date`,
    [manager_id, client_id, month + '%']);
  if (!attRows.length) return res.json({ error: '해당 월의 출석 기록이 없습니다.' });

  const hourlyWage = parseInt(s.hourly_wage) || 13500;
  const dailyTransport = parseInt(s.daily_transport) || 9000;
  const incomeTier = cli.income_tier || 'basic';
  let burdenRate = 0;
  if (incomeTier === 'low') burdenRate = 0.15;
  else if (incomeTier === 'high' || incomeTier === 'general') burdenRate = 1.0;

  // 수가 테이블
  const GOV_RATES = [
    [60,19000,25000,29000],[90,28500,37000,43000],[120,38000,49000,57000],
    [150,47500,62000,71000],[180,57000,74000,86000],[210,66500,86000,100000],
    [240,76000,99000,114000],[270,85500,111000,128000],[300,95000,124000,143000],
    [330,104500,136000,157000],[360,114000,148000,171000],[390,123500,161000,185000],
    [420,133000,173000,200000],[450,142500,185000,214000],[480,152000,198000,228000]
  ];
  function getRate(minutes) {
    for (const row of GOV_RATES) { if (minutes <= row[0]) return row[1]; }
    return GOV_RATES[GOV_RATES.length - 1][1];
  }

  // 회차별 상세 (서식11 테이블)
  const items = attRows.map((att, i) => {
    const dr = drRows.find(d => {
      try { const dd = JSON.parse(d.data || '{}'); return dd.service_date === att.date; } catch(e) { return false; }
    });
    const drData = dr ? JSON.parse(dr.data || '{}') : {};
    const hours = att.hours || 0;
    const minutes = Math.round(hours * 60);
    const provideAmount = getRate(minutes);
    const surcharge = 0; // 고난이도 가산은 기본 0
    const transportClaim = dailyTransport; // 원거리 교통지원금
    const personalBurden = Math.round(provideAmount * burdenRate);
    const claimable = provideAmount + surcharge - personalBurden;
    return {
      round: drData.service_round || String(i + 1),
      date: att.date,
      time_start: drData.time_start || att.clock_in?.slice(11,16) || '',
      time_end: drData.time_end || att.clock_out?.slice(11,16) || '',
      hours: hours.toFixed(1),
      minutes: minutes,
      content: drData.service_content || '',
      note: '',
      provide_amount: provideAmount,
      surcharge: surcharge,
      transport: transportClaim,
      personal_burden: personalBurden,
      claimable: claimable + transportClaim
    };
  });

  const totalProvide = items.reduce((s, i) => s + i.provide_amount, 0);
  const totalSurcharge = items.reduce((s, i) => s + i.surcharge, 0);
  const totalTransport = items.reduce((s, i) => s + i.transport, 0);
  const totalPersonal = items.reduce((s, i) => s + i.personal_burden, 0);
  const totalClaimable = items.reduce((s, i) => s + i.claimable, 0);

  // 기존 삭제 후 재생성
  runSql("DELETE FROM cost_claims WHERE manager_id=? AND client_id=? AND month=?", [manager_id, client_id, month]);

  const data = {
    service_type: '가사지원',
    provider_name: s.provider_name || '', provider_contact: s.provider_contact || s.claimant_name || '',
    staff_name: mgr.name,
    client_name: cli.name, client_birth: cli.birth || '', client_gender: cli.gender || '',
    client_dong: '', client_address: cli.address || '',
    income_tier: incomeTier, burden_rate: burdenRate,
    items: items,
    total_provide: totalProvide, total_surcharge: totalSurcharge,
    total_transport: totalTransport, total_personal: totalPersonal,
    total_claimable: totalClaimable,
    submit_date: today, submit_year: today.slice(0,4), submit_month: today.slice(5,7), submit_day: today.slice(8,10),
    claimant_title: s.claimant_title || '', claimant_name: s.claimant_name || ''
  };

  runSql("INSERT INTO cost_claims (manager_id, client_id, month, data) VALUES (?, ?, ?, ?)",
    [manager_id, client_id, month, JSON.stringify(data)]);
  io.emit('cost_claim_saved');
  res.json({ success: true, id: getLastInsertId(), ...data });
});

// ─── Monthly Close (월 마감 - 자동 연계) ───
app.post('/api/monthly-close', (req, res) => {
  const month = req.body.month;
  if (!month) return res.status(400).json({ error: '월을 지정해주세요.' });

  const [yr, mo] = month.split('-');
  const today = kstDate();

  // 설정값 로드
  const settingsRows = allRows("SELECT key, value FROM settings");
  const s = {};
  settingsRows.forEach(r => { s[r.key] = r.value; });

  // 수가 테이블
  const GOV_RATES = [
    [60,19000,25000,29000],[90,28500,37000,43000],[120,38000,49000,57000],
    [150,47500,62000,71000],[180,57000,74000,86000],[210,66500,86000,100000],
    [240,76000,99000,114000],[270,85500,111000,128000],[300,95000,124000,143000],
    [330,104500,136000,157000],[360,114000,148000,171000],[390,123500,161000,185000],
    [420,133000,173000,200000],[450,142500,185000,214000],[480,152000,198000,228000]
  ];
  function getGovRate(minutes) {
    for (const row of GOV_RATES) { if (minutes <= row[0]) return { rate: row[1], bracket: row[0] + '분이하' }; }
    const last = GOV_RATES[GOV_RATES.length - 1];
    return { rate: last[1], bracket: '480분이하(최대)' };
  }

  // 매니저-대상자별 출석 집계
  const summaryRows = allRows(`
    SELECT a.manager_id, a.client_id, m.name as manager_name, m.hourly_rate, m.transport_fee,
      m.bank_name, m.account_no, m.account_holder,
      c.name as client_name, c.birth as client_birth, c.gender as client_gender,
      c.phone as client_phone, c.address as client_address, c.income_tier,
      count(*) as work_days, COALESCE(sum(a.hours),0) as total_hours
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.date LIKE ? AND a.status='done'
    GROUP BY a.manager_id, a.client_id
    ORDER BY m.name, c.name
  `, [month + '%']);

  // 일별 상세 기록
  const detailRows = allRows(`
    SELECT a.*, m.name as manager_name, c.name as client_name
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.date LIKE ? AND a.status='done'
    ORDER BY a.date
  `, [month + '%']);

  if (!summaryRows.length) {
    return res.json({ success: false, message: '해당 월의 출석 기록이 없습니다.' });
  }

  const results = { cost_claims: [], invoices: [], payroll_ready: true };

  for (const row of summaryRows) {
    // 근무일 목록
    const dayRecords = detailRows.filter(d => d.manager_id === row.manager_id && d.client_id === row.client_id);
    const workDates = dayRecords.map(d => d.date.slice(8, 10) + '일').join(', ');
    const avgMinutesPerDay = row.work_days > 0 ? Math.round((row.total_hours / row.work_days) * 60) : 0;

    // 소득구분에 따른 본인부담률
    const incomeTier = row.income_tier || 'basic';
    let burdenRate = 0;
    if (incomeTier === 'low') burdenRate = 0.15;
    else if (incomeTier === 'high' || incomeTier === 'general') burdenRate = 1.0;

    // ── 1) 비용청구서(서식11) 자동생성 ──
    // 일별 상세 비용 계산
    const dailyRecords = detailRows.filter(d => d.manager_id === row.manager_id && d.client_id === row.client_id);
    const drRows = allRows(`SELECT * FROM daily_reports WHERE manager_id=? AND client_id=? AND date LIKE ? ORDER BY date`,
      [row.manager_id, row.client_id, month + '%']);
    const costItems = dailyRecords.map((att, idx) => {
      const dr = drRows.find(d => { try { const dd = JSON.parse(d.data || '{}'); return dd.service_date === att.date; } catch(e) { return false; } });
      const drData = dr ? JSON.parse(dr.data || '{}') : {};
      const hours = att.hours || 0;
      const minutes = Math.round(hours * 60);
      const provideAmount = getGovRate(minutes).rate;
      const personalBurdenItem = Math.round(provideAmount * burdenRate);
      const transportClaim = parseInt(s.daily_transport) || 9000;
      return {
        round: drData.service_round || String(idx + 1), date: att.date,
        time_start: drData.time_start || att.clock_in?.slice(11,16) || '',
        time_end: drData.time_end || att.clock_out?.slice(11,16) || '',
        hours: hours.toFixed(1), minutes,
        content: drData.service_content || '',
        provide_amount: provideAmount, surcharge: 0, transport: transportClaim,
        personal_burden: personalBurdenItem,
        claimable: provideAmount - personalBurdenItem + transportClaim
      };
    });
    const totalClaimable = costItems.reduce((sum, i) => sum + i.claimable, 0);

    // 기존 비용청구서가 있으면 삭제 후 재생성
    runSql("DELETE FROM cost_claims WHERE manager_id=? AND client_id=? AND month=?",
      [row.manager_id, row.client_id, month]);

    const costData = {
      service_type: '가사지원',
      provider_name: s.provider_name || '', provider_contact: s.provider_contact || s.claimant_name || '',
      staff_name: row.manager_name || '',
      client_name: row.client_name || '', client_birth: row.client_birth || '',
      client_gender: row.client_gender || '', client_dong: '', client_address: row.client_address || '',
      income_tier: incomeTier, burden_rate: burdenRate,
      items: costItems,
      total_provide: costItems.reduce((sum, i) => sum + i.provide_amount, 0),
      total_surcharge: 0,
      total_transport: costItems.reduce((sum, i) => sum + i.transport, 0),
      total_personal: costItems.reduce((sum, i) => sum + i.personal_burden, 0),
      total_claimable: totalClaimable,
      submit_date: today, submit_year: today.slice(0,4), submit_month: today.slice(5,7), submit_day: today.slice(8,10),
      claimant_title: s.claimant_title || '', claimant_name: s.claimant_name || ''
    };
    runSql("INSERT INTO cost_claims (manager_id, client_id, month, data) VALUES (?, ?, ?, ?)",
      [row.manager_id, row.client_id, month, JSON.stringify(costData)]);
    results.cost_claims.push({ manager: row.manager_name, client: row.client_name, amount: totalClaimable });

    // ── 2) 본인부담금 청구서 자동생성 ──
    const hourlyWage = parseInt(s.hourly_wage) || 13500;
    const dailyTransport = parseInt(s.daily_transport) || 9000;
    const totalPay = Math.round(row.total_hours * hourlyWage);
    const totalTransport = row.work_days * dailyTransport;
    const basicFee = totalPay + totalTransport;
    const invPersonalBurden = Math.round(basicFee * burdenRate);
    const govSupport = basicFee - invPersonalBurden;

    // 기존 청구서 삭제 후 재생성
    runSql("DELETE FROM invoices WHERE manager_id=? AND client_id=? AND month=? AND form_type='user'",
      [row.manager_id, row.client_id, month]);

    const invData = {
      invoice_date: today,
      invoice_month: month,
      provider_name: s.provider_name || s.org_name || '',
      provider_rep: s.provider_rep || s.org_rep || '',
      provider_phone: s.provider_phone || s.org_phone || '',
      provider_address: s.provider_address || s.org_addr || '',
      biz_no: s.provider_biz_no || s.org_biz_no || '',
      provider_staff: row.manager_name || '',
      client_name: row.client_name || '',
      client_birth: row.client_birth || '',
      client_gender: row.client_gender || '',
      client_address: row.client_address || '',
      client_phone: row.client_phone || '',
      service_type: '가사지원',
      service_dates: workDates,
      work_days: row.work_days,
      total_hours: row.total_hours,
      basic_fee: basicFee,
      surcharge_fee: 0,
      personal_burden: invPersonalBurden,
      claim_amount: invPersonalBurden,
      gov_support: govSupport,
      income_tier: incomeTier,
      burden_rate: burdenRate,
      bank_name: row.bank_name || '',
      account_number: row.account_no || '',
      account_holder: row.account_holder || '',
      claimant_title: s.claimant_title || '',
      claimant_name: s.claimant_name || '',
      form_type: 'user',
      auto_generated: 1
    };
    runSql("INSERT INTO invoices (manager_id, client_id, month, form_type, data, photo) VALUES (?, ?, ?, 'user', ?, '')",
      [row.manager_id, row.client_id, month, JSON.stringify(invData)]);
    results.invoices.push({ manager: row.manager_name, client: row.client_name, personal: invPersonalBurden, gov: govSupport });
  }

  io.emit('monthly_closed', { month });
  io.emit('cost_claim_saved');
  io.emit('invoice_saved');

  res.json({
    success: true,
    month,
    message: `${month} 월 마감 완료! 비용청구서 ${results.cost_claims.length}건, 본인부담금 ${results.invoices.length}건 자동생성, 급여대장 연계 완료`,
    cost_claims: results.cost_claims,
    invoices: results.invoices
  });
});

// ─── Payroll (급여대장) ───
app.get('/api/payroll/monthly', (req, res) => {
  const month = req.query.month || kstMonth();
  let sumSql = `SELECT a.manager_id, m.name as manager_name, m.hourly_rate, m.transport_fee,
    m.bank_name, m.account_no, m.account_holder,
    count(*) as work_days, COALESCE(sum(a.hours),0) as total_hours
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    WHERE a.date LIKE ? AND a.status='done'`;
  const sumParams = [month + '%'];
  if (req.query.manager_id) { sumSql += " AND a.manager_id=?"; sumParams.push(req.query.manager_id); }
  sumSql += " GROUP BY a.manager_id ORDER BY m.name";
  const summaries = allRows(sumSql, sumParams);

  // Get detailed records per manager
  const details = {};
  let detSql = `SELECT a.*, m.name as manager_name, c.name as client_name
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.date LIKE ? AND a.status='done'`;
  const detParams = [month + '%'];
  if (req.query.manager_id) { detSql += " AND a.manager_id=?"; detParams.push(req.query.manager_id); }
  detSql += " ORDER BY a.date, a.clock_in";
  const allRecords = allRows(detSql, detParams);
  allRecords.forEach(r => {
    if (!details[r.manager_id]) details[r.manager_id] = [];
    details[r.manager_id].push(r);
  });

  res.json({ summaries, details });
});

// ─── Contracts ───
app.get('/api/contracts', (req, res) => {
  let sql = `SELECT ct.*, m.name as manager_name, c.name as client_name
    FROM contracts ct
    LEFT JOIN managers m ON ct.manager_id = m.id
    LEFT JOIN clients c ON ct.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.manager_id) { sql += " AND ct.manager_id=?"; params.push(req.query.manager_id); }
  sql += " ORDER BY ct.created_at DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => {
    try {
      const d = JSON.parse(r.data || '{}');
      Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; });
    } catch(e) {}
  });
  res.json(rows);
});

app.get('/api/contracts/:id', (req, res) => {
  const row = oneRow(`SELECT ct.*, m.name as manager_name, c.name as client_name
    FROM contracts ct
    LEFT JOIN managers m ON ct.manager_id = m.id
    LEFT JOIN clients c ON ct.client_id = c.id
    WHERE ct.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: '찾을 수 없습니다.' });
  try {
    const d = JSON.parse(row.data || '{}');
    Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; });
  } catch(e) {}
  res.json(row);
});

app.post('/api/contracts', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, ...rest } = d;
  runSql(`INSERT INTO contracts (manager_id, client_id, data) VALUES (?, ?, ?)`,
    [manager_id, client_id, JSON.stringify(rest)]);
  io.emit('contract_saved');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/contracts/:id', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, ...rest } = d;
  runSql(`UPDATE contracts SET manager_id=?, client_id=?, data=? WHERE id=?`,
    [manager_id, client_id, JSON.stringify(rest), req.params.id]);
  io.emit('contract_saved');
  res.json({ success: true });
});

app.delete('/api/contracts/:id', (req, res) => {
  runSql("DELETE FROM contracts WHERE id=?", [req.params.id]);
  io.emit('contract_deleted');
  res.json({ success: true });
});

// ─── Dispatch Apps ───
app.get('/api/dispatch-apps', (req, res) => {
  const rows = allRows("SELECT * FROM dispatch_apps ORDER BY created_at DESC");
  rows.forEach(r => {
    try {
      const d = JSON.parse(r.data || '{}');
      Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; });
    } catch(e) {}
  });
  res.json(rows);
});

app.get('/api/dispatch-apps/:id', (req, res) => {
  const row = oneRow("SELECT * FROM dispatch_apps WHERE id=?", [req.params.id]);
  if (!row) return res.status(404).json({ error: '찾을 수 없습니다.' });
  try {
    const d = JSON.parse(row.data || '{}');
    Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; });
  } catch(e) {}
  res.json(row);
});

app.post('/api/dispatch-apps', (req, res) => {
  const d = req.body;
  runSql(`INSERT INTO dispatch_apps (data) VALUES (?)`, [JSON.stringify(d)]);
  io.emit('dispatch_saved');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/dispatch-apps/:id', (req, res) => {
  const d = req.body;
  runSql(`UPDATE dispatch_apps SET data=? WHERE id=?`, [JSON.stringify(d), req.params.id]);
  io.emit('dispatch_saved');
  res.json({ success: true });
});

app.delete('/api/dispatch-apps/:id', (req, res) => {
  runSql("DELETE FROM dispatch_apps WHERE id=?", [req.params.id]);
  io.emit('dispatch_deleted');
  res.json({ success: true });
});

// ─── Transport Apps ───
app.get('/api/transport-apps', (req, res) => {
  let sql = `SELECT t.*, m.name as manager_name
    FROM transport_apps t
    LEFT JOIN managers m ON t.manager_id = m.id WHERE 1=1`;
  const params = [];
  if (req.query.month) { sql += " AND t.month=?"; params.push(req.query.month); }
  if (req.query.manager_id) { sql += " AND t.manager_id=?"; params.push(req.query.manager_id); }
  sql += " ORDER BY t.created_at DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => {
    try {
      const d = JSON.parse(r.data || '{}');
      Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; });
    } catch(e) {}
  });
  res.json(rows);
});

app.get('/api/transport-apps/:id', (req, res) => {
  const row = oneRow(`SELECT t.*, m.name as manager_name
    FROM transport_apps t
    LEFT JOIN managers m ON t.manager_id = m.id
    WHERE t.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: '찾을 수 없습니다.' });
  try {
    const d = JSON.parse(row.data || '{}');
    Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; });
  } catch(e) {}
  res.json(row);
});

app.post('/api/transport-apps', (req, res) => {
  const d = req.body;
  // 프론트엔드가 모든 필드를 최상위로 보내므로 manager_id/client_id 분리 후 나머지를 data로 저장
  const { manager_id, client_id, ...rest } = d;
  const month = d.service_period_start ? d.service_period_start.slice(0,7) : d.month || '';
  runSql(`INSERT INTO transport_apps (manager_id, month, data) VALUES (?, ?, ?)`,
    [manager_id, month, JSON.stringify(rest)]);
  io.emit('transport_app_saved');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/transport-apps/:id', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, ...rest } = d;
  const month = d.service_period_start ? d.service_period_start.slice(0,7) : d.month || '';
  runSql(`UPDATE transport_apps SET manager_id=?, month=?, data=? WHERE id=?`,
    [manager_id, month, JSON.stringify(rest), req.params.id]);
  io.emit('transport_app_saved');
  res.json({ success: true });
});

app.delete('/api/transport-apps/:id', (req, res) => {
  runSql("DELETE FROM transport_apps WHERE id=?", [req.params.id]);
  io.emit('transport_app_deleted');
  res.json({ success: true });
});

// ─── Monitoring Records (서식 08호) ───
app.get('/api/monitoring-records', (req, res) => {
  let sql = `SELECT mr.*, m.name as manager_name, c.name as client_name
    FROM monitoring_records mr
    LEFT JOIN managers m ON mr.manager_id = m.id
    LEFT JOIN clients c ON mr.client_id = c.id WHERE 1=1`;
  const params = [];
  if (req.query.manager_id) { sql += " AND mr.manager_id=?"; params.push(req.query.manager_id); }
  if (req.query.client_id) { sql += " AND mr.client_id=?"; params.push(req.query.client_id); }
  if (req.query.month) { sql += " AND mr.month=?"; params.push(req.query.month); }
  sql += " ORDER BY mr.created_at DESC";
  const rows = allRows(sql, params);
  rows.forEach(r => {
    try {
      const d = JSON.parse(r.data || '{}');
      Object.keys(d).forEach(k => { if (r[k] === undefined) r[k] = d[k]; });
    } catch(e) {}
  });
  res.json(rows);
});

app.get('/api/monitoring-records/:id', (req, res) => {
  const row = oneRow(`SELECT mr.*, m.name as manager_name, c.name as client_name
    FROM monitoring_records mr
    LEFT JOIN managers m ON mr.manager_id = m.id
    LEFT JOIN clients c ON mr.client_id = c.id
    WHERE mr.id=?`, [req.params.id]);
  if (!row) return res.status(404).json({ error: '찾을 수 없습니다.' });
  try {
    const d = JSON.parse(row.data || '{}');
    Object.keys(d).forEach(k => { if (row[k] === undefined) row[k] = d[k]; });
  } catch(e) {}
  res.json(row);
});

app.post('/api/monitoring-records', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, month, ...rest } = d;
  runSql(`INSERT INTO monitoring_records (manager_id, client_id, month, data) VALUES (?, ?, ?, ?)`,
    [manager_id || null, client_id || null, month || '', JSON.stringify(rest)]);
  io.emit('monitoring_saved');
  res.json({ success: true, id: getLastInsertId() });
});

app.put('/api/monitoring-records/:id', (req, res) => {
  const d = req.body;
  const { manager_id, client_id, month, ...rest } = d;
  runSql(`UPDATE monitoring_records SET manager_id=?, client_id=?, month=?, data=? WHERE id=?`,
    [manager_id || null, client_id || null, month || '', JSON.stringify(rest), req.params.id]);
  io.emit('monitoring_saved');
  res.json({ success: true });
});

app.delete('/api/monitoring-records/:id', (req, res) => {
  runSql("DELETE FROM monitoring_records WHERE id=?", [req.params.id]);
  io.emit('monitoring_deleted');
  res.json({ success: true });
});

// 자동연동: 출석 기록 기반 모니터링 기록지 데이터 생성
app.post('/api/monitoring-records/auto-generate', (req, res) => {
  const d = req.body;
  const managerId = d.manager_id;
  const clientId = d.client_id;
  if (!managerId || !clientId) return res.json({ error: '매니저와 대상자를 선택해주세요.' });

  // 해당 매니저-대상자의 출석 기록 조회
  const records = allRows(`
    SELECT a.date, a.clock_in, a.clock_out, a.hours, a.status,
      m.name as manager_name, c.name as client_name, c.birth as client_birth,
      c.address as client_address, c.service_type
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    LEFT JOIN clients c ON a.client_id = c.id
    WHERE a.manager_id=? AND a.client_id=? AND a.status='done'
    ORDER BY a.date ASC
  `, [managerId, clientId]);

  if (!records.length) return res.json({ error: '출석 기록이 없습니다.' });

  const firstRec = records[0];
  const lastRec = records[records.length - 1];
  const totalDays = records.length;
  const totalHours = records.reduce((sum, r) => sum + (r.hours || 0), 0);

  // 생년월일 형식 변환 (YYYY-MM-DD → YYYY.MM.DD)
  let birthFormatted = '';
  if (firstRec.client_birth) {
    birthFormatted = firstRec.client_birth.replace(/-/g, '.');
  }

  // 날짜 한글 형식
  function toKorDate(dateStr) {
    if (!dateStr) return '';
    const [y, m, d] = dateStr.split('-');
    return `${y}년${parseInt(m)}월${parseInt(d)}일`;
  }

  // 주 몇 회인지 계산 (총 일수 / 주 수)
  const firstDate = new Date(firstRec.date);
  const lastDate = new Date(lastRec.date);
  const weekSpan = Math.max(1, Math.ceil((lastDate - firstDate) / (7 * 24 * 60 * 60 * 1000)));
  const perWeek = Math.round(totalDays / weekSpan);

  const result = {
    client_name: firstRec.client_name || '',
    client_birth: birthFormatted,
    client_address: firstRec.client_address || '',
    staff_name: firstRec.manager_name || '',
    svc_cat1_1: '가사지원',
    svc_cat2_1: '가사지원',
    svc_detail_1: firstRec.service_type || '일상지원,말벗,청소,활동보조',
    svc_cycle_1: `주${perWeek}회`,
    svc_first_date_1: toKorDate(firstRec.date),
    svc_direct_date_1: toKorDate(firstRec.date),
    status_change: '개선',
    status_detail: `총 ${totalDays}회의 집중 돌봄 서비스를 제공한 결과, 대상자의 고립감이 해소되고 정서적 안정감이 크게 개선되었습니다. 주거 환경 정비와 일상 지원을 통해 스스로 생활할 수 있는 자립 능력이 향상되어 긍정적인 상태 변화를 보이고 있습니다.`,
    total_days: totalDays,
    total_hours: Math.round(totalHours * 10) / 10
  };

  res.json(result);
});

// ─── Accounting (회계장부) ───
app.get('/api/accounting/monthly', (req, res) => {
  const month = req.query.month || kstMonth();
  const [yr, mo] = month.split('-');

  // 설정값 로드
  const settingsRows = allRows("SELECT key, value FROM settings");
  const s = {};
  settingsRows.forEach(r => { s[r.key] = r.value; });
  const hourlyWage = parseInt(s.hourly_wage) || 13500;

  // ═══ 1. 수입 ① : 지자체 수가 청구서 (cost_claims / 서식11) ═══
  const claimRows = allRows(`
    SELECT s.data, s.manager_id, s.client_id,
           m.name as manager_name, c.name as client_name
    FROM cost_claims s
    LEFT JOIN managers m ON s.manager_id = m.id
    LEFT JOIN clients c ON s.client_id = c.id
    WHERE s.month=?
  `, [month]);

  let govClaimTotal = 0;       // 수가 청구 총액 (제공금액 합계)
  let govClaimClaimable = 0;   // 청구가능액 합계
  let govPersonalBurden = 0;   // 본인부담금 합계
  const claimDetails = [];
  claimRows.forEach(g => {
    try {
      const d = JSON.parse(g.data || '{}');
      const provide = d.total_provide || 0;
      const claimable = d.total_claimable || 0;
      const personal = d.total_personal || 0;
      const transport = d.total_transport || 0;
      govClaimTotal += provide;
      govClaimClaimable += claimable;
      govPersonalBurden += personal;
      claimDetails.push({
        manager_name: g.manager_name || '-',
        client_name: g.client_name || '-',
        provide_amount: provide,
        transport: transport,
        personal_burden: personal,
        claimable: claimable,
        item_count: (d.items || []).length
      });
    } catch(e) {}
  });

  // ═══ 2. 수입 ② : 원거리 교통지원금 신청서 (transport_apps) ═══
  const transportRows = allRows(`
    SELECT t.data, t.manager_id, m.name as manager_name
    FROM transport_apps t
    LEFT JOIN managers m ON t.manager_id = m.id
    WHERE t.month=?
  `, [month]);

  let transportGrantTotal = 0;
  const transportDetails = [];
  transportRows.forEach(t => {
    try {
      const d = JSON.parse(t.data || '{}');
      const amt = d.total_amount || 0;
      transportGrantTotal += amt;
      transportDetails.push({
        manager_name: t.manager_name || d.staff_name || '-',
        client_name: d.client_name || '-',
        distance_range: d.distance_range || '-',
        trip_count: d.trip_count || 0,
        per_amount: d.support_amount || 0,
        total_amount: amt
      });
    } catch(e) {}
  });

  // ═══ 3. 지출 : 매니저 급여 (시급 13,500원 × 근무시간, attendance 기반) ═══
  const attRows = allRows(`
    SELECT a.manager_id, m.name as manager_name,
      count(*) as work_days, COALESCE(sum(a.hours),0) as total_hours
    FROM attendance a
    LEFT JOIN managers m ON a.manager_id = m.id
    WHERE a.date LIKE ? AND a.status='done'
    GROUP BY a.manager_id ORDER BY m.name
  `, [month + '%']);

  let totalWage = 0;
  const managerPayroll = attRows.map((r, i) => {
    const wage = Math.round(r.total_hours * hourlyWage);
    totalWage += wage;
    return {
      no: i + 1,
      manager_name: r.manager_name || '-',
      work_days: r.work_days,
      total_hours: r.total_hours,
      hourly_rate: hourlyWage,
      wage: wage
    };
  });

  // ═══ 4. 지출 ② : 교통비 (매니저에게 지급) ═══
  // 교통지원금 신청서 기준으로 매니저에게 실제 지급하는 교통비
  const transportExpenseTotal = transportGrantTotal;

  // ═══ 5. 회계 요약 ═══
  // ※ 서식11 청구가능액(total_claimable)에 교통지원금이 이미 포함됨
  //   청구가능액 = 제공금액(수가) + 교통지원금 - 본인부담금
  //   따라서 수입 = 청구가능액 (교통지원금 별도 합산 X, 이중계산 방지)
  const totalIncome = govClaimClaimable;
  // 지출 = 급여 + 교통비
  const totalExpense = totalWage + transportExpenseTotal;
  // 순수익 = 수입 - 급여 - 교통비
  const netProfit = totalIncome - totalExpense;

  res.json({
    month, year: yr, month_num: mo,
    org_name: s.provider_name || s.org_name || '',
    org_rep: s.provider_rep || s.org_rep || '',
    hourly_wage: hourlyWage,

    // 수입 (서식11 청구가능액 = 제공금액 + 교통지원금 - 본인부담금)
    income: {
      gov_claim: {
        total_provide: govClaimTotal,         // 제공금액(수가) 합계
        total_claimable: govClaimClaimable,   // 청구가능액 (교통지원금 포함)
        total_personal_burden: govPersonalBurden,
        total_transport_included: transportGrantTotal, // 청구가능액에 포함된 교통지원금
        details: claimDetails,
        count: claimRows.length
      },
      transport_grant: {
        total: transportGrantTotal,
        details: transportDetails,
        count: transportRows.length
      },
      total: totalIncome  // = 청구가능액 (교통지원금 이미 포함)
    },

    // 지출
    expense: {
      payroll: managerPayroll,
      wage_total: totalWage,
      transport_total: transportExpenseTotal,
      transport_details: transportDetails,
      total: totalExpense
    },

    // 요약
    net_profit: netProfit
  });
});

// ─── Catch-all for SPA ───
app.get('/{*splat}', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// ─── Start ───
const PORT = 3000;
initDB().then(() => {
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}).catch(err => {
  console.error('DB init failed:', err);
  process.exit(1);
});
