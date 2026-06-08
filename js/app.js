/* ═══════════════════════════════════════════════════════════════
   경남형 틈새돌봄 매니저 근무현황 시스템 - Frontend Application
   ═══════════════════════════════════════════════════════════════ */

// ─── Global State ───
let managers = [];
let clients = [];
let settings = { hourly_wage: '13500', daily_transport: '6000' };
let currentTab = 'dashboard';
let socket = null;
let userRole = null; // 'admin' or 'manager'

// ─── Performance: API Cache + Debounce ───
const _apiCache = {};
const _cacheTTL = 2000; // 2초 캐시 (모바일 즉시 반영 개선)
const _pendingRequests = {};
const _debounceTimers = {};

function apiGet(url, ttl) {
  const now = Date.now();
  ttl = ttl || _cacheTTL;
  // 캐시가 유효하면 즉시 반환
  if (_apiCache[url] && (now - _apiCache[url].time < ttl)) {
    return Promise.resolve(_apiCache[url].data);
  }
  // 동일 URL 요청이 이미 진행 중이면 그 Promise 재사용 (중복 방지)
  if (_pendingRequests[url]) return _pendingRequests[url];
  _pendingRequests[url] = apiGet(url).then(data => {
    _apiCache[url] = { data, time: Date.now() };
    delete _pendingRequests[url];
    return data;
  }).catch(e => {
    delete _pendingRequests[url];
    throw e;
  });
  return _pendingRequests[url];
}

function invalidateCache(pattern) {
  if (!pattern) { Object.keys(_apiCache).forEach(k => delete _apiCache[k]); return; }
  Object.keys(_apiCache).forEach(k => { if (k.includes(pattern)) delete _apiCache[k]; });
}

function debounce(key, fn, delay) {
  delay = delay || 300;
  if (_debounceTimers[key]) clearTimeout(_debounceTimers[key]);
  _debounceTimers[key] = setTimeout(fn, delay);
}

// 탭별 마지막 로드 시간 (탭 전환 시 불필요한 재로드 방지)
const _tabLoadTime = {};
const _tabFreshTTL = 1000; // 1초 이내 재로드 방지

// ─── Login / Logout ───
function doLogin(role) {
  userRole = role;
  sessionStorage.setItem('gapcare_role', role);
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('mainApp').style.display = '';
  document.getElementById('mainContainer').style.display = '';
  document.getElementById('userRoleBadge').textContent = role === 'admin' ? '👑 관리자' : '👤 매니저';
  applyRoleUI();
}

function checkAdminPw() {
  const pw = document.getElementById('adminPwInput').value;
  if (pw === '3651') {
    document.getElementById('adminPwBox').style.display = 'none';
    document.getElementById('adminPwInput').value = '';
    doLogin('admin');
  } else {
    alert('비밀번호가 틀렸습니다.');
    document.getElementById('adminPwInput').value = '';
    document.getElementById('adminPwInput').focus();
  }
}

function doLogout() {
  userRole = null;
  sessionStorage.removeItem('gapcare_role');
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('mainApp').style.display = 'none';
  document.getElementById('mainContainer').style.display = 'none';
}

function applyRoleUI() {
  const tabs = document.querySelectorAll('.nav-tab[data-role]');
  tabs.forEach(tab => {
    const role = tab.getAttribute('data-role');
    if (role === 'all' || userRole === 'admin') {
      tab.style.display = '';
    } else {
      tab.style.display = 'none';
    }
  });
  // 매니저는 출퇴근 탭으로 시작
  if (userRole === 'manager') {
    switchTab('clock');
  } else {
    switchTab('dashboard');
  }
}

// ─── Socket.IO Connection ───
function initSocket() {
  socket = io({ reconnection: true, reconnectionDelay: 1000, reconnectionAttempts: 10 });
  socket.on('connect', () => { document.querySelector('.live-dot').style.background = '#34a853'; });
  socket.on('disconnect', () => { document.querySelector('.live-dot').style.background = '#d93025'; });
  socket.on('user_count', cnt => { document.getElementById('connectedCount').textContent = `접속 ${cnt}명`; });
  // 실시간 동기화 (debounce로 중복 방지 + 캐시 무효화)
  socket.on('attendance_updated', () => {
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status'); invalidateCache('summary');
    debounce('att_upd', () => { _tabLoadTime[currentTab] = 0; refreshCurrentTab(true); }, 500);
  });
  socket.on('attendance_deleted', () => {
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status'); invalidateCache('summary');
    debounce('att_del', () => { _tabLoadTime[currentTab] = 0; refreshCurrentTab(true); }, 500);
  });
  socket.on('manager_added', () => { invalidateCache('managers'); debounce('mgr', () => { loadManagers(); if (currentTab === 'managers') loadManagersList(); }, 300); });
  socket.on('manager_updated', () => { invalidateCache('managers'); debounce('mgr', () => { loadManagers(); if (currentTab === 'managers') loadManagersList(); }, 300); });
  socket.on('manager_deleted', () => { invalidateCache('managers'); debounce('mgr', () => { loadManagers(); if (currentTab === 'managers') loadManagersList(); }, 300); });
  socket.on('client_added', () => { invalidateCache('clients'); debounce('cli', () => { loadClients(); if (currentTab === 'clients') loadClientsList(); }, 300); });
  socket.on('client_updated', () => { invalidateCache('clients'); debounce('cli', () => { loadClients(); if (currentTab === 'clients') loadClientsList(); }, 300); });
  socket.on('client_deleted', () => { invalidateCache('clients'); debounce('cli', () => { loadClients(); if (currentTab === 'clients') loadClientsList(); }, 300); });
  socket.on('settings_updated', s => { settings = s; if (currentTab === 'settings') loadSettings(); });
  socket.on('daily_report_saved', () => { invalidateCache('daily-reports'); debounce('dr_save', () => { if (currentTab === 'clock') dfLoadList(); }, 300); });
  socket.on('daily_report_deleted', () => { invalidateCache('daily-reports'); debounce('dr_del', () => { if (currentTab === 'clock') dfLoadList(); }, 300); });
  socket.on('invoice_saved', () => { invalidateCache('invoices'); debounce('inv', () => { if (currentTab === 'invoice') invLoadList(); }, 300); });
  socket.on('invoice_deleted', () => { invalidateCache('invoices'); debounce('inv', () => { if (currentTab === 'invoice') invLoadList(); }, 300); });
  socket.on('contract_saved', () => { invalidateCache('contracts'); debounce('ct', () => { if (currentTab === 'contract') ctLoadList(); }, 300); });
  socket.on('contract_deleted', () => { invalidateCache('contracts'); debounce('ct', () => { if (currentTab === 'contract') ctLoadList(); }, 300); });
  socket.on('transport_app_saved', () => { invalidateCache('transport'); debounce('tr', () => { if (currentTab === 'transport') trLoadList(); }, 300); });
  socket.on('transport_app_deleted', () => { invalidateCache('transport'); debounce('tr', () => { if (currentTab === 'transport') trLoadList(); }, 300); });
  socket.on('dispatch_app_saved', () => { invalidateCache('dispatch'); debounce('dp', () => { if (currentTab === 'dispatch') dpLoadList(); }, 300); });
  socket.on('dispatch_app_deleted', () => { invalidateCache('dispatch'); debounce('dp', () => { if (currentTab === 'dispatch') dpLoadList(); }, 300); });
  socket.on('service_report_saved', () => { invalidateCache('service-reports'); debounce('rpt10', () => { if (currentTab === 'report10') rpt10LoadList(); }, 300); });
  socket.on('service_report_deleted', () => { invalidateCache('service-reports'); debounce('rpt10', () => { if (currentTab === 'report10') rpt10LoadList(); }, 300); });
  socket.on('cost_claim_saved', () => { invalidateCache('cost-claims'); debounce('clm11', () => { if (currentTab === 'claim11') clm11LoadList(); }, 300); });
  socket.on('cost_claim_deleted', () => { invalidateCache('cost-claims'); debounce('clm11', () => { if (currentTab === 'claim11') clm11LoadList(); }, 300); });
  socket.on('force_refresh', () => { invalidateCache(); _tabLoadTime[currentTab] = 0; refreshCurrentTab(true); });
}

// ─── API Helpers ───
async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
async function apiPost(url, data) {
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  if (!res.ok) { const err = await res.json().catch(() => ({ error: 'Request failed' })); throw new Error(err.error || 'Request failed'); }
  return res.json();
}
async function apiPut(url, data) {
  const res = await fetch(url, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  if (!res.ok) { const err = await res.json().catch(() => ({ error: 'Request failed' })); throw new Error(err.error || 'Request failed'); }
  return res.json();
}
async function apiDelete(url) {
  const res = await fetch(url, { method: 'DELETE' });
  if (!res.ok) throw new Error('Delete failed');
  return res.json();
}

// ─── Toast Notifications ───
function showToast(msg, type = 'info') {
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateY(20px)'; setTimeout(() => t.remove(), 300); }, 3000);
}

// ─── Formatting Helpers ───
function formatMoney(n) { return (n || 0).toLocaleString('ko-KR') + '원'; }
function formatTime(dt) {
  if (!dt) return '-';
  // "14:55" 같은 HH:MM 순수 시간 문자열 → 바로 한국어로 변환
  if (typeof dt === 'string' && /^\d{1,2}:\d{2}(:\d{2})?$/.test(dt.trim())) {
    const [h, m] = dt.trim().split(':').map(Number);
    const period = h < 12 ? '오전' : '오후';
    const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
    return `${period} ${h12}:${String(m).padStart(2, '0')}`;
  }
  // "2026-04-28 14:53:34" 형식
  if (typeof dt === 'string' && dt.includes(' ')) {
    const [, timePart] = dt.split(' ');
    if (timePart) {
      const [h, m] = timePart.split(':').map(Number);
      const period = h < 12 ? '오전' : '오후';
      const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
      return `${period} ${h12}:${String(m).padStart(2, '0')}`;
    }
  }
  // ISO 형식
  if (typeof dt === 'string' && dt.includes('T')) {
    const [, timePart] = dt.split('T');
    if (timePart) {
      const [h, m] = timePart.split(':').map(Number);
      const period = h < 12 ? '오전' : '오후';
      const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
      return `${period} ${h12}:${String(m).padStart(2, '0')}`;
    }
  }
  return dt;
}
function formatDate(dt) {
  if (!dt) return '-';
  return dt.split(' ')[0];
}
function formatDateTime(dt) {
  if (!dt) return '-';
  if (typeof dt === 'string' && dt.includes(' ')) {
    const [datePart, timePart] = dt.split(' ');
    if (timePart) return datePart + ' ' + timePart.slice(0, 8);
  }
  return dt;
}
function formatTimeWithSec(dt) {
  if (!dt) return '-';
  if (typeof dt === 'string' && dt.includes(' ')) {
    const [, timePart] = dt.split(' ');
    if (timePart) return timePart.slice(0, 8);
  }
  if (typeof dt === 'string' && dt.includes('T')) {
    const [, timePart] = dt.split('T');
    if (timePart) return timePart.slice(0, 8);
  }
  const d = new Date(dt);
  return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}
function calcAge(birthStr) {
  if (!birthStr) return '';
  const birth = new Date(birthStr);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return age;
}
function todayStr() {
  // Use KST (UTC+9) to get correct Korean date
  const now = new Date();
  const kst = new Date(now.getTime() + (9 * 60 * 60 * 1000));
  return kst.toISOString().split('T')[0];
}
function currentMonthStr() { return todayStr().slice(0, 7); }
function elapsedStr(clockIn) {
  if (!clockIn) return '';
  // clockIn is KST string from server, current time needs KST too
  const nowKST = new Date(Date.now() + (9 * 60 * 60 * 1000));
  // Parse clockIn as UTC to compare with nowKST (also treated as UTC via toISOString)
  const clockInStr = clockIn.replace(' ', 'T') + 'Z';
  const clockInTime = new Date(clockInStr).getTime();
  const diff = nowKST.getTime() - clockInTime;
  if (diff < 0) return '0시간 0분';
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  return `${h}시간 ${m}분`;
}

// ─── Photo Upload Helper ───
async function uploadPhoto(fileInput) {
  if (!fileInput.files || !fileInput.files[0]) return '';
  const fd = new FormData();
  fd.append('photo', fileInput.files[0]);
  const res = await fetch('/api/upload', { method: 'POST', body: fd });
  if (!res.ok) throw new Error('Photo upload failed');
  const data = await res.json();
  // 사진 저장 위치 + 촬영시간 안내
  const now = new Date();
  const kst = new Date(now.getTime() + 9*60*60*1000);
  const timeStr = `${kst.getUTCFullYear()}-${String(kst.getUTCMonth()+1).padStart(2,'0')}-${String(kst.getUTCDate()).padStart(2,'0')} ${String(kst.getUTCHours()).padStart(2,'0')}:${String(kst.getUTCMinutes()).padStart(2,'0')}`;
  showToast(`📷 사진 저장완료 (${timeStr}) 경로: uploads/${data.filename}`, 'success');
  return data.path;
}

// 촬영시간 포맷 (KST)
function photoTimeNow() {
  const now = new Date();
  const kst = new Date(now.getTime() + 9*60*60*1000);
  return `${kst.getUTCFullYear()}-${String(kst.getUTCMonth()+1).padStart(2,'0')}-${String(kst.getUTCDate()).padStart(2,'0')} ${String(kst.getUTCHours()).padStart(2,'0')}:${String(kst.getUTCMinutes()).padStart(2,'0')}:${String(kst.getUTCSeconds()).padStart(2,'0')}`;
}

function setupPhotoPreview(inputId, previewId, areaId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  const area = document.getElementById(areaId);
  if (!input || !preview || !area) return;
  input.addEventListener('change', function () {
    if (this.files && this.files[0]) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        area.classList.add('has-photo');
        area.classList.remove('photo-required');
        // 경고 메시지 숨기기
        const warnMap = { 'clockPhotoInput': 'clockPhotoWarning', 'clockOutPhotoInputInline': 'clockOutPhotoWarning' };
        const warnEl = document.getElementById(warnMap[inputId]);
        if (warnEl) warnEl.classList.remove('show');
        showPhotoInPrintArea(inputId, e.target.result);
      };
      reader.readAsDataURL(this.files[0]);
    }
  });
}

// 사진 선택 시 인쇄 양식의 사진 영역에도 즉시 표시
function showPhotoInPrintArea(inputId, dataUrl) {
  const mapping = {
    'invPhotoInput': { printArea: 'invPhotoPrintArea', printImg: 'invPhotoPrintImg', display: 'invPhotoDisplay', displayImg: 'invPhotoImg' },

    'trPhotoInput': { printArea: 'trPhotoPrintArea', printImg: 'trPhotoPrintImg', display: 'trPhotoDisplay', displayImg: 'trPhotoImg' },
    'dpPhotoInput': { printArea: 'dpPhotoPrintArea', printImg: 'dpPhotoPrintImg', display: 'dpPhotoDisplay', displayImg: 'dpPhotoImg' }
  };
  const m = mapping[inputId];
  if (!m) return;
  // 인쇄 양식 사진 영역 표시
  const printArea = document.getElementById(m.printArea);
  if (printArea) printArea.style.display = 'block';
  const printImg = document.getElementById(m.printImg);
  if (printImg) printImg.src = dataUrl;
  // 저장된 사진 미리보기 영역도 표시
  if (m.savedDisp) {
    const savedDisp = document.getElementById(m.savedDisp);
    if (savedDisp) savedDisp.style.display = 'block';
    const savedImg = document.getElementById(m.savedImg);
    if (savedImg) savedImg.src = dataUrl;
  }
  if (m.display) {
    const disp = document.getElementById(m.display);
    if (disp) disp.style.display = 'block';
    const dispImg = document.getElementById(m.displayImg);
    if (dispImg) dispImg.src = dataUrl;
  }
}

function viewPhoto(src) {
  const modal = document.getElementById('photoViewModal');
  document.getElementById('photoViewImg').src = src;
  modal.classList.add('active');
}

// ═══════════════════════════════════════
// CUSTOM FIELDS (dynamic form fields)
// ═══════════════════════════════════════
const customFieldsState = { df: [], inv: [], ct: [], tr: [], dp: [] };

function addCustomField(prefix) {
  if (!customFieldsState[prefix]) customFieldsState[prefix] = [];
  const container = document.getElementById(`${prefix}CustomFields`);
  if (!container) return showToast('커스텀 필드 영역을 찾을 수 없습니다.', 'error');
  const idx = customFieldsState[prefix].length;
  const id = `${prefix}_cf_${idx}`;
  customFieldsState[prefix].push({ id, label: '', value: '' });
  const wrapper = document.createElement('div');
  wrapper.className = 'custom-field-row';
  wrapper.id = `${id}_row`;
  wrapper.innerHTML = `
    <table class="df-table" style="margin-top:8px;">
      <tbody><tr>
        <td class="df-label" style="width:120px;"><input type="text" class="df-input" id="${id}_label" placeholder="필드명" style="font-weight:600;text-align:center;"></td>
        <td><input type="text" class="df-input" id="${id}_value" placeholder="내용 입력"></td>
        <td style="width:40px;text-align:center;"><button class="btn btn-sm btn-danger" onclick="removeCustomField('${prefix}',${idx})">✕</button></td>
      </tr></tbody>
    </table>`;
  container.appendChild(wrapper);
}

function removeCustomField(prefix, idx) {
  const cf = customFieldsState[prefix]?.[idx];
  if (!cf) return;
  const row = document.getElementById(`${cf.id}_row`);
  if (row) row.remove();
  customFieldsState[prefix][idx] = null;
}

function collectCustomFields(prefix) {
  if (!customFieldsState[prefix]) return [];
  return customFieldsState[prefix]
    .filter(cf => cf !== null)
    .map(cf => ({
      label: document.getElementById(`${cf.id}_label`)?.value || '',
      value: document.getElementById(`${cf.id}_value`)?.value || ''
    }))
    .filter(cf => cf.label || cf.value);
}

function renderCustomFields(prefix, fields) {
  const container = document.getElementById(`${prefix}CustomFields`);
  if (!container) return;
  container.innerHTML = '';
  customFieldsState[prefix] = [];
  if (!fields || !fields.length) return;
  fields.forEach(f => {
    addCustomField(prefix);
    const idx = customFieldsState[prefix].length - 1;
    const cf = customFieldsState[prefix][idx];
    if (cf) {
      const labelEl = document.getElementById(`${cf.id}_label`);
      const valueEl = document.getElementById(`${cf.id}_value`);
      if (labelEl) labelEl.value = f.label || '';
      if (valueEl) valueEl.value = f.value || '';
    }
  });
}

// ═══════════════════════════════════════
// TABS & NAVIGATION
// ═══════════════════════════════════════
function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.section').forEach(s => {
    s.classList.toggle('active', s.id === `sec-${tab}`);
    s.classList.remove('print-active');
  });
  refreshCurrentTab();
}

function refreshCurrentTab(force) {
  const now = Date.now();
  if (!force && _tabLoadTime[currentTab] && (now - _tabLoadTime[currentTab] < _tabFreshTTL)) return;
  _tabLoadTime[currentTab] = now;
  switch (currentTab) {
    case 'dashboard': loadDashboard(); loadLiveStatus(); loadDashboardPhotos(); break;
    case 'clock': if (!window._skipAutoLoadClock) loadTodayClock(); dfLoadList(); break;
    case 'records': loadRecords(); break;
    case 'summary': loadSummary(); break;
    case 'invoice': invLoadList(); break;
    case 'payroll': payrollLoad(); break;
    case 'monitoring': monLoadList(); break;
    case 'accounting': acctLoad(); break;
    case 'report10': rpt10LoadList(); break;
    case 'claim11': clm11LoadList(); break;
    case 'contract': ctLoadList(); break;
    case 'transport': trLoadList(); break;
    case 'dispatch': dpLoadList(); break;
    case 'managers': loadManagersList(); break;
    case 'clients': loadClientsList(); break;
    case 'settings': loadSettings(); break;
  }
}

// ─── Modal Helpers ───
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

// ─── Clock Update ───
function updateClock() {
  // Show KST time regardless of browser timezone
  const now = new Date();
  const kst = new Date(now.getTime() + (9 * 60 * 60 * 1000));
  const el = document.getElementById('currentTime');
  if (el) {
    const month = kst.getUTCMonth() + 1;
    const day = kst.getUTCDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const wd = weekdays[kst.getUTCDay()];
    const hh = String(kst.getUTCHours()).padStart(2, '0');
    const mm = String(kst.getUTCMinutes()).padStart(2, '0');
    const ss = String(kst.getUTCSeconds()).padStart(2, '0');
    el.textContent = `${month}월 ${day}일 (${wd}) ${hh}:${mm}:${ss}`;
  }
}

// ═══════════════════════════════════════
// DATA LOADING
// ═══════════════════════════════════════
async function loadManagers() {
  try {
    managers = await apiGet('/api/managers', 30000);
    populateManagerDropdowns();
  } catch (e) { console.error('Load managers error:', e); }
}

async function loadClients() {
  try {
    clients = await apiGet('/api/clients', 30000);
    populateClientDropdowns();
  } catch (e) { console.error('Load clients error:', e); }
}

async function loadSettings() {
  try {
    settings = await apiGet('/api/settings', 30000);
    const w = document.getElementById('settingWage');
    const t = document.getElementById('settingTransport');
    if (w) w.value = settings.hourly_wage || 13500;
    if (t) t.value = settings.daily_transport || 9000;
    // Provider info fields
    const provFields = {
      settingProvName: 'provider_name',
      settingProvRep: 'provider_rep',
      settingProvContact: 'provider_contact',
      settingProvPhone: 'provider_phone',
      settingProvAddress: 'provider_address',
      settingProvBizNo: 'provider_biz_no',
      settingClaimantTitle: 'claimant_title',
      settingClaimantName: 'claimant_name'
    };
    Object.entries(provFields).forEach(([elId, key]) => {
      const el = document.getElementById(elId);
      if (el && settings[key]) el.value = settings[key];
    });
  } catch (e) { console.error('Load settings error:', e); }
}

function populateManagerDropdowns() {
  const selectors = ['clockManager', 'filterManager', 'summaryManager', 'printManager', 'dfManager', 'invManager', 'ctManager', 'trManager', 'dpManager', 'editAttManager', 'rpt10Manager', 'clm11Manager', 'payrollManager', 'monManager'];
  selectors.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const val = el.value;
    const isFilter = ['filterManager', 'summaryManager', 'printManager', 'payrollManager'].includes(id);
    const placeholder = isFilter ? '전체 매니저' : '-- 매니저 선택 --';
    el.innerHTML = `<option value="">${placeholder}</option>` + managers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
    if (val) el.value = val;
  });
}

function populateClientDropdowns() {
  const selectors = ['clockClient', 'dfClient', 'invClient', 'ctClient', 'trClient', 'dpClient', 'editAttClient', 'rpt10Client', 'clm11Client', 'monClient'];
  selectors.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const val = el.value;
    el.innerHTML = `<option value="">-- 대상자 선택 --</option>` + clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    if (val) el.value = val;
  });
}

// ═══════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════
async function loadDashboard() {
  try {
    const data = await apiGet('/api/dashboard');
    document.getElementById('statWorking').textContent = data.today.working_now;
    document.getElementById('statCompleted').textContent = data.today.completed;
    document.getElementById('statManagers').textContent = data.totals.managers;
    document.getElementById('statClients').textContent = data.totals.clients;
    document.getElementById('statMonthHours').textContent = (data.monthly.total_hours || 0).toFixed(1) + 'h';
    document.getElementById('statMonthPay').textContent = formatMoney(data.monthly.total_pay || 0);
  } catch (e) { console.error('Dashboard error:', e); }
}

async function loadLiveStatus() {
  try {
    const records = await apiGet('/api/live-status');
    const el = document.getElementById('liveStatusList');
    if (!records.length) { el.innerHTML = '<div class="empty-state"><div class="icon">😴</div><p>오늘 근무 기록이 없습니다.</p></div>'; return; }
    el.innerHTML = records.map(r => {
      const isActive = !r.clock_out;
      return `<div class="live-card ${isActive ? 'active' : 'done'}">
        <div class="live-name">${r.manager_name}</div>
        <div class="live-client">👤 ${r.client_name} ${r.client_address ? '· ' + r.client_address : ''}</div>
        <div class="live-time">🕐 ${formatTime(r.clock_in)}${r.clock_out ? ' ~ ' + formatTime(r.clock_out) : ' ~ 근무중 (' + elapsedStr(r.clock_in) + ')'}</div>
        <div class="live-status ${isActive ? 'status-working' : 'status-done'}">${isActive ? '🟢 근무중' : `✅ 완료 (${(r.hours_worked || 0).toFixed(1)}h / ${formatMoney(r.total_pay)})`}</div>
      </div>`;
    }).join('');
  } catch (e) { console.error('Live status error:', e); }
}

// 대시보드 오늘 출퇴근 사진 현황
async function loadDashboardPhotos() {
  try {
    const today = todayStr();
    const records = await apiGet(`/api/attendance?date=${today}`);
    const card = document.getElementById('dashboardPhotoCard');
    const el = document.getElementById('dashboardPhotoList');
    const hasPhotos = records.some(r => r.clock_in_photo || r.clock_out_photo);
    if (!hasPhotos) { card.style.display = 'none'; return; }
    card.style.display = '';
    el.innerHTML = records.filter(r => r.clock_in_photo || r.clock_out_photo).map(r => {
      let html = `<div class="photo-report-card">`;
      html += `<div class="photo-report-header">`;
      html += `<span class="photo-report-names">${r.manager_name} → ${r.client_name}</span>`;
      html += `<span class="photo-report-date">${formatDate(r.work_date)}</span>`;
      html += `</div>`;
      html += `<div class="photo-report-grid">`;
      if (r.clock_in_photo) {
        html += `<div class="photo-report-item">`;
        html += `<div class="photo-report-label in">🟢 출근</div>`;
        html += `<div class="photo-with-time">`;
        html += `<img src="${r.clock_in_photo}" class="photo-in" onclick="viewPhoto('${r.clock_in_photo}')">`;
        html += `<div class="photo-time-overlay">📸 ${formatDateTime(r.clock_in)}</div>`;
        html += `</div>`;
        html += `</div>`;
      }
      if (r.clock_out_photo) {
        html += `<div class="photo-report-item">`;
        html += `<div class="photo-report-label out">🔴 퇴근</div>`;
        html += `<div class="photo-with-time">`;
        html += `<img src="${r.clock_out_photo}" class="photo-out" onclick="viewPhoto('${r.clock_out_photo}')">`;
        html += `<div class="photo-time-overlay">📸 ${r.clock_out ? formatDateTime(r.clock_out) : '-'}</div>`;
        html += `</div>`;
        html += `</div>`;
      }
      html += `</div></div>`;
      return html;
    }).join('');
  } catch (e) { console.error('Dashboard photos error:', e); }
}

// ═══════════════════════════════════════
// CLOCK IN / OUT
// ═══════════════════════════════════════
async function clockIn() {
  const managerId = document.getElementById('clockManager').value;
  const clientId = document.getElementById('clockClient').value;
  const memo = document.getElementById('clockMemo').value;
  const photoInput = document.getElementById('clockPhotoInput');
  const photoArea = document.getElementById('clockPhotoArea');
  const photoWarn = document.getElementById('clockPhotoWarning');
  if (!managerId || !clientId) return showToast('매니저와 대상자를 선택해주세요.', 'error');
  if (!photoInput.files || !photoInput.files[0]) {
    photoArea.classList.add('photo-required');
    if (photoWarn) photoWarn.classList.add('show');
    setTimeout(() => { photoArea.classList.remove('photo-required'); }, 3000);
    return showToast('출근 사진을 첨부해주세요.', 'error');
  }
  if (photoWarn) photoWarn.classList.remove('show');
  try {
    const photoPath = await uploadPhoto(photoInput);
    await apiPost('/api/attendance/clock-in', { manager_id: parseInt(managerId), client_id: parseInt(clientId), photo: photoPath, memo });
    showToast('출근이 기록되었습니다! ✅', 'success');
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status');
    document.getElementById('clockMemo').value = '';
    photoInput.value = '';
    document.getElementById('clockPhotoPreview').src = '';
    document.getElementById('clockPhotoArea').classList.remove('has-photo');
    // 출근 시간 자동으로 일지 진행시간(시작)에 등록
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('dfTimeStart').value = `${hh}:${mm}`;
    loadTodayClock();
  } catch (e) { showToast('출근 기록 실패: ' + e.message, 'error'); }
}

async function showClockOutModal() {
  try {
    const today = todayStr();
    const records = await apiGet(`/api/attendance?date=${today}`, 2000);
    const active = records.filter(r => r.clock_in && !r.clock_out);
    const sel = document.getElementById('clockOutSelect');
    sel.innerHTML = '<option value="">-- 선택 --</option>' + active.map(r => `<option value="${r.id}">${r.manager_name} → ${r.client_name} (${formatTime(r.clock_in)}~)</option>`).join('');
    document.getElementById('clockOutPhotoInput').value = '';
    document.getElementById('clockOutPhotoPreview').src = '';
    document.getElementById('clockOutPhotoArea').classList.remove('has-photo');
    document.getElementById('clockOutMemo').value = '';
    openModal('clockOutModal');
  } catch (e) { showToast('퇴근 목록 로드 실패', 'error'); }
}

async function clockOut() {
  const id = document.getElementById('clockOutSelect').value;
  const photoInput = document.getElementById('clockOutPhotoInput');
  const memo = document.getElementById('clockOutMemo').value;
  if (!id) return showToast('퇴근할 기록을 선택해주세요.', 'error');
  try {
    let photoPath = '';
    if (photoInput.files && photoInput.files[0]) photoPath = await uploadPhoto(photoInput);
    await apiPost(`/api/attendance/clock-out/${id}`, { photo: photoPath, memo });
    showToast('퇴근이 처리되었습니다! 🔴', 'success');
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status');
    closeModal('clockOutModal');
    loadTodayClock();
  } catch (e) { showToast('퇴근 처리 실패: ' + e.message, 'error'); }
}

// 인라인 퇴근 처리 (드롭다운 없이 자동으로 활성 기록 찾아서 퇴근)
async function clockOutInline() {
  let id = document.getElementById('clockOutSelectInline').value;
  // 선택된 값이 없으면 오늘의 활성(퇴근 안 한) 기록을 자동으로 찾기
  if (!id) {
    try {
      const today = todayStr();
      invalidateCache('attendance');
      const records = await apiGet(`/api/attendance?date=${today}`);
      const active = records.filter(r => r.clock_in && !r.clock_out);
      if (active.length === 0) return showToast('퇴근할 활성 기록이 없습니다.', 'error');
      if (active.length === 1) {
        id = active[0].id;
      } else {
        document.getElementById('clockOutSelectInline').style.display = '';
        return showToast('퇴근할 기록이 여러 개입니다. 선택해주세요.', 'error');
      }
    } catch (e) { return showToast('기록 조회 실패', 'error'); }
  }
  // 퇴근 사진 필수 검증
  const photoInput = document.getElementById('clockOutPhotoInputInline');
  const photoArea = document.getElementById('clockOutPhotoAreaInline');
  const photoWarn = document.getElementById('clockOutPhotoWarning');
  if (!photoInput.files || !photoInput.files[0]) {
    photoArea.classList.add('photo-required');
    if (photoWarn) photoWarn.classList.add('show');
    setTimeout(() => { photoArea.classList.remove('photo-required'); }, 3000);
    return showToast('퇴근 사진을 첨부해주세요.', 'error');
  }
  if (photoWarn) photoWarn.classList.remove('show');
  // 일지 미작성 경고 (저장은 진행하되 알림)
  const dfContent = document.getElementById('dfServiceContent');
  const dfMissing = !dfContent || !dfContent.value.trim();
  const memo = document.getElementById('clockOutMemoInline').value;
  try {
    const photoPath = await uploadPhoto(photoInput);
    await apiPost(`/api/attendance/clock-out/${id}`, { photo: photoPath, memo });
    showToast('퇴근이 처리되었습니다! 🔴', 'success');
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status');
    document.getElementById('clockOutMemoInline').value = '';
    photoInput.value = '';
    document.getElementById('clockOutPhotoPreviewInline').src = '';
    document.getElementById('clockOutPhotoAreaInline').classList.remove('has-photo');
    // 퇴근 시간 자동으로 일지 진행시간(종료)에 등록
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('dfTimeEnd').value = `${hh}:${mm}`;
    loadTodayClock();
    // 퇴근 완료 후 일지 자동 저장 시도
    if (dfMissing) {
      showToast('⚠️ 일지(서비스내용)가 작성되지 않았습니다. 일지를 작성해주세요!', 'error');
    } else {
      await dfSave();
      showToast('일지도 자동 저장되었습니다! 📝', 'success');
    }
  } catch (e) { showToast('퇴근 처리 실패: ' + e.message, 'error'); }
}

async function loadTodayClock() {
  try {
    const today = todayStr();
    const records = await apiGet(`/api/attendance?date=${today}`, 2000);
    const el = document.getElementById('todayClockList');
    const photoReport = document.getElementById('clockPhotoReport');
    const photoBody = document.getElementById('clockPhotoReportBody');
    // 인라인 퇴근 셀렉트 업데이트 (1개면 자동선택)
    const inlineSel = document.getElementById('clockOutSelectInline');
    if (inlineSel) {
      const active = records.filter(r => r.clock_in && !r.clock_out);
      inlineSel.innerHTML = '<option value="">-- 퇴근할 기록 선택 --</option>' + active.map(r => `<option value="${r.id}">${r.manager_name} → ${r.client_name} (${formatTime(r.clock_in)}~)</option>`).join('');
      if (active.length === 1) inlineSel.value = active[0].id;
    }
    if (!records.length) {
      el.innerHTML = '<div class="empty-state"><div class="icon">📭</div><p>오늘 근무 기록이 없습니다.</p></div>';
      if (photoReport) photoReport.style.display = 'none';
      return;
    }
    el.innerHTML = `<div class="table-wrapper"><table class="data-table"><thead><tr><th>매니저</th><th>대상자</th><th>출근</th><th>퇴근</th><th>시간</th><th>급여</th></tr></thead><tbody>` +
      records.map(r => `<tr><td>${r.manager_name}</td><td>${r.client_name}</td><td>${formatTime(r.clock_in)}</td><td>${r.clock_out ? formatTime(r.clock_out) : '근무중'}</td><td>${(r.hours_worked || 0).toFixed(1)}h</td><td>${formatMoney(r.total_pay)}</td></tr>`).join('') +
      `</tbody></table></div>`;
    // 사진 보고용 (큰 사진 + 실시간 등록시간)
    const hasPhotos = records.some(r => r.clock_in_photo || r.clock_out_photo);
    if (photoReport && photoBody && hasPhotos) {
      photoReport.style.display = '';
      photoBody.innerHTML = records.filter(r => r.clock_in_photo || r.clock_out_photo).map(r => {
        let html = `<div class="photo-report-card">`;
        html += `<div class="photo-report-header">`;
        html += `<span class="photo-report-names">${r.manager_name} → ${r.client_name}</span>`;
        html += `<span class="photo-report-date">${formatDate(r.work_date)}</span>`;
        html += `</div>`;
        html += `<div class="photo-report-grid">`;
        if (r.clock_in_photo) {
          html += `<div class="photo-report-item">`;
          html += `<div class="photo-report-label in">🟢 출근</div>`;
          html += `<div class="photo-with-time">`;
          html += `<img src="${r.clock_in_photo}" class="photo-in" onclick="viewPhoto('${r.clock_in_photo}')">`;
          html += `<div class="photo-time-overlay">📸 ${formatDateTime(r.clock_in)}</div>`;
          html += `</div>`;
          html += `</div>`;
        }
        if (r.clock_out_photo) {
          html += `<div class="photo-report-item">`;
          html += `<div class="photo-report-label out">🔴 퇴근</div>`;
          html += `<div class="photo-with-time">`;
          html += `<img src="${r.clock_out_photo}" class="photo-out" onclick="viewPhoto('${r.clock_out_photo}')">`;
          html += `<div class="photo-time-overlay">📸 ${r.clock_out ? formatDateTime(r.clock_out) : '-'}</div>`;
          html += `</div>`;
          html += `</div>`;
        }
        html += `</div></div>`;
        return html;
      }).join('');
    } else if (photoReport) {
      photoReport.style.display = 'none';
    }
  } catch (e) { console.error('Today clock error:', e); }
}

// ─── 출퇴근 사진 보고서 인쇄 ───
function printClockPhotos() {
  const sec = document.getElementById('sec-clock');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// RECORDS
// ═══════════════════════════════════════
async function loadRecords() {
  try {
    const date = document.getElementById('filterDate').value;
    const month = document.getElementById('filterMonth').value;
    const managerId = document.getElementById('filterManager').value;
    let url = '/api/attendance?';
    if (date) url += `date=${date}&`;
    else if (month) url += `month=${month}&`;
    if (managerId) url += `manager_id=${managerId}&`;
    if (!date && !month && !managerId) url += `month=${currentMonthStr()}&`;
    const records = await apiGet(url);
    // 일지 데이터도 함께 로드
    let drUrl = '/api/daily-reports?';
    if (date) drUrl += `date=${date}&`;
    else if (month) drUrl += `month=${month}&`;
    else drUrl += `month=${currentMonthStr()}&`;
    const dailyReports = await apiGet(drUrl);
    const body = document.getElementById('recordsBody');
    const empty = document.getElementById('recordsEmpty');
    if (!records.length) { body.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    body.innerHTML = records.map(r => {
      const photos = [];
      if (r.clock_in_photo) photos.push(`<span class="thumb-with-time"><img src="${r.clock_in_photo}" class="photo-thumb" onclick="viewPhoto('${r.clock_in_photo}')" title="출근"><span class="thumb-time">출근</span></span>`);
      else photos.push(`<span class="thumb-with-time thumb-empty" title="출근 사진 없음"><span class="thumb-placeholder">🟢</span><span class="thumb-time">출근없음</span></span>`);
      if (r.clock_out_photo) photos.push(`<span class="thumb-with-time"><img src="${r.clock_out_photo}" class="photo-thumb" onclick="viewPhoto('${r.clock_out_photo}')" title="퇴근"><span class="thumb-time">퇴근</span></span>`);
      else photos.push(`<span class="thumb-with-time thumb-empty" title="퇴근 사진 없음"><span class="thumb-placeholder">🔴</span><span class="thumb-time">퇴근없음</span></span>`);
      // 해당 날짜+매니저+대상자에 매칭되는 일지 찾기
      const dr = dailyReports.find(d => d.service_date === r.work_date && d.manager_id === r.manager_id && d.client_id === r.client_id);
      const drContent = dr ? `<div style="max-width:200px;font-size:0.75rem;white-space:pre-wrap;overflow:hidden;text-overflow:ellipsis;max-height:60px;">${dr.service_content || '-'}</div><button class="btn btn-sm btn-outline" onclick="event.stopPropagation();viewReportWithPhotos(${dr.id},'${r.work_date}');" style="margin-top:4px;font-size:0.7rem;">📝 보기</button>` : '<span style="color:#999;font-size:0.75rem;">미작성</span>';
      return `<tr>
        <td>${formatDate(r.work_date)}</td><td>${r.manager_name}</td><td>${r.client_name}</td>
        <td>${formatTime(r.clock_in)}</td><td>${r.clock_out ? formatTime(r.clock_out) : '-'}</td>
        <td>${(r.hours_worked || 0).toFixed(1)}h</td>
        <td>${photos.join(' ') || '-'}</td>
        <td>${drContent}</td>
        <td class="actions">
          <button class="btn btn-sm btn-outline" onclick="editAttendance(${r.id})">✏️</button>
          <button class="btn btn-sm btn-danger" onclick="deleteAttendance(${r.id})">🗑️</button>
        </td></tr>`;
    }).join('');
    // 데이터를 전역에 저장 (인쇄용)
    window._lastRecords = records;
    window._lastDailyReports = dailyReports;
  } catch (e) { console.error('Records error:', e); }
}

function loadRecordsByMonth() {
  document.getElementById('filterDate').value = '';
  loadRecords();
}
function togglePhotoGallery() {
  const gallery = document.getElementById('photoGallery');
  const body = document.getElementById('photoGalleryBody');
  if (gallery.style.display !== 'none') { gallery.style.display = 'none'; return; }
  const records = window._lastRecords;
  if (!records || !records.length) { showToast('먼저 기록을 조회하세요.', 'warning'); return; }
  const withPhotos = records.filter(r => r.clock_in_photo || r.clock_out_photo);
  if (!withPhotos.length) { body.innerHTML = '<p style="color:#999;padding:20px;text-align:center;">사진이 있는 기록이 없습니다.</p>'; gallery.style.display = ''; return; }
  body.innerHTML = withPhotos.map(r => {
    let html = '<div style="border:1px solid #e0e0e0;border-radius:8px;padding:8px;min-width:200px;max-width:280px;">';
    html += '<div style="font-weight:700;font-size:0.82rem;margin-bottom:6px;">' + formatDate(r.work_date) + ' | ' + r.manager_name + ' → ' + r.client_name + '</div>';
    if (r.clock_in_photo) html += '<div style="margin-bottom:4px;"><div style="font-size:0.72rem;color:#0d904f;font-weight:600;">🟢 출근 ' + formatTime(r.clock_in) + '</div><img src="' + r.clock_in_photo + '" style="width:100%;max-height:180px;object-fit:cover;border-radius:6px;cursor:pointer;" onclick="viewPhoto(\'' + r.clock_in_photo + '\')"></div>';
    else html += '<div style="padding:20px;text-align:center;color:#ccc;font-size:0.8rem;">출근사진 없음</div>';
    if (r.clock_out_photo) html += '<div><div style="font-size:0.72rem;color:#d93025;font-weight:600;">🔴 퇴근 ' + formatTime(r.clock_out) + '</div><img src="' + r.clock_out_photo + '" style="width:100%;max-height:180px;object-fit:cover;border-radius:6px;cursor:pointer;" onclick="viewPhoto(\'' + r.clock_out_photo + '\')"></div>';
    else html += '<div style="padding:20px;text-align:center;color:#ccc;font-size:0.8rem;">퇴근사진 없음</div>';
    html += '</div>';
    return html;
  }).join('');
  gallery.style.display = '';
}

// 근무기록+일지 출력 (일일결과등록 양식 + 출퇴근 사진)
function printRecordsReport() {
  const records = window._lastRecords;
  const dailyReports = window._lastDailyReports;
  if (!records || !records.length) return showToast('출력할 기록이 없습니다.', 'error');
  const css = `
    <style>
      * { margin:0; padding:0; box-sizing:border-box; }
      body { font-family: 'Malgun Gothic','맑은 고딕',sans-serif; font-size:11pt; color:#000; }
      .page { page-break-after:always; padding:30px 40px; }
      .page:last-child { page-break-after:auto; }
      .title { text-align:center; font-size:16pt; font-weight:bold; margin-bottom:4px; }
      .subtitle { text-align:center; font-size:9pt; color:#666; margin-bottom:18px; }
      table { width:100%; border-collapse:collapse; margin-bottom:10px; }
      th, td { border:1px solid #333; padding:6px 10px; font-size:10pt; }
      th.section { background:#e8e8e8; text-align:left; font-weight:bold; font-size:10.5pt; }
      td.label { background:#f5f5f5; width:120px; font-weight:bold; white-space:nowrap; }
      .content-cell { white-space:pre-wrap; min-height:80px; vertical-align:top; }
      .report-line { margin:15px 0; font-size:10pt; text-align:center; }
      .sign-area { margin:10px 0; }
      .sign-area table td { text-align:center; }
      .sign-area img { print-color-adjust:exact; -webkit-print-color-adjust:exact; }
      .date-line { text-align:center; margin:10px 0; font-size:10pt; }
      .to-line { text-align:center; font-size:11pt; font-weight:bold; margin:5px 0 20px; }
      .photo-section { border:1px solid #333; padding:15px; margin-top:10px; page-break-inside:avoid; }
      .photo-section-title { font-size:11pt; font-weight:bold; margin-bottom:12px; text-align:center; }
      .photo-grid { display:flex; justify-content:center; gap:30px; }
      .photo-item { text-align:center; }
      .photo-item img { max-width:250px; max-height:200px; border:1px solid #ccc; }
      .photo-label { font-size:9pt; color:#555; margin-bottom:4px; font-weight:bold; }
      .photo-time { font-size:8pt; color:#888; margin-top:2px; }
      @media print { .page { padding:15px 25px; } }
    </style>`;
  let html = '';
  records.forEach(r => {
    const dr = dailyReports ? dailyReports.find(d => d.service_date === r.work_date && d.manager_id === r.manager_id && d.client_id === r.client_id) : null;
    const mgr = managers.find(m => m.id === r.manager_id) || {};
    const cli = clients.find(c => c.id === r.client_id) || {};
    html += '<div class="page">';
    // 제목
    html += '<div class="title">산청군 통합돌봄 기본서비스 일일 결과등록</div>';
    html += '<div class="subtitle">※ &lt;전액 자부담 이용자&gt;도 작성 및 제출</div>';
    // ■ 제공기관 및 제공인력
    html += '<table><tr><th class="section" colspan="4">■ 제공기관 및 제공인력</th></tr>';
    html += `<tr><td class="label">제공인력 성명</td><td colspan="3">${dr ? dr.staff_name || mgr.name || '' : mgr.name || ''}</td></tr>`;
    html += `<tr><td class="label">제공인력 연락처</td><td colspan="3">${dr ? dr.staff_phone || mgr.phone || '' : mgr.phone || ''}</td></tr>`;
    html += '</table>';
    // ■ 돌봄대상자 인적사항
    html += '<table><tr><th class="section" colspan="6">■ 돌봄대상자 인적사항</th></tr>';
    html += `<tr><td class="label">성명</td><td>${dr ? dr.user_name || cli.name || '' : cli.name || ''}</td>`;
    const birthVal = (dr && dr.user_birth) ? dr.user_birth : (cli.birth_date || '');
    const ageVal = (dr && dr.user_age) ? dr.user_age : (birthVal ? calcAge(birthVal) : '');
    html += `<td class="label">생년월일</td><td>${birthVal}</td>`;
    html += `<td class="label">만 나이</td><td>${ageVal ? ageVal + ' 세' : ''}</td></tr>`;
    const gender = dr ? dr.gender || dr.user_gender || cli.gender || '' : cli.gender || '';
    html += `<tr><td class="label">성별</td><td>${gender === '남' ? '● 남 ○ 여' : gender === '여' ? '○ 남 ● 여' : '○ 남 ○ 여'}</td>`;
    html += `<td class="label">주소</td><td colspan="3">${dr ? dr.user_address || cli.address || '' : cli.address || ''}</td></tr>`;
    html += '</table>';
    // ■ 서비스 제공 내역
    html += '<table><tr><th class="section" colspan="6">■ 서비스 제공 내역</th></tr>';
    html += `<tr><td class="label">서비스 회차</td><td>${dr ? dr.service_round || '' : ''}</td>`;
    html += `<td class="label">일자</td><td>${dr ? dr.service_date || r.work_date : r.work_date}</td>`;
    html += `<td class="label">진행시간</td><td>${dr ? (dr.time_start || formatTime(r.clock_in)) : formatTime(r.clock_in)} ~ ${dr ? (dr.time_end || (r.clock_out ? formatTime(r.clock_out) : '')) : (r.clock_out ? formatTime(r.clock_out) : '-')}</td></tr>`;
    html += `<tr><td class="label">서비스내용</td><td colspan="5" class="content-cell">${dr ? dr.service_content || '' : ''}</td></tr>`;
    html += '</table>';
    // 당초 의뢰 대비 서비스 변경사항
    const changeVal = dr ? dr.change_status || '변경없음' : '변경없음';
    html += '<table><tr><th class="section" colspan="4">당초 의뢰 대비 서비스 변경사항</th></tr>';
    html += `<tr><td colspan="4" style="padding:8px 10px;">${changeVal === '변경없음' ? '● 변경없음 ○ 변경됨' : '○ 변경없음 ● 변경됨'}</td></tr>`;
    if (changeVal === '변경됨' && dr) {
      html += `<tr><td class="label">변경내용</td><td>${dr.change_content || ''}</td><td class="label">변경사유</td><td>${dr.change_reason || ''}</td></tr>`;
    }
    html += '</table>';
    // 서비스 목표 달성 여부
    const goalVal = dr ? dr.goal_status || '' : '';
    html += '<table><tr><th class="section" colspan="2">서비스 목표 달성 여부</th></tr>';
    html += `<tr><td colspan="2" style="padding:8px 10px;">${goalVal === '종결' ? '● ' : '○ '}의뢰된 서비스 지원 종결 &nbsp;&nbsp; ${goalVal === '중단' ? '● ' : '○ '}중단</td></tr>`;
    html += '</table>';
    // 보고 문구
    html += `<div class="report-line"><strong>${dr ? dr.staff_name || mgr.name || '' : mgr.name || ''}</strong> 은/는 해당 서비스 이용자에게 위와 같은 내용으로 서비스를 제공하였음을 보고합니다.</div>`;
    // 서비스 이용자 확인
    html += '<table class="sign-area"><tr><th class="section" colspan="2">서비스 이용자 또는 보호자 확인</th></tr>';
    html += `<tr><td class="label">성 명</td><td style="display:flex;align-items:center;gap:10px;">${dr ? dr.sign_name || '' : ''} (서명) ${dr && dr.sign_data ? `<img src="${dr.sign_data}" style="max-height:50px;max-width:180px;vertical-align:middle;" alt="서명">` : ''}</td></tr>`;
    html += '</table>';
    // 날짜 + 산청군수 귀하
    html += `<div class="date-line">${dr ? dr.submit_date || r.work_date : r.work_date}</div>`;
    html += '<div class="to-line">산청군수 귀하</div>';
    // 출퇴근 사진 보고서
    if (r.clock_in_photo || r.clock_out_photo) {
      html += '<div class="photo-section">';
      html += '<div class="photo-section-title">📷 출퇴근 사진 보고서</div>';
      html += '<div class="photo-grid">';
      if (r.clock_in_photo) {
        html += `<div class="photo-item"><div class="photo-label">출근 사진</div><img src="${r.clock_in_photo}"><div class="photo-time">${formatTime(r.clock_in)}</div></div>`;
      }
      if (r.clock_out_photo) {
        html += `<div class="photo-item"><div class="photo-label">퇴근 사진</div><img src="${r.clock_out_photo}"><div class="photo-time">${r.clock_out ? formatTime(r.clock_out) : ''}</div></div>`;
      }
      html += '</div></div>';
    }
    html += '</div>'; // .page end
  });
  const w = window.open('', '_blank');
  w.document.write(`<html><head><title>근무기록 일지 출력</title>${css}</head><body>${html}<script>window.onload=function(){window.print();}<\/script></body></html>`);
  w.document.close();
}

function editAttendance(id) {
  fetch(`/api/attendance?`).then(r => r.json()).then(records => {
    const rec = records.find(r => r.id === id);
    if (!rec) return showToast('기록을 찾을 수 없습니다.', 'error');
    document.getElementById('editAttId').value = rec.id;
    document.getElementById('editAttClockIn').value = rec.clock_in ? rec.clock_in.replace(' ', 'T') : '';
    document.getElementById('editAttClockOut').value = rec.clock_out ? rec.clock_out.replace(' ', 'T') : '';
    document.getElementById('editAttMemo').value = rec.memo || '';
    document.getElementById('editAttManager').innerHTML = managers.map(m => `<option value="${m.id}" ${m.id == rec.manager_id ? 'selected' : ''}>${m.name}</option>`).join('');
    document.getElementById('editAttClient').innerHTML = clients.map(c => `<option value="${c.id}" ${c.id == rec.client_id ? 'selected' : ''}>${c.name}</option>`).join('');
    // 기존 사진 미리보기
    const inWrap = document.getElementById('editAttClockInPhotoPreviewWrap');
    inWrap.innerHTML = rec.clock_in_photo ? `<img src="${rec.clock_in_photo}" style="max-width:120px;border-radius:4px;">` : '<span style="color:#999;">사진 없음</span>';
    const outWrap = document.getElementById('editAttClockOutPhotoPreviewWrap');
    outWrap.innerHTML = rec.clock_out_photo ? `<img src="${rec.clock_out_photo}" style="max-width:120px;border-radius:4px;">` : '<span style="color:#999;">사진 없음</span>';
    document.getElementById('editAttClockInPhoto').value = '';
    document.getElementById('editAttClockOutPhoto').value = '';
    openModal('editAttendanceModal');
  });
}

async function saveAttendanceEdit() {
  const id = document.getElementById('editAttId').value;
  const data = {
    manager_id: parseInt(document.getElementById('editAttManager').value),
    client_id: parseInt(document.getElementById('editAttClient').value),
    clock_in: document.getElementById('editAttClockIn').value.replace('T', ' '),
    clock_out: document.getElementById('editAttClockOut').value.replace('T', ' '),
    memo: document.getElementById('editAttMemo').value
  };
  // 사진 업로드 처리
  const inPhotoInput = document.getElementById('editAttClockInPhoto');
  if (inPhotoInput.files && inPhotoInput.files[0]) {
    data.clock_in_photo = await uploadPhoto(inPhotoInput);
  }
  const outPhotoInput = document.getElementById('editAttClockOutPhoto');
  if (outPhotoInput.files && outPhotoInput.files[0]) {
    data.clock_out_photo = await uploadPhoto(outPhotoInput);
  }
  try {
    await apiPut(`/api/attendance/${id}`, data);
    showToast('기록이 수정되었습니다.', 'success');
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status');
    closeModal('editAttendanceModal');
    loadRecords();
  } catch (e) { showToast('수정 실패: ' + e.message, 'error'); }
}

async function deleteAttendance(id) {
  if (!confirm('정말 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/attendance/${id}`);
    showToast('기록이 삭제되었습니다.', 'success');
    invalidateCache('attendance'); invalidateCache('dashboard'); invalidateCache('live-status');
    loadRecords();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

// ═══════════════════════════════════════
// MONTHLY SUMMARY
// ═══════════════════════════════════════
async function loadSummary() {
  const month = document.getElementById('summaryMonth').value || currentMonthStr();
  const managerId = document.getElementById('summaryManager').value;
  try {
    let url = `/api/summary/monthly?month=${month}`;
    if (managerId) url += `&manager_id=${managerId}`;
    const data = await apiGet(url);
    const body = document.getElementById('summaryBody');
    const empty = document.getElementById('summaryEmpty');
    const totalsEl = document.getElementById('summaryTotals');
    if (!data.length) { body.innerHTML = ''; empty.style.display = 'block'; totalsEl.style.display = 'none'; return; }
    empty.style.display = 'none';
    body.innerHTML = data.map(r => `<tr>
      <td>${r.manager_name}</td><td>${r.work_days}일</td><td>${(r.total_hours || 0).toFixed(1)}h</td>
      <td>${(r.avg_hours_per_day || 0).toFixed(1)}h</td><td>${formatMoney(r.total_wage)}</td>
      <td>${formatMoney(r.total_transport)}</td><td><strong>${formatMoney(r.total_pay)}</strong></td>
    </tr>`).join('');
    const grandHours = data.reduce((s, r) => s + (r.total_hours || 0), 0);
    const grandPay = data.reduce((s, r) => s + (r.total_pay || 0), 0);
    const grandWage = data.reduce((s, r) => s + (r.total_wage || 0), 0);
    const grandTransport = data.reduce((s, r) => s + (r.total_transport || 0), 0);
    totalsEl.innerHTML = `<strong>합계:</strong> 총 ${grandHours.toFixed(1)}시간 / 급여 ${formatMoney(grandWage)} / 교통비 ${formatMoney(grandTransport)} / <strong>총 지급 ${formatMoney(grandPay)}</strong>`;
    totalsEl.style.display = 'block';
  } catch (e) { console.error('Summary error:', e); }
}

// ═══════════════════════════════════════
// MONTHLY PRINT REPORT
// ═══════════════════════════════════════
async function loadPrintReport() {
  const month = document.getElementById('printMonth').value || currentMonthStr();
  const managerId = document.getElementById('printManager').value;
  try {
    let url = `/api/report/monthly?month=${month}`;
    if (managerId) url += `&manager_id=${managerId}`;
    const data = await apiGet(url);
    const area = document.getElementById('printReportArea');
    if (!data.records || !data.records.length) {
      area.innerHTML = '<div class="empty-state"><div class="icon">📊</div><p>해당 월의 데이터가 없습니다.</p></div>';
      return;
    }
    const grouped = {};
    data.records.forEach(r => {
      if (!grouped[r.manager_id]) grouped[r.manager_id] = { name: r.manager_name, phone: r.manager_phone, records: [] };
      grouped[r.manager_id].records.push(r);
    });
    let html = `<div class="print-report"><div class="print-report-header"><h2>경남형 틈새돌봄 월별 근무현황</h2><p>${month} | 시급: ${formatMoney(parseFloat(data.settings.hourly_wage || 13500))} | 일 교통비: ${formatMoney(parseFloat(data.settings.daily_transport || 9000))}</p></div>`;
    let grandTotalHours = 0, grandTotalWage = 0, grandTotalTransport = 0, grandTotalPay = 0;
    Object.values(grouped).forEach(mg => {
      let mHours = 0, mWage = 0, mTransport = 0, mPay = 0;
      html += `<div class="print-manager-section"><div class="print-manager-title">👤 ${mg.name} ${mg.phone ? '(' + mg.phone + ')' : ''}</div>`;
      html += `<table class="print-table"><thead><tr><th>날짜</th><th>대상자</th><th>주소</th><th>출근</th><th>퇴근</th><th>시간</th><th>급여</th><th>교통비</th><th>합계</th><th>출근사진</th><th>퇴근사진</th></tr></thead><tbody>`;
      mg.records.forEach(r => {
        mHours += r.hours_worked || 0; mWage += r.wage || 0; mTransport += r.transport_fee || 0; mPay += r.total_pay || 0;
        html += `<tr><td>${r.work_date}</td><td>${r.client_name}</td><td>${r.client_address || '-'}</td><td>${formatTime(r.clock_in)}</td><td>${formatTime(r.clock_out)}</td><td>${(r.hours_worked || 0).toFixed(1)}h</td><td>${formatMoney(r.wage)}</td><td>${formatMoney(r.transport_fee)}</td><td>${formatMoney(r.total_pay)}</td>`;
        html += `<td>${r.clock_in_photo ? `<img src="${r.clock_in_photo}" class="print-photo" onclick="viewPhoto('${r.clock_in_photo}')">` : '-'}</td>`;
        html += `<td>${r.clock_out_photo ? `<img src="${r.clock_out_photo}" class="print-photo" onclick="viewPhoto('${r.clock_out_photo}')">` : '-'}</td></tr>`;
      });
      html += `</tbody></table>`;
      html += `<div class="print-summary-box"><div class="print-summary-item"><div class="label">근무일수</div><div class="value">${mg.records.length}일</div></div><div class="print-summary-item"><div class="label">총 시간</div><div class="value">${mHours.toFixed(1)}h</div></div><div class="print-summary-item"><div class="label">총 급여</div><div class="value">${formatMoney(mWage)}</div></div><div class="print-summary-item"><div class="label">총 교통비</div><div class="value">${formatMoney(mTransport)}</div></div><div class="print-summary-item"><div class="label">총 지급</div><div class="value">${formatMoney(mPay)}</div></div></div></div>`;
      grandTotalHours += mHours; grandTotalWage += mWage; grandTotalTransport += mTransport; grandTotalPay += mPay;
    });
    html += `<div class="print-grand-total"><div class="print-summary-item"><div class="label">총 근무시간</div><div class="value">${grandTotalHours.toFixed(1)}h</div></div><div class="print-summary-item"><div class="label">총 급여</div><div class="value">${formatMoney(grandTotalWage)}</div></div><div class="print-summary-item"><div class="label">총 교통비</div><div class="value">${formatMoney(grandTotalTransport)}</div></div><div class="print-summary-item"><div class="label">총 지급액</div><div class="value">${formatMoney(grandTotalPay)}</div></div></div>`;
    html += `<div class="print-footer">경남형 틈새돌봄 매니저 근무현황 시스템 | 출력일: ${todayStr()}</div></div>`;
    area.innerHTML = html;
    showToast('보고서가 생성되었습니다.', 'success');
  } catch (e) { showToast('보고서 생성 실패', 'error'); }
}

function doPrint() {
  const sec = document.getElementById('sec-print');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// MONTHLY CLOSE (월 마감 - 자동 연계)
// ═══════════════════════════════════════
async function monthlyClose() {
  const month = document.getElementById('summaryMonth').value || currentMonthStr();
  const [yr, mo] = month.split('-');

  // 확인 다이얼로그
  const confirmed = confirm(
    `📋 ${yr}년 ${mo}월 마감을 실행하시겠습니까?\n\n` +
    `다음 문서가 자동 생성됩니다:\n` +
    `  ✅ 지자체 청구서 (서비스 수가 기반)\n` +
    `  ✅ 대상자용 청구서 (소득구분별)\n` +
    `  ✅ 급여대장 연계 (출석 기반 자동계산)\n\n` +
    `⚠️ 기존 자동생성 문서는 재생성됩니다.`
  );
  if (!confirmed) return;

  try {
    showToast('🔄 월 마감 처리 중...', 'info');
    const result = await apiPost('/api/monthly-close', { month });

    if (!result.success) {
      showToast(result.message || '마감 처리 실패', 'error');
      return;
    }

    // 성공 결과 표시
    let detail = `🎉 ${result.month} 월 마감 완료!\n\n`;

    if (result.cost_claims && result.cost_claims.length) {
      detail += `💰 비용청구서 ${result.cost_claims.length}건 생성:\n`;
      result.cost_claims.forEach(g => {
        detail += `  • ${g.manager} → ${g.client}: ${(g.amount || 0).toLocaleString('ko-KR')}원\n`;
      });
    }

    if (result.invoices && result.invoices.length) {
      detail += `\n💳 대상자용 청구서 ${result.invoices.length}건 생성:\n`;
      result.invoices.forEach(inv => {
        detail += `  • ${inv.manager} → ${inv.client}: 본인부담 ${(inv.personal || 0).toLocaleString('ko-KR')}원 / 정부지원 ${(inv.gov || 0).toLocaleString('ko-KR')}원\n`;
      });
    }

    detail += `\n💰 급여대장: 출석 기반 자동 연계 완료`;

    alert(detail);
    showToast(result.message, 'success');

    // 관련 캐시 무효화 및 뷰 새로고침
    invalidateCache('summary');
    invalidateCache('cost-claims');
    invalidateCache('service-reports');
    invalidateCache('invoices');
    invalidateCache('payroll');
    invalidateCache('attendance');

    // 현재 탭 새로고침
    refreshCurrentTab();

  } catch (e) {
    console.error('Monthly close error:', e);
    showToast('월 마감 처리 실패: ' + e.message, 'error');
  }
}

// ═══════════════════════════════════════
// MANAGERS CRUD
// ═══════════════════════════════════════
async function loadManagersList() {
  try {
    const el = document.getElementById('managersList');
    const empty = document.getElementById('managersEmpty');
    if (!managers.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = managers.map(m => `<div class="list-item">
      <div class="list-item-info"><div class="list-item-name">${m.name}</div><div class="list-item-detail">${m.phone || ''} ${m.memo ? '· ' + m.memo : ''}</div></div>
      <div class="list-item-actions">
        <button class="btn btn-sm btn-outline" onclick="editManager(${m.id})">✏️</button>
        <button class="btn btn-sm btn-danger" onclick="deleteManager(${m.id})">🗑️</button>
      </div></div>`).join('');
  } catch (e) { console.error('Managers list error:', e); }
}

function openManagerModal(id) {
  document.getElementById('managerEditId').value = '';
  document.getElementById('managerName').value = '';
  document.getElementById('managerPhone').value = '';
  document.getElementById('managerAddr').value = '';
  document.getElementById('managerMemo').value = '';
  document.getElementById('managerModalTitle').textContent = '매니저 추가';
  openModal('managerModal');
}

function editManager(id) {
  const m = managers.find(x => x.id === id);
  if (!m) return;
  document.getElementById('managerEditId').value = m.id;
  document.getElementById('managerName').value = m.name;
  document.getElementById('managerPhone').value = m.phone || '';
  document.getElementById('managerAddr').value = m.address || '';
  document.getElementById('managerMemo').value = m.memo || '';
  document.getElementById('managerModalTitle').textContent = '매니저 수정';
  openModal('managerModal');
}

async function saveManager() {
  const id = document.getElementById('managerEditId').value;
  const data = {
    name: document.getElementById('managerName').value,
    phone: document.getElementById('managerPhone').value,
    address: document.getElementById('managerAddr').value,
    memo: document.getElementById('managerMemo').value
  };
  if (!data.name) return showToast('이름을 입력해주세요.', 'error');
  try {
    if (id) await apiPut(`/api/managers/${id}`, data);
    else await apiPost('/api/managers', data);
    showToast(id ? '매니저가 수정되었습니다.' : '매니저가 추가되었습니다.', 'success');
    closeModal('managerModal');
    await loadManagers();
    loadManagersList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

async function deleteManager(id) {
  if (!confirm('매니저를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/managers/${id}`);
    showToast('매니저가 삭제되었습니다.', 'success');
    await loadManagers();
    loadManagersList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

// ═══════════════════════════════════════
// CLIENTS CRUD
// ═══════════════════════════════════════
async function loadClientsList() {
  try {
    const el = document.getElementById('clientsList');
    const empty = document.getElementById('clientsEmpty');
    if (!clients.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = clients.map(c => `<div class="list-item">
      <div class="list-item-info"><div class="list-item-name">${c.name}</div><div class="list-item-detail">${c.birth_date ? c.birth_date + ' (' + calcAge(c.birth_date) + '세)' : ''} ${c.gender || ''} ${c.phone ? '· ' + c.phone : ''} ${c.address ? '· ' + c.address : ''}</div></div>
      <div class="list-item-actions">
        <button class="btn btn-sm btn-outline" onclick="editClient(${c.id})">✏️</button>
        <button class="btn btn-sm btn-danger" onclick="deleteClient(${c.id})">🗑️</button>
      </div></div>`).join('');
  } catch (e) { console.error('Clients list error:', e); }
}

function openClientModal() {
  document.getElementById('clientEditId').value = '';
  document.getElementById('clientName').value = '';
  document.getElementById('clientBirthDate').value = '';
  document.getElementById('clientGender').value = '';
  document.getElementById('clientAddress').value = '';
  document.getElementById('clientPhone').value = '';
  document.getElementById('clientMemo').value = '';
  document.getElementById('clientModalTitle').textContent = '대상자 추가';
  openModal('clientModal');
}

function editClient(id) {
  const c = clients.find(x => x.id === id);
  if (!c) return;
  document.getElementById('clientEditId').value = c.id;
  document.getElementById('clientName').value = c.name;
  document.getElementById('clientBirthDate').value = c.birth_date || '';
  document.getElementById('clientGender').value = c.gender || '';
  document.getElementById('clientAddress').value = c.address || '';
  document.getElementById('clientPhone').value = c.phone || '';
  document.getElementById('clientMemo').value = c.memo || '';
  document.getElementById('clientModalTitle').textContent = '대상자 수정';
  openModal('clientModal');
}

async function saveClient() {
  const id = document.getElementById('clientEditId').value;
  const data = {
    name: document.getElementById('clientName').value,
    birth_date: document.getElementById('clientBirthDate').value,
    gender: document.getElementById('clientGender').value,
    address: document.getElementById('clientAddress').value,
    phone: document.getElementById('clientPhone').value,
    memo: document.getElementById('clientMemo').value
  };
  if (!data.name) return showToast('이름을 입력해주세요.', 'error');
  try {
    if (id) await apiPut(`/api/clients/${id}`, data);
    else await apiPost('/api/clients', data);
    showToast(id ? '대상자가 수정되었습니다.' : '대상자가 추가되었습니다.', 'success');
    closeModal('clientModal');
    await loadClients();
    loadClientsList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

async function deleteClient(id) {
  if (!confirm('대상자를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/clients/${id}`);
    showToast('대상자가 삭제되었습니다.', 'success');
    await loadClients();
    loadClientsList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

// ═══════════════════════════════════════
// SETTINGS
// ═══════════════════════════════════════
async function saveSettings() {
  const data = {
    hourly_wage: document.getElementById('settingWage').value,
    daily_transport: document.getElementById('settingTransport').value,
    provider_name: document.getElementById('settingProvName')?.value || '',
    provider_rep: document.getElementById('settingProvRep')?.value || '',
    provider_contact: document.getElementById('settingProvContact')?.value || '',
    provider_phone: document.getElementById('settingProvPhone')?.value || '',
    provider_address: document.getElementById('settingProvAddress')?.value || '',
    provider_biz_no: document.getElementById('settingProvBizNo')?.value || '',
    claimant_title: document.getElementById('settingClaimantTitle')?.value || '',
    claimant_name: document.getElementById('settingClaimantName')?.value || ''
  };
  try {
    await apiPut('/api/settings', data);
    showToast('설정이 저장되었습니다.', 'success');
  } catch (e) { showToast('설정 저장 실패', 'error'); }
}

// ═══════════════════════════════════════
// DAILY FORM (산청군 통합돌봄 일일 결과등록)
// ═══════════════════════════════════════
let dfSignCtx = null;
let dfSigning = false;

function dfInitSign() {
  const canvas = document.getElementById('dfSignCanvas');
  if (!canvas) return;
  dfSignCtx = canvas.getContext('2d');
  dfSignCtx.strokeStyle = '#202124';
  dfSignCtx.lineWidth = 2;
  dfSignCtx.lineCap = 'round';
  const getPos = (e) => {
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches ? e.touches[0] : e;
    return { x: touch.clientX - rect.left, y: touch.clientY - rect.top };
  };
  const start = e => { e.preventDefault(); dfSigning = true; const p = getPos(e); dfSignCtx.beginPath(); dfSignCtx.moveTo(p.x, p.y); };
  const move = e => { if (!dfSigning) return; e.preventDefault(); const p = getPos(e); dfSignCtx.lineTo(p.x, p.y); dfSignCtx.stroke(); };
  const end = () => { dfSigning = false; };
  canvas.addEventListener('mousedown', start);
  canvas.addEventListener('mousemove', move);
  canvas.addEventListener('mouseup', end);
  canvas.addEventListener('mouseleave', end);
  canvas.addEventListener('touchstart', start, { passive: false });
  canvas.addEventListener('touchmove', move, { passive: false });
  canvas.addEventListener('touchend', end);
}

function dfClearSign() {
  const canvas = document.getElementById('dfSignCanvas');
  if (canvas && dfSignCtx) dfSignCtx.clearRect(0, 0, canvas.width, canvas.height);
  // 서명 이미지도 초기화
  const img = document.getElementById('dfClientSignImg');
  if (img) { img.src = ''; img.style.display = 'none'; }
}

function dfAutoFill() {
  const mid = (document.getElementById('dfManager') || document.getElementById('clockManager')).value;
  const m = managers.find(x => x.id == mid);
  if (m) {
    document.getElementById('dfStaffName').value = m.name;
    document.getElementById('dfStaffPhone').value = m.phone || '';
    document.getElementById('dfReporterName').value = m.name;
  }
}

function dfAutoFillClient() {
  const cid = (document.getElementById('dfClient') || document.getElementById('clockClient')).value;
  const c = clients.find(x => x.id == cid);
  if (c) {
    document.getElementById('dfUserName').value = c.name;
    document.getElementById('dfUserBirth').value = c.birth_date || '';
    document.getElementById('dfUserAge').value = calcAge(c.birth_date);
    document.getElementById('dfUserAddr').value = c.address || '';
    const genderRadios = document.querySelectorAll('input[name="dfGender"]');
    genderRadios.forEach(r => r.checked = r.value === c.gender);
    document.getElementById('dfSignName').value = c.name;
  }
}



function dfShowClientSign(signPath) {
  // 실시간 캔버스 서명 사용 - 별도 이미지 자동 표시 없음
}

function dfHideClientSign() {
  const img = document.getElementById('dfClientSignImg');
  const canvas = document.getElementById('dfSignCanvas');
  if (img) { img.style.display = 'none'; img.src = ''; }
  if (canvas) canvas.style.display = '';
}

function dfToggleChange() {
  const val = document.querySelector('input[name="dfChange"]:checked')?.value;
  document.getElementById('dfChangeDetailRow').style.display = val === '변경됨' ? '' : 'none';
}

function dfToggleGoal() {
  const val = document.querySelector('input[name="dfGoal"]:checked')?.value;
  document.getElementById('dfStopReasonRow').style.display = val === '중단' ? '' : 'none';
}

function dfToggleStopType() {
  const val = document.querySelector('input[name="dfStopType"]:checked')?.value;
  document.getElementById('dfStopUserOpts').style.display = val === '이용자' ? 'inline' : 'none';
  document.getElementById('dfStopOrgOpts').style.display = val === '기관' ? 'inline' : 'none';
  document.getElementById('dfStopHarassNote').style.display = val === '기관' ? 'block' : 'none';
}

function dfCollectData() {
  const stopDetails = [];
  document.querySelectorAll('.df-stop-user:checked').forEach(c => stopDetails.push(c.value));
  document.querySelectorAll('.df-stop-org:checked').forEach(c => stopDetails.push(c.value));
  return {
    manager_id: (document.getElementById('dfManager') || document.getElementById('clockManager')).value || null,
    client_id: (document.getElementById('dfClient') || document.getElementById('clockClient')).value || null,
    staff_name: document.getElementById('dfStaffName').value,
    staff_phone: document.getElementById('dfStaffPhone').value,
    user_name: document.getElementById('dfUserName').value,
    user_birth: document.getElementById('dfUserBirth').value,
    user_age: document.getElementById('dfUserAge').value,
    user_gender: document.querySelector('input[name="dfGender"]:checked')?.value || '',
    user_address: document.getElementById('dfUserAddr').value,
    service_round: document.getElementById('dfRound').value,
    service_date: document.getElementById('dfServiceDate').value,
    time_start: document.getElementById('dfTimeStart').value,
    time_end: document.getElementById('dfTimeEnd').value,
    service_content: document.getElementById('dfServiceContent').value,
    change_type: document.querySelector('input[name="dfChange"]:checked')?.value || '변경없음',
    change_content: document.getElementById('dfChangeContent').value,
    change_reason: document.getElementById('dfChangeReason').value,
    goal_type: document.querySelector('input[name="dfGoal"]:checked')?.value || '',
    stop_type: document.querySelector('input[name="dfStopType"]:checked')?.value || '',
    stop_detail: stopDetails.join(', '),
    sign_name: document.getElementById('dfSignName').value,
    sign_data: document.getElementById('dfSignCanvas')?.toDataURL() || '',
    client_sign_img: (() => {
      const s = document.getElementById('dfClientSignImg')?.getAttribute('src') || '';
      // 전체 URL에서 /uploads/ 이하 경로만 추출하여 저장
      const idx = s.indexOf('/uploads/');
      if (idx !== -1) return s.substring(idx).split('?')[0];
      return s.split('?')[0];
    })(),
    submit_date: document.getElementById('dfSubmitDate').value,
    photo_path: '',
    custom_fields: JSON.stringify(collectCustomFields('df'))
  };
}

async function dfSave() {
  const data = dfCollectData();
  const editId = document.getElementById('dfEditId').value;
  try {
    if (editId) {
      await apiPut(`/api/daily-reports/${editId}`, data);
      showToast('일일결과가 수정되었습니다.', 'success');
    } else {
      await apiPost('/api/daily-reports', data);
      showToast('일일결과가 저장되었습니다! ✅', 'success');
    }
    invalidateCache(); // 전체 캐시 무효화
    _tabLoadTime[currentTab] = 0;
    await dfLoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

function dfReset() {
  document.getElementById('dfEditId').value = '';
  ['dfStaffName', 'dfStaffPhone', 'dfUserName', 'dfUserAddr', 'dfRound', 'dfServiceContent', 'dfChangeContent', 'dfChangeReason', 'dfSignName', 'dfReporterName'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('dfUserBirth').value = '';
  document.getElementById('dfUserAge').value = '';
  document.getElementById('dfServiceDate').value = todayStr();
  document.getElementById('dfTimeStart').value = '';
  document.getElementById('dfTimeEnd').value = '';
  document.getElementById('dfSubmitDate').value = todayStr();
  document.querySelectorAll('input[name="dfGender"]').forEach(r => r.checked = false);
  const changeRadio = document.querySelector('input[name="dfChange"][value="변경없음"]');
  if (changeRadio) changeRadio.checked = true;
  document.querySelectorAll('input[name="dfGoal"]').forEach(r => r.checked = false);
  document.querySelectorAll('input[name="dfStopType"]').forEach(r => r.checked = false);
  document.querySelectorAll('.df-stop-user, .df-stop-org').forEach(c => c.checked = false);
  document.getElementById('dfChangeDetailRow').style.display = 'none';
  document.getElementById('dfStopReasonRow').style.display = 'none';
  document.getElementById('dfStopUserOpts').style.display = 'none';
  document.getElementById('dfStopOrgOpts').style.display = 'none';
  document.getElementById('dfStopHarassNote').style.display = 'none';
  renderCustomFields('df', []);
  dfClearSign();
  dfHideClientSign();
}

function dfFillForm(report) {
  document.getElementById('dfEditId').value = report.id;
  const dfMgrEl = document.getElementById('dfManager') || document.getElementById('clockManager');
  const dfCliEl = document.getElementById('dfClient') || document.getElementById('clockClient');
  if (dfMgrEl) dfMgrEl.value = report.manager_id || '';
  if (dfCliEl) dfCliEl.value = report.client_id || '';
  document.getElementById('dfStaffName').value = report.staff_name || '';
  document.getElementById('dfStaffPhone').value = report.staff_phone || '';
  document.getElementById('dfUserName').value = report.user_name || '';
  // 생년월일/나이: 일지 데이터가 없으면 대상자 정보에서 가져오기
  const dfCli = clients.find(c => c.id == report.client_id);
  const dfBirth = report.user_birth || (dfCli ? dfCli.birth_date || '' : '');
  const dfAge = report.user_age || (dfBirth ? calcAge(dfBirth) : '');
  document.getElementById('dfUserBirth').value = dfBirth;
  document.getElementById('dfUserAge').value = dfAge;
  document.getElementById('dfUserAddr').value = report.user_address || (dfCli ? dfCli.address || '' : '');
  document.getElementById('dfRound').value = report.service_round || '';
  document.getElementById('dfServiceDate').value = report.service_date || '';
  document.getElementById('dfTimeStart').value = report.time_start || '';
  document.getElementById('dfTimeEnd').value = report.time_end || '';
  document.getElementById('dfServiceContent').value = report.service_content || '';
  document.getElementById('dfChangeContent').value = report.change_content || '';
  document.getElementById('dfChangeReason').value = report.change_reason || '';
  document.getElementById('dfSignName').value = report.sign_name || '';
  document.getElementById('dfReporterName').value = report.staff_name || '';
  document.getElementById('dfSubmitDate').value = report.submit_date || '';
  document.querySelectorAll('input[name="dfGender"]').forEach(r => r.checked = r.value === report.user_gender);
  const changeRadio = document.querySelector(`input[name="dfChange"][value="${report.change_type || '변경없음'}"]`);
  if (changeRadio) changeRadio.checked = true;
  dfToggleChange();
  if (report.goal_type) {
    const goalRadio = document.querySelector(`input[name="dfGoal"][value="${report.goal_type}"]`);
    if (goalRadio) goalRadio.checked = true;
  }
  dfToggleGoal();
  if (report.stop_type) {
    const stopRadio = document.querySelector(`input[name="dfStopType"][value="${report.stop_type}"]`);
    if (stopRadio) stopRadio.checked = true;
    dfToggleStopType();
  }
  if (report.stop_detail) {
    const details = report.stop_detail.split(', ');
    details.forEach(d => {
      document.querySelectorAll('.df-stop-user, .df-stop-org').forEach(c => { if (c.value === d) c.checked = true; });
    });
  }
  if (report.client_sign_img) {
    dfShowClientSign(report.client_sign_img);
  } else if (report.sign_data && dfSignCtx) {
    const img = new Image();
    img.onload = () => {
      dfSignCtx.clearRect(0, 0, 300, 80);
      dfSignCtx.drawImage(img, 0, 0);
    };
    img.src = report.sign_data;
  }
  try { renderCustomFields('df', JSON.parse(report.custom_fields || '[]')); } catch(e) {}
}

async function dfLoadList() {
  const date = document.getElementById('dfListDate').value;
  const month = document.getElementById('dfListMonth').value;
  try {
    let url = '/api/daily-reports?';
    if (date) url += `date=${date}&`;
    else if (month) url += `month=${month}&`;
    else url += `month=${currentMonthStr()}&`;
    const reports = await apiGet(url);
    // 목록은 항상 최신 데이터 사용 (캐시 미사용)
    const el = document.getElementById('dfSavedList');
    const empty = document.getElementById('dfSavedEmpty');
    if (!reports.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = reports.map(r => `<div class="saved-item" onclick="dfLoadReport(${r.id})">
      <div class="saved-item-info">
        <div class="saved-item-title">${r.user_name || '미입력'} - ${r.service_date || r.report_date}</div>
        <div class="saved-item-sub">제공인력: ${r.staff_name || '-'} | 회차: ${r.service_round || '-'}</div>
      </div>
      <div class="saved-item-actions">
        <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();dfDeleteReport(${r.id})">🗑️</button>
      </div>
    </div>`).join('');
  } catch (e) { console.error('DF list error:', e); }
}

function dfLoadListByMonth() {
  document.getElementById('dfListDate').value = '';
  dfLoadList();
}

async function dfLoadReport(id) {
  try {
    const report = await apiGet(`/api/daily-reports/${id}`);
    dfReset();
    dfFillForm(report);
    showToast('일일결과를 불러왔습니다.', 'success');
    document.getElementById('dailyFormPaper').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (e) { showToast('불러오기 실패', 'error'); }
}

// 근무기록에서 일지보기 클릭 시 - 해당 날짜의 사진도 함께 로드
async function viewReportWithPhotos(reportId, workDate) {
  // 탭 전환 시 loadTodayClock() 자동호출을 방지하기 위해 플래그 설정
  window._skipAutoLoadClock = true;
  switchTab('clock');
  window._skipAutoLoadClock = false;
  // 일지 로드
  await dfLoadReport(reportId);
  // 해당 날짜의 출퇴근 사진 로드
  await loadClockForDate(workDate);
}

// 특정 날짜의 출퇴근 기록+사진을 로드 (일지보기 연동용)
async function loadClockForDate(date) {
  try {
    const records = await apiGet(`/api/attendance?date=${date}`);
    const el = document.getElementById('todayClockList');
    const photoReport = document.getElementById('clockPhotoReport');
    const photoBody = document.getElementById('clockPhotoReportBody');
    if (!records.length) {
      el.innerHTML = `<div class="empty-state"><div class="icon">📋</div><p>${date} 근무 기록이 없습니다.</p></div>`;
      if (photoReport) photoReport.style.display = 'none';
      return;
    }
    el.innerHTML = `<div style="text-align:center;padding:4px;background:#e3f2fd;border-radius:6px;margin-bottom:8px;font-size:0.8rem;">📅 조회 날짜: <strong>${date}</strong></div>` +
      `<div class="table-wrapper"><table class="data-table"><thead><tr><th>매니저</th><th>대상자</th><th>출근</th><th>퇴근</th><th>시간</th></tr></thead><tbody>` +
      records.map(r => `<tr><td>${r.manager_name}</td><td>${r.client_name}</td><td>${formatTime(r.clock_in)}</td><td>${r.clock_out ? formatTime(r.clock_out) : '근무중'}</td><td>${(r.hours_worked || 0).toFixed(1)}h</td></tr>`).join('') +
      `</tbody></table></div>`;
    // 사진 보고용
    const hasPhotos = records.some(r => r.clock_in_photo || r.clock_out_photo);
    if (photoReport && photoBody && hasPhotos) {
      photoReport.style.display = '';
      photoBody.innerHTML = records.filter(r => r.clock_in_photo || r.clock_out_photo).map(r => {
        let html = `<div class="photo-report-card">`;
        html += `<div class="photo-report-header">`;
        html += `<span class="photo-report-names">${r.manager_name} → ${r.client_name}</span>`;
        html += `<span class="photo-report-date">${formatDate(r.work_date)}</span>`;
        html += `</div>`;
        html += `<div class="photo-report-grid">`;
        if (r.clock_in_photo) {
          html += `<div class="photo-report-item">`;
          html += `<div class="photo-report-label in">🟢 출근</div>`;
          html += `<div class="photo-with-time">`;
          html += `<img src="${r.clock_in_photo}" class="photo-in" onclick="viewPhoto('${r.clock_in_photo}')">`;
          html += `<div class="photo-time-overlay">📸 ${formatDateTime(r.clock_in)}</div>`;
          html += `</div></div>`;
        }
        if (r.clock_out_photo) {
          html += `<div class="photo-report-item">`;
          html += `<div class="photo-report-label out">🔴 퇴근</div>`;
          html += `<div class="photo-with-time">`;
          html += `<img src="${r.clock_out_photo}" class="photo-out" onclick="viewPhoto('${r.clock_out_photo}')">`;
          html += `<div class="photo-time-overlay">📸 ${r.clock_out ? formatDateTime(r.clock_out) : '-'}</div>`;
          html += `</div></div>`;
        }
        html += `</div></div>`;
        return html;
      }).join('');
    } else if (photoReport) {
      photoReport.style.display = 'none';
    }
  } catch (e) { console.error('loadClockForDate error:', e); }
}

async function dfDeleteReport(id) {
  if (!confirm('일일결과를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/daily-reports/${id}`);
    showToast('삭제되었습니다.', 'success');
    dfLoadList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

function dfPrint() {
  const sec = document.getElementById('sec-clock');
  const paper = document.getElementById('dailyFormPaper');
  const photoReport = document.getElementById('clockPhotoReport');

  // 출퇴근 사진 보고서를 일지 바로 뒤에 삽입 (인쇄 시 같은 페이지)
  if (photoReport && paper && photoReport.style.display !== 'none') {
    paper.parentNode.insertBefore(photoReport, paper.nextSibling);
  }

  // ★ 인쇄 전: 서명 이미지 강제 표시 + 캔버스 완전 숨김
  const signImg = document.getElementById('dfClientSignImg');
  const signCanvas = document.getElementById('dfSignCanvas');
  const signBtn = document.querySelector('#dfSignArea .btn');
  if (signCanvas) signCanvas.style.display = 'none';
  if (signBtn) signBtn.style.display = 'none';

  // ★ 캔버스 서명 데이터를 이미지로 변환하여 인쇄
  if (signCanvas && signImg) {
    const canvasData = signCanvas.toDataURL();
    if (canvasData && canvasData !== 'data:,') {
      signImg.src = canvasData;
      signImg.style.cssText = 'display:block !important;visibility:visible !important;opacity:1 !important;max-height:60px;max-width:200px;position:static !important;';
    }
  }

  sec.classList.add('print-active');

  // 인쇄 실행
  setTimeout(() => {
    window.print();
    setTimeout(() => {
      sec.classList.remove('print-active');
      if (signBtn) signBtn.style.display = '';
    }, 500);
  }, 150);
}

// ═══════════════════════════════════════
// INVOICE (대상자용 청구서)
// ═══════════════════════════════════════

// ─── Provider Info Pre-fill ───
function invFillProviderDefaults() {
  const el = (id) => document.getElementById(id);
  if (el('invProvName') && !el('invProvName').value) el('invProvName').value = settings.provider_name || '산청인애노인통합지원센터';
  if (el('invProvRep') && !el('invProvRep').value) el('invProvRep').value = settings.provider_rep || '김일득';
  if (el('invProvPhone') && !el('invProvPhone').value) el('invProvPhone').value = settings.provider_phone || '055-973-8642';
  if (el('invProvAddr') && !el('invProvAddr').value) el('invProvAddr').value = settings.provider_address || '산청군 산청읍 산청대로 1381번길 17';
  if (el('invProvBizNo') && !el('invProvBizNo').value) el('invProvBizNo').value = settings.provider_biz_no || '726-82-00506';
  if (el('invProvStaff') && !el('invProvStaff').value) el('invProvStaff').value = settings.provider_contact || '반철영';
  if (el('invClaimantTitle') && !el('invClaimantTitle').value) el('invClaimantTitle').value = settings.claimant_title || '센터장';
  if (el('invClaimantName') && !el('invClaimantName').value) el('invClaimantName').value = settings.claimant_name || '반철영';
}

function invAutoFill() {
  const mid = document.getElementById('invManager').value;
  const m = managers.find(x => x.id == mid);
  if (m) {
    // Don't overwrite provider phone with manager phone
  }
  // Pre-fill provider defaults
  invFillProviderDefaults();
}

function invAutoFillClient() {
  const cid = document.getElementById('invClient').value;
  const c = clients.find(x => x.id == cid);
  if (c) {
    document.getElementById('invClientName').value = c.name;
    document.getElementById('invClientBirth').value = c.birth_date || '';
    document.getElementById('invClientAddr').value = c.address || '';
    document.getElementById('invClientPhone').value = c.phone || '';
    const genderRadios = document.querySelectorAll('input[name="invGender"]');
    genderRadios.forEach(r => r.checked = r.value === c.gender);
  }
}

// ─── Income Tier & Auto-Calculation ───
const INCOME_TIERS = {
  basic:  { rate: 0,    label: '기초수급자 (면제)' },
  low:    { rate: 0.15, label: '차상위 (15%)' },
  high:   { rate: 1.00, label: '일반 (100%)' }
};

// Checkbox-based income tier: only one can be checked at a time
function invIncomeTierCheck(clicked) {
  document.querySelectorAll('input[name="invIncomeTierCb"]').forEach(cb => {
    if (cb !== clicked) cb.checked = false;
  });
  // 양식 내부 체크박스도 동기화
  document.querySelectorAll('input[name="invIncomeTierCbInner"]').forEach(cb => {
    cb.checked = cb.value === (clicked.checked ? clicked.value : '');
  });
  invCalcByTier();
}

function invIncomeTierCheckInner(clicked) {
  // 양식 내부 소득구분 체크박스 클릭 시: 다른 항목 해제 후 동기화
  document.querySelectorAll('input[name="invIncomeTierCbInner"]').forEach(cb => {
    if (cb !== clicked) cb.checked = false;
  });
  // 상단 체크박스도 동기화
  document.querySelectorAll('input[name="invIncomeTierCb"]').forEach(cb => {
    cb.checked = cb.value === (clicked.checked ? clicked.value : '');
  });
  invCalcByTier();
  // 소득구분 텍스트 즉시 업데이트
  const tierVal = clicked.checked ? clicked.value : '';
  if (tierVal && INCOME_TIERS[tierVal]) {
    document.getElementById('invIncomeTierText').value = INCOME_TIERS[tierVal].label;
  } else {
    document.getElementById('invIncomeTierText').value = '';
  }
  invSyncMirrors();
}

// Grade dropdown logic
function invUpdateGrade() {
  const gradeType = document.getElementById('invGradeType').value;
  const disGrade = document.getElementById('invDisabilityGrade');
  const disType = document.getElementById('invDisabilityType');
  const careGrade = document.getElementById('invCareGrade');
  const hiddenGrade = document.getElementById('invClientGrade');

  // Show/hide relevant dropdowns
  disGrade.style.display = gradeType === 'disability' ? '' : 'none';
  disType.style.display = gradeType === 'disability' ? '' : 'none';
  careGrade.style.display = gradeType === 'care' ? '' : 'none';

  // Build combined grade string
  let parts = [];
  if (gradeType === 'disability') {
    if (disGrade.value) parts.push(disGrade.value);
    if (disType.value) parts.push(disType.value);
  } else if (gradeType === 'care') {
    if (careGrade.value) parts.push('장기요양 ' + careGrade.value);
  } else if (gradeType === 'etc') {
    parts.push('등외자');
  }
  hiddenGrade.value = parts.join(' / ');
  // Sync mirrors
  invSyncMirrors();
}

function invCalcByTier() {
  const checked = document.querySelector('input[name="invIncomeTierCb"]:checked');
  const tierVal = checked ? checked.value : null;
  if (!tierVal || !INCOME_TIERS[tierVal]) {
    document.getElementById('invBurdenRate').value = '';
    document.getElementById('invIncomeTierText').value = '';
    invCalcTotal();
    return;
  }
  const tier = INCOME_TIERS[tierVal];
  const rateText = tierVal === 'basic' ? '0% (면제)' : tierVal === 'high' ? '100% (전액)' : `${Math.round(tier.rate * 100)}%`;
  document.getElementById('invBurdenRate').value = rateText;
  document.getElementById('invIncomeTierText').value = tier.label;
  invCalcTotal();
}

function invCalcFees() {
  const hours = parseFloat(document.getElementById('invTotalHours').value) || 0;
  const wage = parseFloat(settings.hourly_wage || 13500);
  document.getElementById('invBasicFee').value = Math.round(hours * wage);
  invCalcTotal();
}

function invCalcTotal() {
  const basic = parseFloat(document.getElementById('invBasicFee').value) || 0;
  const surcharge = parseFloat(document.getElementById('invSurchargeFee').value) || 0;
  const totalService = basic + surcharge;

  // Get burden rate from income tier (checkbox)
  const checkedTier = document.querySelector('input[name="invIncomeTierCb"]:checked');
  const tierVal = checkedTier ? checkedTier.value : null;
  let burdenRate = 0;
  if (tierVal && INCOME_TIERS[tierVal]) {
    burdenRate = INCOME_TIERS[tierVal].rate;
  }

  const personalBurden = Math.round(totalService * burdenRate);
  const govSupport = totalService - personalBurden;

  document.getElementById('invPersonalBurden').value = personalBurden;
  document.getElementById('invGovSupport').value = govSupport;
  document.getElementById('invClaimAmount').value = totalService;

  // Sync mirrors after calculation
  invSyncMirrors();
}

// ─── Form Type (User only - provider form removed) ───
function invSwitchForm() {
  // Provider form removed - always show user form
  const userPaper = document.getElementById('invoicePaperUser');
  if (userPaper) userPaper.style.display = 'block';
}

// ─── Mirror Sync (no-op after provider form removal) ───
function invSyncMirrors() {
  // Provider form removed - mirror sync no longer needed
}

function invCollectData() {
  return {
    invoice_date: document.getElementById('invDate').value,
    invoice_month: document.getElementById('invMonthField').value,
    provider_name: document.getElementById('invProvName').value,
    provider_rep: document.getElementById('invProvRep').value,
    provider_phone: document.getElementById('invProvPhone').value,
    provider_address: document.getElementById('invProvAddr').value,
    client_name: document.getElementById('invClientName').value,
    client_birth: document.getElementById('invClientBirth').value,
    client_gender: document.querySelector('input[name="invGender"]:checked')?.value || '',
    client_address: document.getElementById('invClientAddr').value,
    client_phone: document.getElementById('invClientPhone').value,
    client_grade: document.getElementById('invClientGrade').value,
    disability_grade: document.getElementById('invDisabilityGrade').value,
    disability_type: document.getElementById('invDisabilityType').value,
    care_grade: document.getElementById('invCareGrade').value,
    service_type: document.getElementById('invServiceType').value,
    service_dates: document.getElementById('invServiceDates').value,
    total_hours: parseFloat(document.getElementById('invTotalHours').value) || 0,
    basic_fee: parseFloat(document.getElementById('invBasicFee').value) || 0,
    surcharge_fee: parseFloat(document.getElementById('invSurchargeFee').value) || 0,
    personal_burden: parseFloat(document.getElementById('invPersonalBurden').value) || 0,
    claim_amount: parseFloat(document.getElementById('invClaimAmount').value) || 0,
    gov_support: parseFloat(document.getElementById('invGovSupport').value) || 0,
    work_days: parseInt(document.getElementById('invWorkDays').value) || 0,
    bank_name: document.getElementById('invBankName').value,
    account_number: document.getElementById('invAccountNo').value,
    account_holder: document.getElementById('invAccountHolder').value,
    notes: document.getElementById('invNotes').value,
    photo_path: document.getElementById('invPhotoPath').value,
    custom_fields: JSON.stringify(collectCustomFields('inv')),
    manager_id: document.getElementById('invManager').value || null,
    client_id: document.getElementById('invClient').value || null,
    auto_generated: 0,
    income_tier: document.querySelector('input[name="invIncomeTierCb"]:checked')?.value || '',
    burden_rate: INCOME_TIERS[document.querySelector('input[name="invIncomeTierCb"]:checked')?.value]?.rate || 0,
    biz_no: document.getElementById('invProvBizNo').value,
    provider_staff: document.getElementById('invProvStaff').value,
    claimant_title: document.getElementById('invClaimantTitle').value,
    claimant_name: document.getElementById('invClaimantName').value,
    form_type: 'user'
  };
}

async function invSave() {
  const data = invCollectData();
  const editId = document.getElementById('invEditId').value;
  const photoInput = document.getElementById('invPhotoInput');
  if (photoInput && photoInput.files && photoInput.files[0]) {
    try {
      data.photo_path = await uploadPhoto(photoInput);
      // 사진 업로드 후 즉시 양식에 표시
      invShowPhotoInForm(data.photo_path);
      document.getElementById('invPhotoPath').value = data.photo_path;
    } catch (e) { showToast('사진 업로드 실패', 'error'); }
  }
  try {
    if (editId) {
      await apiPut(`/api/invoices/${editId}`, data);
      showToast('청구서가 수정되었습니다.', 'success');
    } else {
      await apiPost('/api/invoices', data);
      showToast('청구서가 저장되었습니다! ✅', 'success');
    }
    invLoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

// 청구서 양식에 사진 실시간 표시
function invShowPhotoInForm(photoPath) {
  if (!photoPath) return;
  const invPhotoDisplay = document.getElementById('invPhotoDisplay');
  if (invPhotoDisplay) invPhotoDisplay.style.display = 'block';
  const invPhotoImg = document.getElementById('invPhotoImg');
  if (invPhotoImg) invPhotoImg.src = photoPath;
  const invPhotoPrintArea = document.getElementById('invPhotoPrintArea');
  if (invPhotoPrintArea) invPhotoPrintArea.style.display = 'block';
  const invPhotoPrintImg = document.getElementById('invPhotoPrintImg');
  if (invPhotoPrintImg) invPhotoPrintImg.src = photoPath;
}

function invReset() {
  document.getElementById('invEditId').value = '';
  document.getElementById('invPhotoPath').value = '';
  ['invProvName', 'invProvRep', 'invProvPhone', 'invProvAddr', 'invProvBizNo', 'invProvStaff', 'invClientName', 'invClientBirth', 'invClientAddr', 'invClientPhone', 'invClientGrade', 'invIncomeTierText', 'invServiceDates', 'invBankName', 'invAccountNo', 'invAccountHolder', 'invNotes', 'invClaimantTitle', 'invClaimantName', 'invBurdenRate'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('invTotalHours').value = '';
  document.getElementById('invBasicFee').value = '';
  document.getElementById('invSurchargeFee').value = '';
  document.getElementById('invPersonalBurden').value = '';
  document.getElementById('invClaimAmount').value = '';
  document.getElementById('invGovSupport').value = '';
  const invWorkDays = document.getElementById('invWorkDays');
  if (invWorkDays) invWorkDays.value = '';
  document.getElementById('invServiceType').value = '가사지원';
  document.querySelectorAll('input[name="invGender"]').forEach(r => r.checked = false);
  document.querySelectorAll('input[name="invIncomeTierCb"]').forEach(cb => cb.checked = false);
  document.querySelectorAll('input[name="invIncomeTierCbInner"]').forEach(cb => cb.checked = false);
  // Reset grade dropdowns
  document.getElementById('invGradeType').value = '';
  document.getElementById('invDisabilityGrade').value = '';
  document.getElementById('invDisabilityGrade').style.display = 'none';
  document.getElementById('invDisabilityType').value = '';
  document.getElementById('invDisabilityType').style.display = 'none';
  document.getElementById('invCareGrade').value = '';
  document.getElementById('invCareGrade').style.display = 'none';
  // Ensure user form visible
  invSwitchForm();
  document.getElementById('invDate').value = todayStr();
  document.getElementById('invMonthField').value = currentMonthStr();
  const invPhotoInput = document.getElementById('invPhotoInput');
  if (invPhotoInput) invPhotoInput.value = '';
  const invPhotoPreview = document.getElementById('invPhotoPreview');
  if (invPhotoPreview) invPhotoPreview.src = '';
  const invPhotoArea = document.getElementById('invPhotoArea');
  if (invPhotoArea) invPhotoArea.classList.remove('has-photo');
  const invPhotoDisplay = document.getElementById('invPhotoDisplay');
  if (invPhotoDisplay) invPhotoDisplay.style.display = 'none';
  const invPhotoPrintArea = document.getElementById('invPhotoPrintArea');
  if (invPhotoPrintArea) invPhotoPrintArea.style.display = 'none';

  renderCustomFields('inv', []);
  // Pre-fill provider defaults on reset
  invFillProviderDefaults();
}

function invFillForm(inv) {
  document.getElementById('invEditId').value = inv.id;
  document.getElementById('invManager').value = inv.manager_id || '';
  document.getElementById('invClient').value = inv.client_id || '';
  document.getElementById('invDate').value = inv.invoice_date || '';
  document.getElementById('invMonthField').value = inv.invoice_month || '';
  document.getElementById('invProvName').value = inv.provider_name || '';
  document.getElementById('invProvRep').value = inv.provider_rep || '';
  document.getElementById('invProvPhone').value = inv.provider_phone || '';
  document.getElementById('invProvAddr').value = inv.provider_address || '';
  const invProvBizNo = document.getElementById('invProvBizNo');
  if (invProvBizNo) invProvBizNo.value = inv.biz_no || '';
  const invProvStaff = document.getElementById('invProvStaff');
  if (invProvStaff) invProvStaff.value = inv.provider_staff || '';
  document.getElementById('invClientName').value = inv.client_name || '';
  document.getElementById('invClientBirth').value = inv.client_birth || '';
  document.getElementById('invClientAddr').value = inv.client_address || '';
  document.getElementById('invClientPhone').value = inv.client_phone || '';
  document.getElementById('invClientGrade').value = inv.client_grade || '';
  // Restore grade dropdowns
  if (inv.disability_grade || inv.disability_type) {
    document.getElementById('invGradeType').value = 'disability';
    document.getElementById('invDisabilityGrade').value = inv.disability_grade || '';
    document.getElementById('invDisabilityGrade').style.display = '';
    document.getElementById('invDisabilityType').value = inv.disability_type || '';
    document.getElementById('invDisabilityType').style.display = '';
    document.getElementById('invCareGrade').style.display = 'none';
  } else if (inv.care_grade) {
    document.getElementById('invGradeType').value = 'care';
    document.getElementById('invCareGrade').value = inv.care_grade || '';
    document.getElementById('invCareGrade').style.display = '';
    document.getElementById('invDisabilityGrade').style.display = 'none';
    document.getElementById('invDisabilityType').style.display = 'none';
  } else if (inv.client_grade === '등외자') {
    document.getElementById('invGradeType').value = 'etc';
    document.getElementById('invDisabilityGrade').style.display = 'none';
    document.getElementById('invDisabilityType').style.display = 'none';
    document.getElementById('invCareGrade').style.display = 'none';
  }
  document.getElementById('invServiceType').value = inv.service_type || '가사지원';
  document.getElementById('invServiceDates').value = inv.service_dates || '';
  document.getElementById('invTotalHours').value = inv.total_hours || '';
  document.getElementById('invBasicFee').value = inv.basic_fee || '';
  document.getElementById('invSurchargeFee').value = inv.surcharge_fee || '';
  document.getElementById('invPersonalBurden').value = inv.personal_burden || '';
  document.getElementById('invClaimAmount').value = inv.claim_amount || '';
  const invGovSupport = document.getElementById('invGovSupport');
  if (invGovSupport) invGovSupport.value = inv.gov_support || '';
  const invWorkDays = document.getElementById('invWorkDays');
  if (invWorkDays) invWorkDays.value = inv.work_days || '';
  document.getElementById('invBankName').value = inv.bank_name || '';
  document.getElementById('invAccountNo').value = inv.account_number || '';
  document.getElementById('invAccountHolder').value = inv.account_holder || '';
  document.getElementById('invNotes').value = inv.notes || '';
  document.getElementById('invPhotoPath').value = inv.photo_path || '';
  const invClaimantTitle = document.getElementById('invClaimantTitle');
  if (invClaimantTitle) invClaimantTitle.value = inv.claimant_title || '';
  const invClaimantName = document.getElementById('invClaimantName');
  if (invClaimantName) invClaimantName.value = inv.claimant_name || '';
  document.querySelectorAll('input[name="invGender"]').forEach(r => r.checked = r.value === inv.client_gender);
  // Income tier (checkbox) - 상단 + 양식 내부 동기화
  document.querySelectorAll('input[name="invIncomeTierCb"]').forEach(cb => cb.checked = false);
  document.querySelectorAll('input[name="invIncomeTierCbInner"]').forEach(cb => cb.checked = false);
  if (inv.income_tier) {
    const tierCb = document.querySelector(`input[name="invIncomeTierCb"][value="${inv.income_tier}"]`);
    if (tierCb) tierCb.checked = true;
    const tierCbInner = document.querySelector(`input[name="invIncomeTierCbInner"][value="${inv.income_tier}"]`);
    if (tierCbInner) tierCbInner.checked = true;
    invCalcByTier();
  }
  // Burden rate display
  if (inv.burden_rate !== undefined && inv.burden_rate !== null) {
    const ratePercent = Math.round(inv.burden_rate * 100);
    const rateText = ratePercent === 0 ? '0% (면제)' : ratePercent === 100 ? '100% (전액)' : `${ratePercent}%`;
    document.getElementById('invBurdenRate').value = rateText;
  }
  // Income tier text
  if (inv.income_tier && INCOME_TIERS[inv.income_tier]) {
    document.getElementById('invIncomeTierText').value = INCOME_TIERS[inv.income_tier].label;
  }
  if (inv.photo_path) {
    const invPhotoDisplay = document.getElementById('invPhotoDisplay');
    if (invPhotoDisplay) invPhotoDisplay.style.display = 'block';
    const invPhotoImg = document.getElementById('invPhotoImg');
    if (invPhotoImg) invPhotoImg.src = inv.photo_path;
    const invPhotoPrintArea = document.getElementById('invPhotoPrintArea');
    if (invPhotoPrintArea) invPhotoPrintArea.style.display = 'block';
    const invPhotoPrintImg = document.getElementById('invPhotoPrintImg');
    if (invPhotoPrintImg) invPhotoPrintImg.src = inv.photo_path;
  }
  try { renderCustomFields('inv', JSON.parse(inv.custom_fields || '[]')); } catch(e) {}
  // Pre-fill missing provider details
  invFillProviderDefaults();

}

async function invLoadList() {
  const month = document.getElementById('invMonth').value || currentMonthStr();
  try {
    const list = await apiGet(`/api/invoices?month=${month}`);
    const el = document.getElementById('invSavedList');
    const empty = document.getElementById('invSavedEmpty');
    if (!list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(inv => `<div class="saved-item" onclick="invLoadItem(${inv.id})">
      <div class="saved-item-info">
        <div class="saved-item-title">${inv.client_name || '미입력'} - ${inv.invoice_month || inv.invoice_date}</div>
        <div class="saved-item-sub">${inv.service_type || '-'} | ${(inv.total_hours || 0).toFixed(1)}h | 청구: ${formatMoney(inv.claim_amount)}</div>
      </div>
      <span class="saved-item-badge ${inv.auto_generated ? 'auto' : ''}">${inv.auto_generated ? '자동생성' : '수동'}</span>
      <div class="saved-item-actions">
        <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();invDeleteItem(${inv.id})">🗑️</button>
      </div>
    </div>`).join('');
  } catch (e) { console.error('Invoice list error:', e); }
}

async function invLoadItem(id) {
  try {
    const inv = await apiGet(`/api/invoices/${id}`);
    invFillForm(inv);
    showToast('청구서를 불러왔습니다.', 'success');
    const target = document.getElementById('invoicePaperUser');
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  } catch (e) { showToast('불러오기 실패', 'error'); }
}

async function invDeleteItem(id) {
  if (!confirm('청구서를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/invoices/${id}`);
    showToast('삭제되었습니다.', 'success');
    invLoadList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

async function invAutoGenerate() {
  const managerId = document.getElementById('invManager').value;
  const clientId = document.getElementById('invClient').value;
  const month = document.getElementById('invMonth').value || currentMonthStr();
  if (!managerId || !clientId) return showToast('매니저와 대상자를 선택해주세요.', 'error');
  try {
    const inv = await apiPost('/api/invoices/auto-generate', { month, manager_id: parseInt(managerId), client_id: parseInt(clientId) });
    invFillForm(inv);
    showToast('청구서가 자동 생성되었습니다! ⚡', 'success');
    invLoadList();
  } catch (e) { showToast('자동 생성 실패: ' + e.message, 'error'); }
}

function invPrint() {
  const sec = document.getElementById('sec-invoice');
  const userPaper = document.getElementById('invoicePaperUser');
  if (userPaper) userPaper.style.display = 'block';
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// PAYROLL (급여대장)
// ═══════════════════════════════════════

async function payrollLoad() {
  const month = document.getElementById('payrollMonth').value || currentMonthStr();
  const managerId = document.getElementById('payrollManager').value;
  document.getElementById('payrollMonth').value = month;

  try {
    let url = `/api/payroll/monthly?month=${month}`;
    if (managerId) url += `&manager_id=${managerId}`;
    const data = await apiGet(url);

    // Fill org info on print form
    document.getElementById('payrollOrgName').textContent = settings.provider_name || settings.org_name || '-';
    document.getElementById('payrollOrgRep').textContent = settings.provider_rep || settings.org_rep || '-';
    document.getElementById('payrollOrgBizNo').textContent = settings.provider_biz_no || settings.org_biz_no || '-';
    document.getElementById('payrollOrgPhone').textContent = settings.provider_phone || settings.org_phone || '-';
    document.getElementById('payrollBottomOrg').textContent = settings.provider_name || settings.org_name || '-';
    document.getElementById('payrollBottomRep').textContent = settings.provider_rep || settings.org_rep || '-';

    const [yr, mo] = month.split('-');
    document.getElementById('payrollPaperMonth').textContent = `${yr}년 ${parseInt(mo)}월 급여대장`;
    document.getElementById('payrollDateLine').textContent = `${yr}년 ${parseInt(mo)}월`;

    const summaries = data.summaries || [];
    const hourlyWage = parseInt(settings.hourly_wage) || 13500;
    const dailyTransport = parseInt(settings.daily_transport) || 9000;

    // Build summary table
    let grandTotalPay = 0, grandTotalTransport = 0, grandTotal = 0;
    let tableHtml = `<table class="df-table" style="margin-top:2px;">
      <thead>
        <tr><th colspan="8" class="df-section-header">■ 급여 내역</th></tr>
        <tr style="background:#f5f5f5;">
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">No</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">성명</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">근무일수</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">총 시간</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">시급(원)</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">근무수당</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">교통비</th>
          <th style="padding:3px 4px;border:1px solid #333;text-align:center;">지급합계</th>
        </tr>
      </thead><tbody>`;

    summaries.forEach((s, i) => {
      const rate = s.hourly_rate || hourlyWage;
      const tFee = s.transport_fee || dailyTransport;
      const workPay = Math.round(s.total_hours * rate);
      const transportPay = s.work_days * tFee;
      const total = workPay + transportPay;
      grandTotalPay += workPay;
      grandTotalTransport += transportPay;
      grandTotal += total;
      tableHtml += `<tr>
        <td style="padding:3px 4px;border:1px solid #333;text-align:center;">${i + 1}</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:center;font-weight:600;">${s.manager_name || '-'}</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:center;">${s.work_days}일</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:center;">${s.total_hours.toFixed(1)}h</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:right;">${rate.toLocaleString()}</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:right;">${workPay.toLocaleString()}원</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:right;">${transportPay.toLocaleString()}원</td>
        <td style="padding:3px 4px;border:1px solid #333;text-align:right;font-weight:700;">${total.toLocaleString()}원</td>
      </tr>`;
    });

    tableHtml += `<tr style="background:#e3f2fd;font-weight:700;">
      <td colspan="5" style="padding:3px 4px;border:1px solid #333;text-align:center;">합 계</td>
      <td style="padding:3px 4px;border:1px solid #333;text-align:right;">${grandTotalPay.toLocaleString()}원</td>
      <td style="padding:3px 4px;border:1px solid #333;text-align:right;">${grandTotalTransport.toLocaleString()}원</td>
      <td style="padding:3px 4px;border:1px solid #333;text-align:right;font-weight:700;">${grandTotal.toLocaleString()}원</td>
    </tr></tbody></table>`;

    document.getElementById('payrollTableArea').innerHTML = tableHtml;
    document.getElementById('payrollPaper').style.display = 'block';

    // Build individual payslips
    const details = data.details || {};
    let detailHtml = '';
    summaries.forEach(s => {
      const rate = s.hourly_rate || hourlyWage;
      const tFee = s.transport_fee || dailyTransport;
      const workPay = Math.round(s.total_hours * rate);
      const transportPay = s.work_days * tFee;
      const total = workPay + transportPay;
      const records = details[s.manager_id] || [];

      detailHtml += `<div class="daily-form-paper" style="margin-top:24px;page-break-before:always;">
        <div class="df-title-area">
          <div class="df-main-title">급 여 명 세 서</div>
          <div class="df-sub-notice">${yr}년 ${parseInt(mo)}월</div>
        </div>
        <table class="df-table">
          <thead><tr><th colspan="4" class="df-section-header">■ 매니저 정보</th></tr></thead>
          <tbody>
            <tr><td class="df-label">성명</td><td>${s.manager_name || '-'}</td><td class="df-label">시급</td><td>${rate.toLocaleString()}원</td></tr>
            <tr><td class="df-label">은행</td><td>${s.bank_name || '-'}</td><td class="df-label">계좌번호</td><td>${s.account_no || '-'}</td></tr>
            <tr><td class="df-label">예금주</td><td colspan="3">${s.account_holder || '-'}</td></tr>
          </tbody>
        </table>
        <table class="df-table" style="margin-top:8px;">
          <thead>
            <tr><th colspan="6" class="df-section-header">■ 근무 내역</th></tr>
            <tr style="background:#f5f5f5;">
              <th style="padding:6px;border:1px solid #333;text-align:center;">날짜</th>
              <th style="padding:6px;border:1px solid #333;text-align:center;">대상자</th>
              <th style="padding:6px;border:1px solid #333;text-align:center;">출근</th>
              <th style="padding:6px;border:1px solid #333;text-align:center;">퇴근</th>
              <th style="padding:6px;border:1px solid #333;text-align:center;">시간</th>
              <th style="padding:6px;border:1px solid #333;text-align:center;">수당</th>
            </tr>
          </thead><tbody>`;

      records.forEach(r => {
        const h = r.hours || 0;
        const pay = Math.round(h * rate);
        detailHtml += `<tr>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${r.date || '-'}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${r.client_name || '-'}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${r.clock_in || '-'}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${r.clock_out || '-'}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${h.toFixed(1)}h</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;">${pay.toLocaleString()}원</td>
        </tr>`;
      });

      detailHtml += `</tbody></table>
        <table class="df-table" style="margin-top:8px;">
          <thead><tr><th colspan="4" class="df-section-header">■ 지급 내역</th></tr></thead>
          <tbody>
            <tr><td class="df-label">근무수당</td><td style="text-align:right;">${workPay.toLocaleString()}원</td><td class="df-label">교통비</td><td style="text-align:right;">${transportPay.toLocaleString()}원</td></tr>
            <tr><td class="df-label" style="background:#e3f2fd;">지급합계</td><td colspan="3" style="text-align:right;font-weight:700;font-size:1.1em;background:#e3f2fd;">${total.toLocaleString()}원</td></tr>
          </tbody>
        </table>
        <div class="df-bottom" style="margin-top:16px;">
          <p>위 금액을 정히 지급합니다.</p>
          <table class="df-table" style="max-width:400px;margin:12px auto 0;">
            <tbody>
              <tr><td class="df-label">기관명</td><td style="padding:8px;">${settings.provider_name || settings.org_name || '-'}</td></tr>
              <tr><td class="df-label">대표자</td><td style="padding:8px;">${settings.provider_rep || settings.org_rep || '-'} (인)</td></tr>
            </tbody>
          </table>
          <table class="df-table" style="max-width:400px;margin:12px auto 0;">
            <tbody>
              <tr><td class="df-label">수령인</td><td style="padding:8px;">${s.manager_name || '-'} (인)</td></tr>
            </tbody>
          </table>
        </div>
      </div>`;
    });

    document.getElementById('payrollDetailArea').innerHTML = detailHtml;

    if (summaries.length === 0) {
      showToast('해당 월의 근무 기록이 없습니다.', 'info');
    } else {
      showToast(`${summaries.length}명의 급여대장을 조회했습니다.`, 'success');
    }
  } catch (e) {
    console.error('Payroll load error:', e);
    showToast('급여대장 조회 실패: ' + e.message, 'error');
  }
}

function payrollPrint() {
  const paper = document.getElementById('payrollPaper');
  if (!paper || paper.style.display === 'none') {
    return showToast('먼저 조회 버튼을 눌러주세요.', 'error');
  }
  const sec = document.getElementById('sec-payroll');
  const detail = document.getElementById('payrollDetailArea');
  sec.classList.add('print-active');
  // 급여대장(요약) 1장만 인쇄 — 개인별 명세서는 숨김
  if (detail) detail.style.display = 'none';
  window.print();
  setTimeout(() => {
    sec.classList.remove('print-active');
    if (detail) detail.style.display = '';
  }, 500);
}

// ═══════════════════════════════════════
// MONITORING (모니터링 - 서비스 제공기관 기록지) [서식 08호]
// ═══════════════════════════════════════

function monAutoFill() {
  const el = (id) => document.getElementById(id);
  // 제공기관 자동채움
  if (el('monProvName') && !el('monProvName').value) {
    el('monProvName').value = settings.provider_name || '산청인애노인통합지원센터';
  }
  // 담당자 = 선택한 매니저 이름
  const mid = el('monManager').value;
  const m = managers.find(x => x.id == mid);
  if (m && el('monStaffName')) {
    el('monStaffName').value = m.name;
  }
}

function monAutoFillClient() {
  const cid = document.getElementById('monClient').value;
  const c = clients.find(x => x.id == cid);
  if (c) {
    document.getElementById('monClientName').value = c.name || '';
    // 생년월일 형식 변환 (YYYY-MM-DD → YYYY.MM.DD)
    if (c.birth_date || c.birth) {
      const b = (c.birth_date || c.birth).replace(/-/g, '.');
      document.getElementById('monClientBirth').value = b;
    }
    document.getElementById('monClientAddr').value = c.address || '';
  }
}

function monCollectData() {
  const el = (id) => { const e = document.getElementById(id); return e ? e.value : ''; };
  // 서비스 제공 현황 (최대 3행)
  const services = [];
  for (let i = 1; i <= 3; i++) {
    const cat1 = el(`monSvcCat1_${i}`);
    const cat2 = el(`monSvcCat2_${i}`);
    const detail = el(`monSvcDetail_${i}`);
    const cycle = el(`monSvcCycle_${i}`);
    const firstDate = el(`monSvcFirstDate_${i}`);
    const directDate = el(`monSvcDirectDate_${i}`);
    if (cat1 || detail) {
      services.push({ cat1, cat2, detail, cycle, first_date: firstDate, direct_date: directDate });
    }
  }

  // 상태변화 라디오
  let statusChange = '개선';
  document.querySelectorAll('input[name="monStatusChange"]').forEach(r => {
    if (r.checked) statusChange = r.value;
  });

  return {
    manager_id: document.getElementById('monManager').value || null,
    client_id: document.getElementById('monClient').value || null,
    month: new Date().toISOString().slice(0, 7),
    client_name: el('monClientName'),
    client_birth: el('monClientBirth'),
    client_address: el('monClientAddr'),
    provider_name: el('monProvName'),
    staff_name: el('monStaffName'),
    services: JSON.stringify(services),
    status_change: statusChange,
    status_detail: el('monStatusDetail'),
    note: el('monNote')
  };
}

function monFillForm(data) {
  const el = (id) => document.getElementById(id);
  if (data.id) el('monEditId').value = data.id;
  if (data.manager_id) el('monManager').value = data.manager_id;
  if (data.client_id) el('monClient').value = data.client_id;
  if (data.client_name) el('monClientName').value = data.client_name;
  if (data.client_birth) el('monClientBirth').value = data.client_birth;
  if (data.client_address) el('monClientAddr').value = data.client_address;
  if (data.provider_name) el('monProvName').value = data.provider_name;
  if (data.staff_name) el('monStaffName').value = data.staff_name;
  if (data.status_detail) el('monStatusDetail').value = data.status_detail;
  if (data.note) el('monNote').value = data.note;

  // 상태변화 라디오
  if (data.status_change) {
    document.querySelectorAll('input[name="monStatusChange"]').forEach(r => {
      r.checked = (r.value === data.status_change);
    });
  }

  // 서비스 현황 채우기
  let services = [];
  try { services = JSON.parse(data.services || '[]'); } catch(e) {}
  for (let i = 0; i < 3; i++) {
    const svc = services[i] || {};
    const idx = i + 1;
    if (el(`monSvcCat1_${idx}`)) el(`monSvcCat1_${idx}`).value = svc.cat1 || '';
    if (el(`monSvcCat2_${idx}`)) el(`monSvcCat2_${idx}`).value = svc.cat2 || '';
    if (el(`monSvcDetail_${idx}`)) el(`monSvcDetail_${idx}`).value = svc.detail || '';
    if (el(`monSvcCycle_${idx}`)) el(`monSvcCycle_${idx}`).value = svc.cycle || '';
    if (el(`monSvcFirstDate_${idx}`)) el(`monSvcFirstDate_${idx}`).value = svc.first_date || '';
    if (el(`monSvcDirectDate_${idx}`)) el(`monSvcDirectDate_${idx}`).value = svc.direct_date || '';
  }

  // 자동연동 결과에서 직접 제공한 필드도 처리
  if (data.svc_cat1_1 && !services.length) {
    el('monSvcCat1_1').value = data.svc_cat1_1 || '';
    el('monSvcCat2_1').value = data.svc_cat2_1 || '';
    el('monSvcDetail_1').value = data.svc_detail_1 || '';
    el('monSvcCycle_1').value = data.svc_cycle_1 || '';
    el('monSvcFirstDate_1').value = data.svc_first_date_1 || '';
    el('monSvcDirectDate_1').value = data.svc_direct_date_1 || '';
  }
}

function monReset() {
  document.getElementById('monEditId').value = '';
  ['monClientName', 'monClientBirth', 'monClientAddr', 'monStaffName', 'monStatusDetail', 'monNote'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  // 제공기관 기본값
  const provEl = document.getElementById('monProvName');
  if (provEl) provEl.value = settings.provider_name || '산청인애노인통합지원센터';
  // 서비스 행 초기화
  for (let i = 1; i <= 3; i++) {
    ['monSvcCat1_', 'monSvcCat2_', 'monSvcDetail_', 'monSvcCycle_', 'monSvcFirstDate_', 'monSvcDirectDate_'].forEach(prefix => {
      const el = document.getElementById(prefix + i);
      if (el) el.value = (i === 1 && prefix === 'monSvcCat1_') ? '가사지원' : (i === 1 && prefix === 'monSvcCat2_') ? '가사지원' : (i === 1 && prefix === 'monSvcDetail_') ? '일상지원,말벗,청소,활동보조' : (i === 1 && prefix === 'monSvcCycle_') ? '주3회' : '';
    });
  }
  // 라디오 초기화
  document.querySelectorAll('input[name="monStatusChange"]').forEach(r => {
    r.checked = (r.value === '개선');
  });
}

async function monSave() {
  const data = monCollectData();
  const editId = document.getElementById('monEditId').value;
  try {
    if (editId) {
      await apiPut(`/api/monitoring-records/${editId}`, data);
      showToast('모니터링 기록지가 수정되었습니다.', 'success');
    } else {
      await apiPost('/api/monitoring-records', data);
      showToast('모니터링 기록지가 저장되었습니다! ✅', 'success');
    }
    invalidateCache('monitoring');
    monLoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

async function monLoadList() {
  try {
    const list = await apiGet('/api/monitoring-records');
    const el = document.getElementById('monSavedList');
    const empty = document.getElementById('monSavedEmpty');
    if (!list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(c => `<div class="saved-item" onclick="monLoadItem(${c.id})">
      <div class="saved-item-info">
        <div class="saved-item-title">📋 ${c.client_name || '미입력'} - ${c.staff_name || c.manager_name || '담당자 미입력'}</div>
        <div class="saved-item-sub">${c.month || '-'} | ${c.status_change || '-'} | ${(c.created_at || '').slice(0, 10)}</div>
      </div>
      <div class="saved-item-actions">
        <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();monDeleteItem(${c.id})">🗑️</button>
      </div>
    </div>`).join('');
  } catch (e) { console.error('Monitoring list error:', e); }
}

async function monLoadItem(id) {
  try {
    const data = await apiGet(`/api/monitoring-records/${id}`);
    monReset();
    monFillForm(data);
    showToast('모니터링 기록지를 불러왔습니다.', 'success');
    document.getElementById('monitoringPaper').scrollIntoView({ behavior: 'smooth' });
  } catch (e) { showToast('불러오기 실패', 'error'); }
}

async function monDeleteItem(id) {
  if (!confirm('모니터링 기록지를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/monitoring-records/${id}`);
    showToast('삭제되었습니다.', 'success');
    invalidateCache('monitoring');
    monLoadList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

async function monAutoGenerate() {
  const managerId = document.getElementById('monManager').value;
  const clientId = document.getElementById('monClient').value;
  if (!managerId || !clientId) {
    return showToast('매니저와 대상자를 먼저 선택해주세요.', 'error');
  }
  try {
    const result = await apiPost('/api/monitoring-records/auto-generate', {
      manager_id: managerId, client_id: clientId
    });
    if (result.error) return showToast(result.error, 'error');
    monFillForm(result);
    // 제공기관 자동채움
    const provEl = document.getElementById('monProvName');
    if (provEl && !provEl.value) provEl.value = settings.provider_name || '산청인애노인통합지원센터';
    showToast(`자동연동 완료! (${result.total_days || 0}회, ${result.total_hours || 0}시간)`, 'success');
  } catch (e) { showToast('자동연동 실패: ' + e.message, 'error'); }
}

function monPrint() {
  const sec = document.getElementById('sec-monitoring');
  if (!sec) return;
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// ACCOUNTING (회계자료)
// ═══════════════════════════════════════

async function acctLoad() {
  const month = document.getElementById('acctMonth').value || currentMonthStr();
  document.getElementById('acctMonth').value = month;

  try {
    const data = await apiGet(`/api/accounting/monthly?month=${month}`);
    const [yr, mo] = month.split('-');
    const fmt = (v) => (v||0).toLocaleString() + '원';

    // 제목 및 기관 정보
    document.getElementById('acctPaperMonth').textContent = `${yr}년 ${parseInt(mo)}월 회계자료`;
    document.getElementById('acctOrgName').textContent = data.org_name || '';
    document.getElementById('acctBottomOrg').textContent = data.org_name || '-';
    document.getElementById('acctBottomRep').textContent = (data.org_rep || '-') + ' (인)';
    document.getElementById('acctHourlyRate').textContent = (data.hourly_wage||13500).toLocaleString();

    // ═══ 수입 ① : 지자체 수가 청구 ═══
    const inc = data.income || {};
    const govClaim = inc.gov_claim || {};
    let govHtml = '';
    if (!govClaim.details || govClaim.details.length === 0) {
      govHtml = `<tr><td colspan="6" style="padding:12px;border:1px solid #333;text-align:center;color:#999;">해당 월의 수가 청구서(서식11) 데이터가 없습니다.</td></tr>`;
    } else {
      govClaim.details.forEach((d, i) => {
        govHtml += `<tr>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${i+1}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.manager_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.client_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;">${fmt(d.provide_amount)}</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;">${fmt(d.personal_burden)}</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;font-weight:600;">${fmt(d.claimable)}</td>
        </tr>`;
      });
    }
    document.getElementById('acctGovClaimBody').innerHTML = govHtml;
    document.getElementById('acctGovProvideTotal').textContent = fmt(govClaim.total_provide);
    document.getElementById('acctGovPersonalTotal').textContent = fmt(govClaim.total_personal_burden);
    document.getElementById('acctGovClaimTotal').textContent = fmt(govClaim.total_claimable);

    // ═══ 수입 ② : 원거리 교통지원금 ═══
    const trGrant = inc.transport_grant || {};
    let trHtml = '';
    if (!trGrant.details || trGrant.details.length === 0) {
      trHtml = `<tr><td colspan="6" style="padding:12px;border:1px solid #333;text-align:center;color:#999;">해당 월의 교통지원금 신청서 데이터가 없습니다.</td></tr>`;
    } else {
      trGrant.details.forEach((d, i) => {
        const distLabel = d.distance_range === '3-10' ? '3~10km' : d.distance_range === '10+' ? '10km 이상' : (d.distance_range||'-');
        trHtml += `<tr>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${i+1}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.manager_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.client_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${distLabel}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.trip_count}회 × ${fmt(d.per_amount)}</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;font-weight:600;">${fmt(d.total_amount)}</td>
        </tr>`;
      });
    }
    document.getElementById('acctTransportBody').innerHTML = trHtml;
    document.getElementById('acctTransportTotal').textContent = fmt(trGrant.total);

    // ═══ 수입 합계 ═══
    document.getElementById('acctIncomeTotalAll').textContent = fmt(inc.total);

    // ═══ 지출 : 매니저 급여 ═══
    const exp = data.expense || {};
    let payHtml = '';
    if (!exp.payroll || exp.payroll.length === 0) {
      payHtml = `<tr><td colspan="5" style="padding:12px;border:1px solid #333;text-align:center;color:#999;">해당 월의 출근 기록이 없습니다.</td></tr>`;
    } else {
      exp.payroll.forEach(m => {
        payHtml += `<tr>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${m.no}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;font-weight:600;">${m.manager_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${m.work_days}일</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${m.total_hours.toFixed(1)}시간</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;font-weight:600;">${fmt(m.wage)}</td>
        </tr>`;
      });
    }
    document.getElementById('acctPayrollBody').innerHTML = payHtml;
    document.getElementById('acctWageTotal').textContent = fmt(exp.wage_total);

    // ═══ 지출 ② : 교통비 (매니저 지급) ═══
    let trExpHtml = '';
    const trExpDetails = exp.transport_details || [];
    if (trExpDetails.length === 0) {
      trExpHtml = `<tr><td colspan="6" style="padding:12px;border:1px solid #333;text-align:center;color:#999;">해당 월의 교통비 지급 내역이 없습니다.</td></tr>`;
    } else {
      trExpDetails.forEach((d, i) => {
        const distLabel = d.distance_range === '3-10' ? '3~10km' : d.distance_range === '10+' ? '10km 이상' : (d.distance_range||'-');
        trExpHtml += `<tr>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${i+1}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.manager_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.client_name}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${distLabel}</td>
          <td style="padding:6px;border:1px solid #333;text-align:center;">${d.trip_count}회 × ${fmt(d.per_amount)}</td>
          <td style="padding:6px;border:1px solid #333;text-align:right;font-weight:600;">${fmt(d.total_amount)}</td>
        </tr>`;
      });
    }
    document.getElementById('acctTransportExpBody').innerHTML = trExpHtml;
    document.getElementById('acctTransportExpTotal').textContent = fmt(exp.transport_total);
    document.getElementById('acctExpenseTotal').textContent = fmt(exp.total);

    // ═══ 손익 요약 ═══
    document.getElementById('acctSummaryIncome').textContent = fmt(inc.total);
    document.getElementById('acctSummaryWage').textContent = fmt(exp.wage_total);
    document.getElementById('acctSummaryTransport').textContent = fmt(exp.transport_total);
    const profitEl = document.getElementById('acctNetProfit');
    profitEl.textContent = fmt(data.net_profit);
    profitEl.style.color = data.net_profit >= 0 ? '#2e7d32' : '#c62828';

    document.getElementById('accountingPaper').style.display = 'block';
  } catch (e) {
    showToast('회계자료 조회 실패: ' + e.message, 'error');
  }
}

function acctPrint() {
  const sec = document.getElementById('sec-accounting');
  if (!sec) return;
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// 서식10: 기본서비스 결과보고서
// ═══════════════════════════════════════
function rpt10AutoFill() {
  const mid = document.getElementById('rpt10Manager').value;
  const mgr = managers.find(m => m.id == mid);
  if (mgr) { document.getElementById('rpt10StaffName').value = mgr.name; document.getElementById('rpt10StaffPhone').value = mgr.phone || ''; }
  document.getElementById('rpt10ProvName').value = settings.provider_name || '';
  document.getElementById('rpt10ProvContact').value = settings.provider_contact || settings.claimant_name || '';
  document.getElementById('rpt10ProvPhone').value = settings.provider_phone || '';
}
function rpt10AutoFillClient() {
  const cid = document.getElementById('rpt10Client').value;
  const c = clients.find(x => x.id == cid);
  if (!c) return;
  document.getElementById('rpt10ClientName').value = c.name;
  document.getElementById('rpt10ClientBirth').value = c.birth_date || '';
  document.getElementById('rpt10ClientAge').value = calcAge(c.birth_date);
  document.getElementById('rpt10ClientAddr').value = c.address || '';
  document.querySelectorAll('input[name="rpt10Gender"]').forEach(r => r.checked = r.value === c.gender);
}
function rpt10CollectData() {
  const rounds = [];
  document.querySelectorAll('#rpt10RoundsBody tr[data-round]').forEach(tr => {
    rounds.push({
      round: tr.querySelector('.rpt10-round')?.value || '',
      date: tr.querySelector('.rpt10-date')?.value || '',
      time_start: tr.querySelector('.rpt10-ts')?.value || '',
      time_end: tr.querySelector('.rpt10-te')?.value || '',
      content: tr.querySelector('.rpt10-content')?.value || ''
    });
  });
  return {
    manager_id: document.getElementById('rpt10Manager').value || null,
    client_id: document.getElementById('rpt10Client').value || null,
    month: document.getElementById('rpt10Month').value,
    provider_name: document.getElementById('rpt10ProvName').value,
    provider_contact: document.getElementById('rpt10ProvContact').value,
    provider_phone: document.getElementById('rpt10ProvPhone').value,
    staff_name: document.getElementById('rpt10StaffName').value,
    staff_phone: document.getElementById('rpt10StaffPhone').value,
    client_name: document.getElementById('rpt10ClientName').value,
    client_birth: document.getElementById('rpt10ClientBirth').value,
    client_age: document.getElementById('rpt10ClientAge').value,
    client_gender: document.querySelector('input[name="rpt10Gender"]:checked')?.value || '',
    client_address: document.getElementById('rpt10ClientAddr').value,
    service_name: document.getElementById('rpt10ServiceName').value,
    service_period_start: document.getElementById('rpt10PeriodStart').value,
    service_period_end: document.getElementById('rpt10PeriodEnd').value,
    service_summary: document.getElementById('rpt10ServiceSummary').value,
    rounds: rounds,
    change_status: document.querySelector('input[name="rpt10Change"]:checked')?.value || '변경없음',
    change_content: document.getElementById('rpt10ChangeContent')?.value || '',
    change_reason: document.getElementById('rpt10ChangeReason')?.value || '',
    goal_status: document.querySelector('input[name="rpt10Goal"]:checked')?.value || '',
    org_opinion: document.getElementById('rpt10OrgOpinion').value
  };
}
function rpt10RenderRounds(rounds) {
  const tbody = document.getElementById('rpt10RoundsBody');
  if (!rounds || !rounds.length) { tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:12px;">데이터 없음</td></tr>'; return; }
  tbody.innerHTML = rounds.map((r, i) => {
    const dayName = r.date ? ['일','월','화','수','목','금','토'][new Date(r.date).getDay()] : '';
    return `<tr data-round="${i}">
      <td style="text-align:center;"><input type="text" class="df-input rpt10-round" value="${r.round || ''}" style="width:40px;text-align:center;"></td>
      <td style="font-size:0.82rem;"><input type="date" class="df-input rpt10-date" value="${r.date || ''}" style="font-size:0.8rem;"> <span style="font-size:0.75rem;color:#666;">(${dayName})</span></td>
      <td style="font-size:0.82rem;"><input type="time" class="df-input rpt10-ts" value="${r.time_start || ''}" style="width:70px;font-size:0.8rem;">~<input type="time" class="df-input rpt10-te" value="${r.time_end || ''}" style="width:70px;font-size:0.8rem;"></td>
      <td><textarea class="df-textarea rpt10-content" rows="2" style="font-size:0.82rem;min-height:40px;">${r.content || ''}</textarea></td>
    </tr>`;
  }).join('');
}
async function rpt10Save() {
  const data = rpt10CollectData();
  const editId = document.getElementById('rpt10EditId').value;
  try {
    if (editId) { await apiPut('/api/service-reports/' + editId, data); showToast('결과보고서 수정완료', 'success'); }
    else { await apiPost('/api/service-reports', data); showToast('결과보고서 저장완료 ✅', 'success'); }
    rpt10LoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}
function rpt10Print() {
  const sec = document.getElementById('sec-report10');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}
function rpt10Reset() {
  document.getElementById('rpt10EditId').value = '';
  ['rpt10ProvName','rpt10ProvContact','rpt10ProvPhone','rpt10StaffName','rpt10StaffPhone','rpt10ClientName','rpt10ClientBirth','rpt10ClientAge','rpt10ClientAddr','rpt10ServiceName','rpt10PeriodStart','rpt10PeriodEnd','rpt10ServiceSummary','rpt10ChangeContent','rpt10ChangeReason','rpt10OrgOpinion'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  document.querySelectorAll('input[name="rpt10Gender"]').forEach(r => r.checked = false);
  const cr = document.querySelector('input[name="rpt10Change"][value="변경없음"]'); if (cr) cr.checked = true;
  document.querySelectorAll('input[name="rpt10Goal"]').forEach(r => r.checked = false);
  document.getElementById('rpt10RoundsBody').innerHTML = '<tr><td colspan="4" style="text-align:center;padding:20px;">자동생성 버튼을 클릭하면 일일결과등록의 데이터가 채워집니다.</td></tr>';
}
async function rpt10AutoGenerate() {
  const month = document.getElementById('rpt10Month').value;
  const mid = document.getElementById('rpt10Manager').value;
  const cid = document.getElementById('rpt10Client').value;
  if (!month || !mid || !cid) { showToast('월, 매니저, 대상자를 선택하세요.', 'warning'); return; }
  try {
    const r = await apiPost('/api/service-reports/auto-generate', { month, manager_id: parseInt(mid), client_id: parseInt(cid) });
    if (r.error) { showToast(r.error, 'warning'); return; }
    rpt10FillForm(r); showToast('결과보고서 자동생성 완료! ⚡ ' + (r.rounds?.length || 0) + '회차', 'success');
    rpt10LoadList();
  } catch (e) { showToast('자동생성 실패: ' + e.message, 'error'); }
}
function rpt10FillForm(d) {
  if (d.id) document.getElementById('rpt10EditId').value = d.id;
  if (d.manager_id) document.getElementById('rpt10Manager').value = d.manager_id;
  if (d.client_id) document.getElementById('rpt10Client').value = d.client_id;
  if (d.month) document.getElementById('rpt10Month').value = d.month;
  document.getElementById('rpt10ProvName').value = d.provider_name || '';
  document.getElementById('rpt10ProvContact').value = d.provider_contact || '';
  document.getElementById('rpt10ProvPhone').value = d.provider_phone || '';
  document.getElementById('rpt10StaffName').value = d.staff_name || '';
  document.getElementById('rpt10StaffPhone').value = d.staff_phone || '';
  document.getElementById('rpt10ClientName').value = d.client_name || '';
  document.getElementById('rpt10ClientBirth').value = d.client_birth || '';
  document.getElementById('rpt10ClientAge').value = d.client_age || '';
  document.getElementById('rpt10ClientAddr').value = d.client_address || '';
  if (d.client_gender) document.querySelectorAll('input[name="rpt10Gender"]').forEach(r => r.checked = r.value === d.client_gender);
  document.getElementById('rpt10ServiceName').value = d.service_name || '가사지원';
  document.getElementById('rpt10PeriodStart').value = d.service_period_start || '';
  document.getElementById('rpt10PeriodEnd').value = d.service_period_end || '';
  document.getElementById('rpt10ServiceSummary').value = d.service_summary || '';
  let rounds = d.rounds;
  if (typeof rounds === 'string') try { rounds = JSON.parse(rounds); } catch(e) { rounds = []; }
  rpt10RenderRounds(rounds || []);
  const cs = d.change_status || '변경없음';
  const cr = document.querySelector(`input[name="rpt10Change"][value="${cs}"]`); if (cr) cr.checked = true;
  const crow = document.getElementById('rpt10ChangeRow'); if (crow) crow.style.display = cs === '변경됨' ? '' : 'none';
  document.getElementById('rpt10ChangeContent').value = d.change_content || '';
  document.getElementById('rpt10ChangeReason').value = d.change_reason || '';
  if (d.goal_status) { const gr = document.querySelector(`input[name="rpt10Goal"][value="${d.goal_status}"]`); if (gr) gr.checked = true; }
  document.getElementById('rpt10OrgOpinion').value = d.org_opinion || '';
}
async function rpt10LoadList() {
  const month = document.getElementById('rpt10Month').value;
  try {
    const list = await apiGet('/api/service-reports?month=' + (month || ''));
    const el = document.getElementById('rpt10SavedList');
    const empty = document.getElementById('rpt10SavedEmpty');
    if (!list || !list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(r => `<div class="saved-item" onclick="rpt10Load(${r.id})">
      <div class="saved-item-info"><div class="saved-item-title">${r.client_name||'미입력'} - ${r.month||''}</div>
      <div class="saved-item-sub">제공인력: ${r.staff_name||'-'}</div></div>
      <div class="saved-item-actions"><button class="btn btn-sm btn-danger" onclick="event.stopPropagation();rpt10Delete(${r.id})">삭제</button></div>
    </div>`).join('');
  } catch (e) { console.error(e); }
}
async function rpt10Load(id) {
  try { const d = await apiGet('/api/service-reports/' + id); rpt10FillForm(d); showToast('불러왔습니다.', 'success'); } catch(e) { showToast('실패', 'error'); }
}
async function rpt10Delete(id) {
  if (!confirm('삭제하시겠습니까?')) return;
  try { await apiDelete('/api/service-reports/' + id); rpt10LoadList(); showToast('삭제됨', 'success'); } catch(e) { showToast('실패', 'error'); }
}

// ═══════════════════════════════════════
// 서식11: 기본서비스 비용청구서
// ═══════════════════════════════════════
function clm11AutoFill() {
  const mid = document.getElementById('clm11Manager').value;
  const mgr = managers.find(m => m.id == mid);
  if (mgr) document.getElementById('clm11StaffName').value = mgr.name;
  document.getElementById('clm11ProvName').value = settings.provider_name || '';
  document.getElementById('clm11ProvContact').value = settings.provider_contact || settings.claimant_name || '';
  document.getElementById('clm11ClaimTitle').value = settings.claimant_title || '';
  document.getElementById('clm11ClaimName').value = settings.claimant_name || '';
}
function clm11AutoFillClient() {
  const cid = document.getElementById('clm11Client').value;
  const c = clients.find(x => x.id == cid);
  if (!c) return;
  document.getElementById('clm11ClientName').value = c.name;
  document.getElementById('clm11ClientBirth').value = c.birth_date || '';
  document.getElementById('clm11ClientAddr').value = c.address || '';
  document.querySelectorAll('input[name="clm11Gender"]').forEach(r => r.checked = r.value === c.gender);
}
function clm11RenderItems(items) {
  const tbody = document.getElementById('clm11ItemsBody');
  if (!items || !items.length) { tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:12px;">데이터 없음</td></tr>'; return; }
  tbody.innerHTML = items.map((it, i) => {
    const dayName = it.date ? ['일','월','화','수','목','금','토'][new Date(it.date).getDay()] : '';
    return `<tr data-item="${i}">
      <td style="text-align:center;border:1px solid #333;">${it.round || i+1}</td>
      <td style="white-space:nowrap;border:1px solid #333;">${it.date || ''} (${dayName})</td>
      <td style="white-space:nowrap;text-align:center;border:1px solid #333;">${it.time_start||''}~${it.time_end||''}</td>
      <td style="text-align:center;white-space:nowrap;border:1px solid #333;">${it.hours||''}h/${it.minutes||0}분</td>
      <td style="border:1px solid #333;overflow:hidden;">${(it.content||'').slice(0,25)}${(it.content||'').length>25?'…':''}</td>
      <td style="text-align:right;border:1px solid #333;">${(it.provide_amount||0).toLocaleString()}</td>
      <td style="text-align:right;border:1px solid #333;">${(it.transport||0).toLocaleString()}</td>
      <td style="text-align:right;border:1px solid #333;">${(it.personal_burden||0).toLocaleString()}</td>
      <td style="text-align:right;font-weight:700;border:1px solid #333;">${(it.claimable||0).toLocaleString()}</td>
    </tr>`;
  }).join('');
  // Update totals
  const tp = items.reduce((s,i) => s + (i.provide_amount||0), 0);
  const ts = items.reduce((s,i) => s + (i.transport||0), 0);
  const tpb = items.reduce((s,i) => s + (i.personal_burden||0), 0);
  const tc = items.reduce((s,i) => s + (i.claimable||0), 0);
  document.getElementById('clm11TotalProvide').textContent = tp.toLocaleString();
  document.getElementById('clm11TotalSurcharge').textContent = ts.toLocaleString();
  document.getElementById('clm11TotalPersonal').textContent = tpb.toLocaleString();
  document.getElementById('clm11TotalClaimable').textContent = tc.toLocaleString() + '원';
}
function clm11CollectData() {
  return {
    manager_id: document.getElementById('clm11Manager').value || null,
    client_id: document.getElementById('clm11Client').value || null,
    month: document.getElementById('clm11Month').value,
    service_type: document.getElementById('clm11ServiceType').value,
    provider_name: document.getElementById('clm11ProvName').value,
    provider_contact: document.getElementById('clm11ProvContact').value,
    staff_name: document.getElementById('clm11StaffName').value,
    client_name: document.getElementById('clm11ClientName').value,
    client_birth: document.getElementById('clm11ClientBirth').value,
    client_gender: document.querySelector('input[name="clm11Gender"]:checked')?.value || '',
    client_dong: document.getElementById('clm11ClientDong').value,
    client_address: document.getElementById('clm11ClientAddr').value,
    claimant_title: document.getElementById('clm11ClaimTitle').value,
    claimant_name: document.getElementById('clm11ClaimName').value,
    items: window._clm11Items || []
  };
}
async function clm11Save() {
  const data = clm11CollectData();
  const editId = document.getElementById('clm11EditId').value;
  try {
    if (editId) { await apiPut('/api/cost-claims/' + editId, data); showToast('비용청구서 수정완료', 'success'); }
    else { await apiPost('/api/cost-claims', data); showToast('비용청구서 저장완료 ✅', 'success'); }
    clm11LoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}
function clm11Print() {
  const sec = document.getElementById('sec-claim11');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}
function clm11Reset() {
  document.getElementById('clm11EditId').value = '';
  ['clm11ServiceType','clm11ProvName','clm11ProvContact','clm11StaffName','clm11ClientName','clm11ClientBirth','clm11ClientDong','clm11ClientAddr','clm11ClaimTitle','clm11ClaimName'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  document.querySelectorAll('input[name="clm11Gender"]').forEach(r => r.checked = false);
  document.getElementById('clm11ItemsBody').innerHTML = '<tr><td colspan="9" style="text-align:center;padding:20px;">자동생성 버튼을 클릭하면 출석/일지 데이터가 채워집니다.</td></tr>';
  ['clm11TotalProvide','clm11TotalSurcharge','clm11TotalPersonal'].forEach(id => document.getElementById(id).textContent = '0');
  document.getElementById('clm11TotalClaimable').textContent = '0';
  window._clm11Items = [];
}
async function clm11AutoGenerate() {
  const month = document.getElementById('clm11Month').value;
  const mid = document.getElementById('clm11Manager').value;
  const cid = document.getElementById('clm11Client').value;
  if (!month || !mid || !cid) { showToast('월, 매니저, 대상자를 선택하세요.', 'warning'); return; }
  try {
    const r = await apiPost('/api/cost-claims/auto-generate', { month, manager_id: parseInt(mid), client_id: parseInt(cid) });
    if (r.error) { showToast(r.error, 'warning'); return; }
    clm11FillForm(r); showToast('비용청구서 자동생성 완료! ⚡ 총 청구: ' + (r.total_claimable||0).toLocaleString() + '원', 'success');
    clm11LoadList();
  } catch (e) { showToast('자동생성 실패: ' + e.message, 'error'); }
}
function clm11FillForm(d) {
  if (d.id) document.getElementById('clm11EditId').value = d.id;
  if (d.manager_id) document.getElementById('clm11Manager').value = d.manager_id;
  if (d.client_id) document.getElementById('clm11Client').value = d.client_id;
  if (d.month) document.getElementById('clm11Month').value = d.month;
  document.getElementById('clm11ServiceType').value = d.service_type || '가사지원';
  document.getElementById('clm11ProvName').value = d.provider_name || '';
  document.getElementById('clm11ProvContact').value = d.provider_contact || '';
  document.getElementById('clm11StaffName').value = d.staff_name || '';
  document.getElementById('clm11ClientName').value = d.client_name || '';
  document.getElementById('clm11ClientBirth').value = d.client_birth || '';
  document.getElementById('clm11ClientDong').value = d.client_dong || '';
  document.getElementById('clm11ClientAddr').value = d.client_address || '';
  if (d.client_gender) document.querySelectorAll('input[name="clm11Gender"]').forEach(r => r.checked = r.value === d.client_gender);
  document.getElementById('clm11ClaimTitle').value = d.claimant_title || '';
  document.getElementById('clm11ClaimName').value = d.claimant_name || '';
  if (d.submit_year) document.getElementById('clm11SubmitYear').textContent = d.submit_year;
  if (d.submit_month) document.getElementById('clm11SubmitMonth').textContent = d.submit_month;
  if (d.submit_day) document.getElementById('clm11SubmitDay').textContent = d.submit_day;
  let items = d.items;
  if (typeof items === 'string') try { items = JSON.parse(items); } catch(e) { items = []; }
  window._clm11Items = items || [];
  clm11RenderItems(window._clm11Items);
}
async function clm11LoadList() {
  const month = document.getElementById('clm11Month').value;
  try {
    const list = await apiGet('/api/cost-claims?month=' + (month || ''));
    const el = document.getElementById('clm11SavedList');
    const empty = document.getElementById('clm11SavedEmpty');
    if (!list || !list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(r => `<div class="saved-item" onclick="clm11Load(${r.id})">
      <div class="saved-item-info"><div class="saved-item-title">${r.client_name||'미입력'} - ${r.month||''}</div>
      <div class="saved-item-sub">총 청구: ${(r.total_claimable||0).toLocaleString()}원</div></div>
      <div class="saved-item-actions"><button class="btn btn-sm btn-danger" onclick="event.stopPropagation();clm11Delete(${r.id})">삭제</button></div>
    </div>`).join('');
  } catch (e) { console.error(e); }
}
async function clm11Load(id) {
  try { const d = await apiGet('/api/cost-claims/' + id); clm11FillForm(d); showToast('불러왔습니다.', 'success'); } catch(e) { showToast('실패', 'error'); }
}
async function clm11Delete(id) {
  if (!confirm('삭제하시겠습니까?')) return;
  try { await apiDelete('/api/cost-claims/' + id); clm11LoadList(); showToast('삭제됨', 'success'); } catch(e) { showToast('실패', 'error'); }
}

// ═══════════════════════════════════════
// CONTRACT (서비스 제공·이용 계약서)
// ═══════════════════════════════════════
function ctAutoFill() {
  const mid = document.getElementById('ctManager').value;
  const m = managers.find(x => x.id == mid);
  // Pre-fill provider defaults (연락처는 항상 기관 연락처로 설정)
  const el = (id) => document.getElementById(id);
  if (el('ctProvName') && !el('ctProvName').value) el('ctProvName').value = settings.provider_name || '산청인애노인통합지원센터';
  if (el('ctProvRep') && !el('ctProvRep').value) el('ctProvRep').value = settings.provider_rep || '김일득';
  el('ctProvPhone').value = settings.provider_phone || '055-973-8642';
  if (el('ctProvAddr') && !el('ctProvAddr').value) el('ctProvAddr').value = settings.provider_address || '산청군 산청읍 산청대로 1381번길 17';
}

function ctAutoFillClient() {
  const cid = document.getElementById('ctClient').value;
  const c = clients.find(x => x.id == cid);
  if (c) {
    document.getElementById('ctClientName').value = c.name;
    document.getElementById('ctClientBirth').value = c.birth_date || '';
    document.getElementById('ctClientPhone').value = c.phone || '';
    document.getElementById('ctClientAddr').value = c.address || '';
  }
}

function ctCollectData() {
  return {
    contract_date: document.getElementById('ctDate').value,
    client_name: document.getElementById('ctClientName').value,
    client_birth: document.getElementById('ctClientBirth').value,
    client_phone: document.getElementById('ctClientPhone').value,
    client_address: document.getElementById('ctClientAddr').value,
    guardian_name: document.getElementById('ctGuardianName').value,
    guardian_relation: document.getElementById('ctGuardianRelation').value,
    guardian_phone: document.getElementById('ctGuardianPhone').value,
    provider_name: document.getElementById('ctProvName').value,
    provider_rep: document.getElementById('ctProvRep').value,
    provider_phone: document.getElementById('ctProvPhone').value,
    provider_address: document.getElementById('ctProvAddr').value,
    service_name: document.getElementById('ctServiceName').value,
    service_period_start: document.getElementById('ctPeriodStart').value,
    service_period_end: document.getElementById('ctPeriodEnd').value,
    service_schedule: document.getElementById('ctSchedule').value,
    surcharge_rate: document.getElementById('ctSurchargeRate').value,
    total_hours: parseFloat(document.getElementById('ctTotalHours').value) || 0,
    estimated_cost: parseFloat(document.getElementById('ctEstCost').value) || 0,
    personal_burden: parseFloat(document.getElementById('ctPersonalBurden').value) || 0,
    special_terms: document.getElementById('ctSpecialTerms').value,
    client_sign: document.getElementById('ctClientSign').value,
    guardian_sign: document.getElementById('ctGuardianSign').value,
    provider_sign: document.getElementById('ctProvSign').value,
    photo_path: '',
    custom_fields: JSON.stringify(collectCustomFields('ct')),
    manager_id: document.getElementById('ctManager').value || null,
    client_id: document.getElementById('ctClient').value || null
  };
}

async function ctSave() {
  const data = ctCollectData();
  const editId = document.getElementById('ctEditId').value;
  try {
    if (editId) {
      await apiPut(`/api/contracts/${editId}`, data);
      showToast('계약서가 수정되었습니다.', 'success');
    } else {
      await apiPost('/api/contracts', data);
      showToast('계약서가 저장되었습니다! ✅', 'success');
    }
    ctLoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

function ctReset() {
  document.getElementById('ctEditId').value = '';
  ['ctDate', 'ctClientName', 'ctClientBirth', 'ctClientPhone', 'ctClientAddr', 'ctGuardianName', 'ctGuardianRelation', 'ctGuardianPhone', 'ctProvName', 'ctProvRep', 'ctProvPhone', 'ctProvAddr', 'ctSchedule', 'ctSurchargeRate', 'ctSpecialTerms', 'ctClientSign', 'ctGuardianSign', 'ctProvSign'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('ctServiceName').value = '통합돌봄 기본서비스';
  document.getElementById('ctPeriodStart').value = '';
  document.getElementById('ctPeriodEnd').value = '';
  document.getElementById('ctTotalHours').value = '';
  document.getElementById('ctEstCost').value = '';
  document.getElementById('ctPersonalBurden').value = '';
  document.getElementById('ctDate').value = todayStr();
  renderCustomFields('ct', []);
  // 기관정보 자동 설정 (연락처 항상 055-973-8642)
  document.getElementById('ctProvName').value = settings.provider_name || '산청인애노인통합지원센터';
  document.getElementById('ctProvRep').value = settings.provider_rep || '김일득';
  document.getElementById('ctProvPhone').value = settings.provider_phone || '055-973-8642';
  document.getElementById('ctProvAddr').value = settings.provider_address || '산청군 산청읍 산청대로 1381번길 17';
}

function ctFillForm(c) {
  document.getElementById('ctEditId').value = c.id;
  document.getElementById('ctManager').value = c.manager_id || '';
  document.getElementById('ctClient').value = c.client_id || '';
  document.getElementById('ctDate').value = c.contract_date || '';
  document.getElementById('ctClientName').value = c.client_name || '';
  document.getElementById('ctClientBirth').value = c.client_birth || '';
  document.getElementById('ctClientPhone').value = c.client_phone || '';
  document.getElementById('ctClientAddr').value = c.client_address || '';
  document.getElementById('ctGuardianName').value = c.guardian_name || '';
  document.getElementById('ctGuardianRelation').value = c.guardian_relation || '';
  document.getElementById('ctGuardianPhone').value = c.guardian_phone || '';
  document.getElementById('ctProvName').value = c.provider_name || '';
  document.getElementById('ctProvRep').value = c.provider_rep || '';
  document.getElementById('ctProvPhone').value = c.provider_phone || '';
  document.getElementById('ctProvAddr').value = c.provider_address || '';
  document.getElementById('ctServiceName').value = c.service_name || '통합돌봄 기본서비스';
  document.getElementById('ctPeriodStart').value = c.service_period_start || '';
  document.getElementById('ctPeriodEnd').value = c.service_period_end || '';
  document.getElementById('ctSchedule').value = c.service_schedule || '';
  document.getElementById('ctSurchargeRate').value = c.surcharge_rate || '';
  document.getElementById('ctTotalHours').value = c.total_hours || '';
  document.getElementById('ctEstCost').value = c.estimated_cost || '';
  document.getElementById('ctPersonalBurden').value = c.personal_burden || '';
  document.getElementById('ctSpecialTerms').value = c.special_terms || '';
  document.getElementById('ctClientSign').value = c.client_sign || '';
  document.getElementById('ctGuardianSign').value = c.guardian_sign || '';
  document.getElementById('ctProvSign').value = c.provider_sign || '';
  try { renderCustomFields('ct', JSON.parse(c.custom_fields || '[]')); } catch(e) {}
}

async function ctLoadList() {
  try {
    const list = await apiGet('/api/contracts');
    const el = document.getElementById('ctSavedList');
    const empty = document.getElementById('ctSavedEmpty');
    if (!list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(c => `<div class="saved-item" onclick="ctLoadItem(${c.id})">
      <div class="saved-item-info">
        <div class="saved-item-title">${c.client_name || '미입력'} - ${c.service_name || '통합돌봄'}</div>
        <div class="saved-item-sub">기간: ${c.service_period_start || '?'} ~ ${c.service_period_end || '?'} | 계약일: ${c.contract_date || '-'}</div>
      </div>
      <div class="saved-item-actions">
        <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();ctDeleteItem(${c.id})">🗑️</button>
      </div>
    </div>`).join('');
  } catch (e) { console.error('Contract list error:', e); }
}

async function ctLoadItem(id) {
  try {
    const c = await apiGet(`/api/contracts/${id}`);
    ctReset();
    ctFillForm(c);
    showToast('계약서를 불러왔습니다.', 'success');
    document.getElementById('contractPaper').scrollIntoView({ behavior: 'smooth' });
  } catch (e) { showToast('불러오기 실패', 'error'); }
}

async function ctDeleteItem(id) {
  if (!confirm('계약서를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/contracts/${id}`);
    showToast('삭제되었습니다.', 'success');
    ctLoadList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

function ctPrint() {
  const sec = document.getElementById('sec-contract');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// TRANSPORT (원거리 교통지원금 신청서)
// ═══════════════════════════════════════
function trAutoFill() {
  const mid = document.getElementById('trManager').value;
  const m = managers.find(x => x.id == mid);
  if (m) {
    document.getElementById('trStaffName').value = m.name;
    document.getElementById('trStaffPhone').value = m.phone || '';
    if (document.getElementById('trStaffAddr')) document.getElementById('trStaffAddr').value = m.address || '';
  }
  // Pre-fill provider defaults
  const el = (id) => document.getElementById(id);
  if (el('trProvName') && !el('trProvName').value) el('trProvName').value = settings.provider_name || '산청인애노인통합지원센터';
  if (el('trProvRep') && !el('trProvRep').value) el('trProvRep').value = settings.provider_rep || '김일득';
  // 하단 청구 기관명/대표자 자동 채움
  if (el('trAppClaimOrg') && !el('trAppClaimOrg').value) el('trAppClaimOrg').value = settings.provider_name || '';
  if (el('trAppClaimRep') && !el('trAppClaimRep').value) el('trAppClaimRep').value = settings.provider_rep || '';
}

function trAutoFillClient() {
  const cid = document.getElementById('trClient').value;
  const c = clients.find(x => x.id == cid);
  if (c) {
    document.getElementById('trClientName').value = c.name;
    document.getElementById('trClientPhone').value = c.phone || '';
    document.getElementById('trClientAddr').value = c.address || '';
  }
}

function trCalcAmount() {
  const val = document.querySelector('input[name="trDistance"]:checked')?.value;
  if (val === '3-10') document.getElementById('trSupportAmount').value = '6,000원/회';
  else if (val === '10+') document.getElementById('trSupportAmount').value = '9,000원/회';
  else document.getElementById('trSupportAmount').value = '';
  trCalcTotal();
}

function trCalcTotal() {
  const distVal = document.querySelector('input[name="trDistance"]:checked')?.value || '';
  let perAmount = 0;
  if (distVal === '3-10') perAmount = 6000;
  else if (distVal === '10+') perAmount = 9000;
  const count = parseInt(document.getElementById('trTripCount').value) || 0;
  const total = perAmount * count;
  document.getElementById('trTotalAmount').value = total > 0 ? total.toLocaleString() + '원' : '';
}

function trCheckAppType() {
  const val = document.querySelector('input[name="trAppType"]:checked')?.value;
  const row = document.getElementById('trChangeReasonRow');
  if (row) row.style.display = (val === '변경' || val === '종료') ? '' : 'none';
}

function trCollectData() {
  const distVal = document.querySelector('input[name="trDistance"]:checked')?.value || '';
  let amount = 0;
  if (distVal === '3-10') amount = 6000;
  else if (distVal === '10+') amount = 9000;
  return {
    app_date: document.getElementById('trAppDate').value,
    provider_name: document.getElementById('trProvName').value,
    provider_rep: document.getElementById('trProvRep').value,
    staff_name: document.getElementById('trStaffName').value,
    staff_phone: document.getElementById('trStaffPhone').value,
    staff_addr: document.getElementById('trStaffAddr').value,
    client_name: document.getElementById('trClientName').value,
    client_address: document.getElementById('trClientAddr').value,
    client_phone: document.getElementById('trClientPhone').value,
    distance_range: distVal,
    support_amount: amount,
    trip_count: parseInt(document.getElementById('trTripCount').value) || 0,
    total_amount: amount * (parseInt(document.getElementById('trTripCount').value) || 0),
    service_period_start: document.getElementById('trPeriodStart').value,
    service_period_end: document.getElementById('trPeriodEnd').value,
    app_type: document.querySelector('input[name="trAppType"]:checked')?.value || '신규',
    change_reason: document.getElementById('trChangeReason').value,
    notes: document.getElementById('trNotes').value,
    photo_path: document.getElementById('trPhotoPath').value,
    custom_fields: JSON.stringify(collectCustomFields('tr')),
    claim_org: document.getElementById('trAppClaimOrg')?.value || '',
    claim_rep: document.getElementById('trAppClaimRep')?.value || '',
    manager_id: document.getElementById('trManager').value || null,
    client_id: document.getElementById('trClient').value || null
  };
}

async function trSave() {
  const data = trCollectData();
  const editId = document.getElementById('trEditId').value;
  const photoInput = document.getElementById('trPhotoInput');
  if (photoInput && photoInput.files && photoInput.files[0]) {
    try {
      data.photo_path = await uploadPhoto(photoInput);
      trShowPhotoInForm(data.photo_path);
      document.getElementById('trPhotoPath').value = data.photo_path;
    } catch (e) { showToast('사진 업로드 실패', 'error'); }
  }
  try {
    if (editId) {
      await apiPut(`/api/transport-apps/${editId}`, data);
      showToast('신청서가 수정되었습니다.', 'success');
    } else {
      await apiPost('/api/transport-apps', data);
      showToast('교통지원금 신청서가 저장되었습니다! ✅', 'success');
    }
    trLoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

// 교통지원 양식에 사진 실시간 표시
function trShowPhotoInForm(photoPath) {
  if (!photoPath) return;
  const trPhotoDisplay = document.getElementById('trPhotoDisplay');
  if (trPhotoDisplay) trPhotoDisplay.style.display = 'block';
  const trPhotoImg = document.getElementById('trPhotoImg');
  if (trPhotoImg) trPhotoImg.src = photoPath;
  const trPhotoPrintArea = document.getElementById('trPhotoPrintArea');
  if (trPhotoPrintArea) trPhotoPrintArea.style.display = 'block';
  const trPhotoPrintImg = document.getElementById('trPhotoPrintImg');
  if (trPhotoPrintImg) trPhotoPrintImg.src = photoPath;
}

function trReset() {
  document.getElementById('trEditId').value = '';
  document.getElementById('trPhotoPath').value = '';
  ['trProvName', 'trProvRep', 'trStaffName', 'trStaffPhone', 'trStaffAddr', 'trClientName', 'trClientAddr', 'trClientPhone', 'trChangeReason', 'trNotes'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('trAppDate').value = todayStr();
  document.getElementById('trPeriodStart').value = '';
  document.getElementById('trPeriodEnd').value = '';
  document.getElementById('trSupportAmount').value = '';
  document.getElementById('trTripCount').value = '';
  document.getElementById('trTotalAmount').value = '';
  document.querySelectorAll('input[name="trDistance"]').forEach(r => r.checked = false);
  const newRadio = document.querySelector('input[name="trAppType"][value="신규"]');
  if (newRadio) newRadio.checked = true;
  document.getElementById('trChangeReasonRow').style.display = 'none';
  const trPhotoInput = document.getElementById('trPhotoInput');
  if (trPhotoInput) trPhotoInput.value = '';
  const trPhotoPreview = document.getElementById('trPhotoPreview');
  if (trPhotoPreview) trPhotoPreview.src = '';
  const trPhotoArea = document.getElementById('trPhotoArea');
  if (trPhotoArea) trPhotoArea.classList.remove('has-photo');
  const trPhotoDisplay = document.getElementById('trPhotoDisplay');
  if (trPhotoDisplay) trPhotoDisplay.style.display = 'none';
  const trPhotoPrintArea = document.getElementById('trPhotoPrintArea');
  if (trPhotoPrintArea) trPhotoPrintArea.style.display = 'none';
  renderCustomFields('tr', []);
}

function trFillForm(t) {
  document.getElementById('trEditId').value = t.id;
  document.getElementById('trManager').value = t.manager_id || '';
  document.getElementById('trClient').value = t.client_id || '';
  document.getElementById('trAppDate').value = t.app_date || '';
  document.getElementById('trProvName').value = t.provider_name || '';
  document.getElementById('trProvRep').value = t.provider_rep || '';
  document.getElementById('trStaffName').value = t.staff_name || '';
  document.getElementById('trStaffPhone').value = t.staff_phone || '';
  if (document.getElementById('trStaffAddr')) document.getElementById('trStaffAddr').value = t.staff_addr || '';
  document.getElementById('trClientName').value = t.client_name || '';
  document.getElementById('trClientAddr').value = t.client_address || '';
  document.getElementById('trClientPhone').value = t.client_phone || '';
  document.getElementById('trPeriodStart').value = t.service_period_start || '';
  document.getElementById('trPeriodEnd').value = t.service_period_end || '';
  document.getElementById('trChangeReason').value = t.change_reason || '';
  document.getElementById('trNotes').value = t.notes || '';
  document.getElementById('trPhotoPath').value = t.photo_path || '';
  if (document.getElementById('trAppClaimOrg')) document.getElementById('trAppClaimOrg').value = t.claim_org || t.provider_name || '';
  if (document.getElementById('trAppClaimRep')) document.getElementById('trAppClaimRep').value = t.claim_rep || t.provider_rep || '';
  if (t.photo_path) {
    const trPhotoDisplay = document.getElementById('trPhotoDisplay');
    if (trPhotoDisplay) trPhotoDisplay.style.display = 'block';
    const trPhotoImg = document.getElementById('trPhotoImg');
    if (trPhotoImg) trPhotoImg.src = t.photo_path;
    const trPhotoPrintArea = document.getElementById('trPhotoPrintArea');
    if (trPhotoPrintArea) trPhotoPrintArea.style.display = 'block';
    const trPhotoPrintImg = document.getElementById('trPhotoPrintImg');
    if (trPhotoPrintImg) trPhotoPrintImg.src = t.photo_path;
  }
  try { renderCustomFields('tr', JSON.parse(t.custom_fields || '[]')); } catch(e) {}
  const appTypeRadio = document.querySelector(`input[name="trAppType"][value="${t.app_type || '신규'}"]`);
  if (appTypeRadio) appTypeRadio.checked = true;
  trCheckAppType();
  document.getElementById('trTripCount').value = t.trip_count || '';
  if (t.distance_range) {
    const distRadio = document.querySelector(`input[name="trDistance"][value="${t.distance_range}"]`);
    if (distRadio) distRadio.checked = true;
    trCalcAmount();
  }
}

async function trLoadList() {
  try {
    const list = await apiGet('/api/transport-apps');
    const el = document.getElementById('trSavedList');
    const empty = document.getElementById('trSavedEmpty');
    if (!list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(t => {
      const amt = t.distance_range === '3-10' ? '6,000원/회' : t.distance_range === '10+' ? '9,000원/회' : (t.distance_range === '10-20' ? '6,000원/회' : t.distance_range === '20+' ? '9,000원/회' : '-');
      const countInfo = t.trip_count ? ` × ${t.trip_count}회 = ${(t.total_amount||0).toLocaleString()}원` : '';
      return `<div class="saved-item" onclick="trLoadItem(${t.id})">
        <div class="saved-item-info">
          <div class="saved-item-title">${t.client_name || '미입력'} - ${t.app_type || '신규'}</div>
          <div class="saved-item-sub">인력: ${t.staff_name || '-'} | 지원금: ${amt}${countInfo} | 기간: ${t.service_period_start || '?'} ~ ${t.service_period_end || '?'}</div>
        </div>
        <div class="saved-item-actions">
          <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();trDeleteItem(${t.id})">🗑️</button>
        </div>
      </div>`;
    }).join('');
  } catch (e) { console.error('Transport list error:', e); }
}

async function trLoadItem(id) {
  try {
    const t = await apiGet(`/api/transport-apps/${id}`);
    trReset();
    trFillForm(t);
    showToast('신청서를 불러왔습니다.', 'success');
    document.getElementById('transportPaper').scrollIntoView({ behavior: 'smooth' });
  } catch (e) { showToast('불러오기 실패', 'error'); }
}

async function trDeleteItem(id) {
  if (!confirm('신청서를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/transport-apps/${id}`);
    showToast('삭제되었습니다.', 'success');
    trLoadList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

function trPrint() {
  const sec = document.getElementById('sec-transport');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// DISPATCH (제공인력 2인 파견 지원 신청서)
// ═══════════════════════════════════════
function dpAutoFill() {
  const mid = document.getElementById('dpManager').value;
  const m = managers.find(x => x.id == mid);
  if (m) {
    document.getElementById('dpStaff1Name').value = m.name;
    document.getElementById('dpStaff1Phone').value = m.phone || '';
  }
  // Pre-fill provider defaults
  const el = (id) => document.getElementById(id);
  if (el('dpProvName') && !el('dpProvName').value) el('dpProvName').value = settings.provider_name || '산청인애노인통합지원센터';
  if (el('dpProvRep') && !el('dpProvRep').value) el('dpProvRep').value = settings.provider_rep || '김일득';
  if (el('dpProvPhone') && !el('dpProvPhone').value) el('dpProvPhone').value = settings.provider_phone || '055-973-8642';
}

function dpAutoFillClient() {
  const cid = document.getElementById('dpClient').value;
  const c = clients.find(x => x.id == cid);
  if (c) {
    document.getElementById('dpClientName').value = c.name;
    document.getElementById('dpClientBirth').value = c.birth_date || '';
    document.getElementById('dpClientAddr').value = c.address || '';
    document.getElementById('dpClientPhone').value = c.phone || '';
    const genderRadios = document.querySelectorAll('input[name="dpGender"]');
    genderRadios.forEach(r => r.checked = r.value === c.gender);
  }
}

function dpCollectData() {
  return {
    app_date: document.getElementById('dpAppDate').value,
    provider_name: document.getElementById('dpProvName').value,
    provider_rep: document.getElementById('dpProvRep').value,
    provider_phone: document.getElementById('dpProvPhone').value,
    client_name: document.getElementById('dpClientName').value,
    client_birth: document.getElementById('dpClientBirth').value,
    client_gender: document.querySelector('input[name="dpGender"]:checked')?.value || '',
    client_address: document.getElementById('dpClientAddr').value,
    client_phone: document.getElementById('dpClientPhone').value,
    staff1_name: document.getElementById('dpStaff1Name').value,
    staff1_phone: document.getElementById('dpStaff1Phone').value,
    staff2_name: document.getElementById('dpStaff2Name').value,
    staff2_phone: document.getElementById('dpStaff2Phone').value,
    service_type: document.getElementById('dpServiceType').value,
    contract_period_start: document.getElementById('dpPeriodStart').value,
    contract_period_end: document.getElementById('dpPeriodEnd').value,
    health_conditions: document.getElementById('dpHealthConditions').value,
    risk_factors: document.getElementById('dpRiskFactors').value,
    justification: document.getElementById('dpJustification').value,
    notes: document.getElementById('dpNotes').value,
    photo_path: document.getElementById('dpPhotoPath')?.value || '',
    custom_fields: JSON.stringify(collectCustomFields('dp')),
    manager_id: document.getElementById('dpManager').value || null,
    client_id: document.getElementById('dpClient').value || null
  };
}

async function dpSave() {
  const data = dpCollectData();
  const editId = document.getElementById('dpEditId').value;
  const photoInput = document.getElementById('dpPhotoInput');
  if (photoInput && photoInput.files && photoInput.files[0]) {
    try {
      data.photo_path = await uploadPhoto(photoInput);
      dpShowPhotoInForm(data.photo_path);
      document.getElementById('dpPhotoPath').value = data.photo_path;
    } catch (e) { showToast('사진 업로드 실패', 'error'); }
  }
  try {
    if (editId) {
      await apiPut(`/api/dispatch-apps/${editId}`, data);
      showToast('신청서가 수정되었습니다.', 'success');
    } else {
      await apiPost('/api/dispatch-apps', data);
      showToast('2인 파견 신청서가 저장되었습니다! ✅', 'success');
    }
    dpLoadList();
  } catch (e) { showToast('저장 실패: ' + e.message, 'error'); }
}

// 2인파견 양식에 사진 실시간 표시
function dpShowPhotoInForm(photoPath) {
  if (!photoPath) return;
  const dpPhotoDisplay = document.getElementById('dpPhotoDisplay');
  if (dpPhotoDisplay) dpPhotoDisplay.style.display = 'block';
  const dpPhotoImg = document.getElementById('dpPhotoImg');
  if (dpPhotoImg) dpPhotoImg.src = photoPath;
  const dpPhotoPrintArea = document.getElementById('dpPhotoPrintArea');
  if (dpPhotoPrintArea) dpPhotoPrintArea.style.display = 'block';
  const dpPhotoPrintImg = document.getElementById('dpPhotoPrintImg');
  if (dpPhotoPrintImg) dpPhotoPrintImg.src = photoPath;
}

function dpReset() {
  document.getElementById('dpEditId').value = '';
  ['dpProvName', 'dpProvRep', 'dpProvPhone', 'dpClientName', 'dpClientAddr', 'dpClientPhone', 'dpStaff1Name', 'dpStaff1Phone', 'dpStaff2Name', 'dpStaff2Phone', 'dpHealthConditions', 'dpRiskFactors', 'dpJustification', 'dpNotes'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('dpAppDate').value = todayStr();
  document.getElementById('dpClientBirth').value = '';
  document.getElementById('dpPeriodStart').value = '';
  document.getElementById('dpPeriodEnd').value = '';
  document.getElementById('dpServiceType').value = '가사지원';
  document.querySelectorAll('input[name="dpGender"]').forEach(r => r.checked = false);
  const dpPhotoInput = document.getElementById('dpPhotoInput');
  if (dpPhotoInput) dpPhotoInput.value = '';
  const dpPhotoPreview = document.getElementById('dpPhotoPreview');
  if (dpPhotoPreview) dpPhotoPreview.src = '';
  const dpPhotoArea = document.getElementById('dpPhotoArea');
  if (dpPhotoArea) dpPhotoArea.classList.remove('has-photo');
  const dpPhotoDisplay = document.getElementById('dpPhotoDisplay');
  if (dpPhotoDisplay) dpPhotoDisplay.style.display = 'none';
  const dpPhotoPrintArea = document.getElementById('dpPhotoPrintArea');
  if (dpPhotoPrintArea) dpPhotoPrintArea.style.display = 'none';
  const dpPhotoPath = document.getElementById('dpPhotoPath');
  if (dpPhotoPath) dpPhotoPath.value = '';
  renderCustomFields('dp', []);
}

function dpFillForm(d) {
  document.getElementById('dpEditId').value = d.id;
  document.getElementById('dpManager').value = d.manager_id || '';
  document.getElementById('dpClient').value = d.client_id || '';
  document.getElementById('dpAppDate').value = d.app_date || '';
  document.getElementById('dpProvName').value = d.provider_name || '';
  document.getElementById('dpProvRep').value = d.provider_rep || '';
  document.getElementById('dpProvPhone').value = d.provider_phone || '';
  document.getElementById('dpClientName').value = d.client_name || '';
  document.getElementById('dpClientBirth').value = d.client_birth || '';
  document.getElementById('dpClientAddr').value = d.client_address || '';
  document.getElementById('dpClientPhone').value = d.client_phone || '';
  document.getElementById('dpStaff1Name').value = d.staff1_name || '';
  document.getElementById('dpStaff1Phone').value = d.staff1_phone || '';
  document.getElementById('dpStaff2Name').value = d.staff2_name || '';
  document.getElementById('dpStaff2Phone').value = d.staff2_phone || '';
  document.getElementById('dpServiceType').value = d.service_type || '가사지원';
  document.getElementById('dpPeriodStart').value = d.contract_period_start || '';
  document.getElementById('dpPeriodEnd').value = d.contract_period_end || '';
  document.getElementById('dpHealthConditions').value = d.health_conditions || '';
  document.getElementById('dpRiskFactors').value = d.risk_factors || '';
  document.getElementById('dpJustification').value = d.justification || '';
  document.getElementById('dpNotes').value = d.notes || '';
  document.querySelectorAll('input[name="dpGender"]').forEach(r => r.checked = r.value === d.client_gender);
  const dpPhotoPath = document.getElementById('dpPhotoPath');
  if (dpPhotoPath) dpPhotoPath.value = d.photo_path || '';
  if (d.photo_path) {
    const dpPhotoDisplay = document.getElementById('dpPhotoDisplay');
    if (dpPhotoDisplay) dpPhotoDisplay.style.display = 'block';
    const dpPhotoImg = document.getElementById('dpPhotoImg');
    if (dpPhotoImg) dpPhotoImg.src = d.photo_path;
    const dpPhotoPrintArea = document.getElementById('dpPhotoPrintArea');
    if (dpPhotoPrintArea) dpPhotoPrintArea.style.display = 'block';
    const dpPhotoPrintImg = document.getElementById('dpPhotoPrintImg');
    if (dpPhotoPrintImg) dpPhotoPrintImg.src = d.photo_path;
  }
  try { renderCustomFields('dp', JSON.parse(d.custom_fields || '[]')); } catch(e) {}
}

async function dpLoadList() {
  try {
    const list = await apiGet('/api/dispatch-apps');
    const el = document.getElementById('dpSavedList');
    const empty = document.getElementById('dpSavedEmpty');
    if (!list.length) { el.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    el.innerHTML = list.map(d => `<div class="saved-item" onclick="dpLoadItem(${d.id})">
      <div class="saved-item-info">
        <div class="saved-item-title">${d.client_name || '미입력'} - ${d.service_type || '-'}</div>
        <div class="saved-item-sub">인력1: ${d.staff1_name || '-'} | 인력2: ${d.staff2_name || '-'} | 기간: ${d.contract_period_start || '?'} ~ ${d.contract_period_end || '?'}</div>
      </div>
      <div class="saved-item-actions">
        <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();dpDeleteItem(${d.id})">🗑️</button>
      </div>
    </div>`).join('');
  } catch (e) { console.error('Dispatch list error:', e); }
}

async function dpLoadItem(id) {
  try {
    const d = await apiGet(`/api/dispatch-apps/${id}`);
    dpReset();
    dpFillForm(d);
    showToast('신청서를 불러왔습니다.', 'success');
    document.getElementById('dispatchPaper').scrollIntoView({ behavior: 'smooth' });
  } catch (e) { showToast('불러오기 실패', 'error'); }
}

async function dpDeleteItem(id) {
  if (!confirm('신청서를 삭제하시겠습니까?')) return;
  try {
    await apiDelete(`/api/dispatch-apps/${id}`);
    showToast('삭제되었습니다.', 'success');
    dpLoadList();
  } catch (e) { showToast('삭제 실패', 'error'); }
}

function dpPrint() {
  const sec = document.getElementById('sec-dispatch');
  sec.classList.add('print-active');
  window.print();
  setTimeout(() => sec.classList.remove('print-active'), 500);
}

// ═══════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Init socket
  initSocket();

  // Tab navigation
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // Photo previews (no duplicates)
  setupPhotoPreview('clockPhotoInput', 'clockPhotoPreview', 'clockPhotoArea');
  setupPhotoPreview('clockOutPhotoInput', 'clockOutPhotoPreview', 'clockOutPhotoArea');
  setupPhotoPreview('clockOutPhotoInputInline', 'clockOutPhotoPreviewInline', 'clockOutPhotoAreaInline');
  setupPhotoPreview('invPhotoInput', 'invPhotoPreview', 'invPhotoArea');
  setupPhotoPreview('trPhotoInput', 'trPhotoPreview', 'trPhotoArea');
  setupPhotoPreview('dpPhotoInput', 'dpPhotoPreview', 'dpPhotoArea');

  // ─── 출퇴근 ↔ 일일결과 매니저/대상자 드롭다운 동기화 ───
  const clockMgr = document.getElementById('clockManager');
  const clockCli = document.getElementById('clockClient');
  // dfManager/dfClient가 없으면 clockManager/clockClient를 직접 사용
  if (clockMgr) {
    clockMgr.addEventListener('change', () => {
      dfAutoFill();
    });
  }
  if (clockCli) {
    clockCli.addEventListener('change', () => {
      dfAutoFillClient();
    });
  }

  // Signature canvas
  dfInitSign();

  // Set default dates
  document.getElementById('dfServiceDate').value = todayStr();
  document.getElementById('dfSubmitDate').value = todayStr();
  document.getElementById('dfListMonth').value = currentMonthStr();
  const filterDate = document.getElementById('filterDate');
  if (filterDate) filterDate.value = todayStr();
  const summaryMonth = document.getElementById('summaryMonth');
  if (summaryMonth) summaryMonth.value = currentMonthStr();
  const printMonth = document.getElementById('printMonth');
  if (printMonth) printMonth.value = currentMonthStr();
  const invMonth = document.getElementById('invMonth');
  if (invMonth) invMonth.value = currentMonthStr();
  const invDate = document.getElementById('invDate');
  if (invDate) invDate.value = todayStr();
  const invMonthField = document.getElementById('invMonthField');
  if (invMonthField) invMonthField.value = currentMonthStr();
  const ctDate = document.getElementById('ctDate');
  if (ctDate) ctDate.value = todayStr();
  const trAppDate = document.getElementById('trAppDate');
  if (trAppDate) trAppDate.value = todayStr();
  const dpAppDate = document.getElementById('dpAppDate');
  if (dpAppDate) dpAppDate.value = todayStr();

  // Auto-age calculation on birth date change
  const dfUserBirth = document.getElementById('dfUserBirth');
  if (dfUserBirth) dfUserBirth.addEventListener('change', () => {
    document.getElementById('dfUserAge').value = calcAge(dfUserBirth.value);
  });

  // Transport app type change listener
  document.querySelectorAll('input[name="trAppType"]').forEach(r => {
    r.addEventListener('change', trCheckAppType);
  });

  // Clock update
  updateClock();
  setInterval(updateClock, 1000);

  // Load initial data
  loadManagers();
  loadClients();
  loadSettings();
  loadDashboard();
  loadLiveStatus();

  // Invoice: real-time mirror sync on input changes
  const invMirrorSources = ['invDate', 'invMonthField', 'invProvName', 'invProvRep', 'invProvPhone', 'invProvAddr', 'invProvBizNo', 'invProvStaff', 'invClientName', 'invClientBirth', 'invClientAddr', 'invClientPhone', 'invClientGrade', 'invIncomeTierText', 'invServiceType', 'invServiceDates', 'invTotalHours', 'invBasicFee', 'invSurchargeFee', 'invPersonalBurden', 'invGovSupport', 'invClaimAmount', 'invWorkDays', 'invBankName', 'invAccountNo', 'invAccountHolder', 'invNotes', 'invBurdenRate', 'invClaimantTitle', 'invClaimantName'];
  invMirrorSources.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', invSyncMirrors);
      el.addEventListener('change', invSyncMirrors);
    }
  });
  document.querySelectorAll('input[name="invGender"]').forEach(r => {
    r.addEventListener('change', invSyncMirrors);
  });

  // 서식10: 변경사항 라디오 토글
  document.querySelectorAll('input[name="rpt10Change"]').forEach(r => {
    r.addEventListener('change', () => {
      const crow = document.getElementById('rpt10ChangeRow');
      if (crow) crow.style.display = r.value === '변경됨' ? '' : 'none';
    });
  });



  // Auto-refresh dashboard every 30s
  setInterval(() => {
    if (currentTab === 'dashboard') { loadDashboard(); loadLiveStatus(); loadDashboardPhotos(); }
  }, 60000);

  // Auto-refresh clock tab (today status + photos) every 30s
  setInterval(() => {
    if (currentTab === 'clock') { loadTodayClock(); }
  }, 30000);

  // 로그인 상태 복원
  const savedRole = sessionStorage.getItem('gapcare_role');
  if (savedRole) {
    doLogin(savedRole);
  }
});
