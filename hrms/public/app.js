// Garissa County HRMS — app.js
// Approved Staff Establishment: 27 March 2026 | 4,755 cadres
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithPopup, GoogleAuthProvider, createUserWithEmailAndPassword,
  signInWithEmailAndPassword, sendPasswordResetEmail, onAuthStateChanged, signOut as fbSignOut } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc, updateDoc, collection,
  query, where, getDocs, addDoc, serverTimestamp, orderBy, limit } from 'firebase/firestore';
import { getStorage, ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';
import { getAnalytics, logEvent } from 'firebase/analytics';

// ─── Firebase Config ─────────────────────────────────────────────────────────
const firebaseConfig = {
  apiKey: "AIzaSyBHgfzfByeRgKMNMua0Od7GJe8qqGkGfg0",
  authDomain: "garissahrm.firebaseapp.com",
  projectId: "garissahrm",
  storageBucket: "garissahrm.firebasestorage.app",
  messagingSenderId: "508536823542",
  appId: "1:508536823542:web:a84f7a7d8eeae8017916d7",
  measurementId: "G-61M0X5NPPK"
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);
const analytics = getAnalytics(app);
const googleProvider = new GoogleAuthProvider();

// ─── 2026 Approved Staff Establishment Data ───────────────────────────────────
const DEPARTMENTS = [
  {
    id: 'governor',
    name: 'Office of the Governor',
    shortName: 'Office of the Governor',
    color: '#1565C0',
    bg: 'linear-gradient(135deg,#1565C0,#0D47A1)',
    icon: 'account_balance',
    authorized: 100,
    inPost: 88,
    chiefOfficers: [],
    head: 'H.E. The Governor',
    headTitle: 'Governor, County Government of Garissa',
    directorates: [
      { name: 'Office of the Governor', authorized: 29, inPost: 36 },
      { name: 'Office of the Deputy Governor', authorized: 12, inPost: 14 },
      { name: 'Office of the County Secretary', authorized: 25, inPost: 25 },
      { name: 'Office of the County Attorney', authorized: 26, inPost: 8 },
      { name: 'Directorate of Press Services', authorized: 5, inPost: 5 },
      { name: 'Chief of Staff', authorized: 3, inPost: 0 }
    ],
    keyPosts: ['Deputy Governor','County Secretary & HPS','County Attorney (T)','Chief of Staff (S)',
      'Director, Press Services','Advisor — Political Affairs (R)','Advisor — Economic Affairs (R)',
      'Advisor — Legal Affairs (R)','Advisor — Gender & Social Affairs (R)']
  },
  {
    id: 'county-affairs',
    name: 'Department of County Affairs, Public Service, Administration, Peace, Donor Coordination, Resource Mobilization, Disaster Management & Intergovernmental Relations',
    shortName: 'County Affairs & Public Service',
    color: '#2E7D32',
    bg: 'linear-gradient(135deg,#2E7D32,#1B5E20)',
    icon: 'groups',
    authorized: 505,
    inPost: 263,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for County Affairs & Public Service',
    chiefOfficers: [
      'Chief Officer — County Affairs, Administration & Devolved Units',
      'Chief Officer — Public Service, Performance & Delivery Management',
      'Chief Officer — Intergovernmental Relations & Public Participation',
      'Chief Officer — Donor, Partners Coordination & Resource Mobilization',
      'Chief Officer — Peace, Community Cohesion & Prevention of Radicalization',
      'Chief Officer — Special Programs & Disaster Management'
    ],
    directorates: [
      { name: 'Directorate of County Affairs & Administration', authorized: 401, inPost: 141 },
      { name: 'Directorate of Donor, Partnership & Resource Mobilization', authorized: 10, inPost: 10 },
      { name: 'Directorate of Special Programmes & Disaster Management', authorized: 11, inPost: 11 },
      { name: 'Directorate of Public Service, Performance & Delivery Unit', authorized: 35, inPost: 50 },
      { name: 'Directorate of HRM & Development', authorized: 23, inPost: 23 },
      { name: 'Directorate of Inter-Governmental Relations & Public Participation', authorized: 15, inPost: 17 },
      { name: 'Directorate of Peace & Cohesion', authorized: 10, inPost: 10 }
    ]
  },
  {
    id: 'water',
    name: 'Department of Water, Irrigation, Environment, Climate Change, Energy & Natural Resources',
    shortName: 'Water, Irrigation & Environment',
    color: '#0277BD',
    bg: 'linear-gradient(135deg,#0277BD,#01579B)',
    icon: 'water_drop',
    authorized: 219,
    inPost: 215,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Water, Irrigation, Environment, Energy & Natural Resources',
    chiefOfficers: [
      'Chief Officer — Water & Sanitation',
      'Chief Officer — Irrigation',
      'Chief Officer — Environment & Climate Change',
      'Chief Officer — Energy & Natural Resources'
    ],
    directorates: [
      { name: 'Directorate of Water Services', authorized: 172, inPost: 170 },
      { name: 'Directorate of Irrigation Services', authorized: 9, inPost: 9 },
      { name: 'Directorate of Environment & Climate Change', authorized: 25, inPost: 16 },
      { name: 'Directorate of Energy, Natural Resource & Wildlife', authorized: 18, inPost: 18 }
    ]
  },
  {
    id: 'roads',
    name: 'Department of Roads, Transport & Public Works',
    shortName: 'Roads, Transport & Public Works',
    color: '#E65100',
    bg: 'linear-gradient(135deg,#E65100,#BF360C)',
    icon: 'directions_car',
    authorized: 80,
    inPost: 73,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Roads, Transport & Public Works',
    chiefOfficers: ['Chief Officer — Roads, Transport & Public Works'],
    directorates: [
      { name: 'Directorate of Roads', authorized: 30, inPost: 28 },
      { name: 'Directorate of Public Works', authorized: 25, inPost: 22 },
      { name: 'Directorate of Transport & Fleet Management', authorized: 25, inPost: 23 }
    ]
  },
  {
    id: 'lands',
    name: 'Department of Lands, Physical Planning, Urban Development & Housing',
    shortName: 'Lands, Planning & Housing',
    color: '#6A1B9A',
    bg: 'linear-gradient(135deg,#6A1B9A,#4A148C)',
    icon: 'landscape',
    authorized: 480,
    inPost: 409,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Lands, Physical Planning, Urban Development & Housing',
    chiefOfficers: [
      'Chief Officer — Lands, Survey & Physical Planning',
      'Chief Officer — Urban Development',
      'Chief Officer — Housing'
    ],
    directorates: [
      { name: 'Directorate of Urban Development', authorized: 208, inPost: 209 },
      { name: 'Garissa Municipality', authorized: 9, inPost: 13 },
      { name: 'Market & Social Development', authorized: 18, inPost: 18 },
      { name: 'Fire Section', authorized: 33, inPost: 33 },
      { name: 'Building Plan & Control Management', authorized: 11, inPost: 11 },
      { name: 'Ijara Municipality', authorized: 59, inPost: 58 },
      { name: 'Modogashe Municipality', authorized: 34, inPost: 21 },
      { name: 'Dadaab Municipality', authorized: 30, inPost: 8 },
      { name: 'Balambala Municipality', authorized: 31, inPost: 1 },
      { name: 'Directorate of Lands, Survey & Physical Planning', authorized: 30, inPost: 25 },
      { name: 'Directorate of Housing', authorized: 13, inPost: 9 }
    ],
    municipalities: ['Garissa','Masalani','Dadaab-Hagardere','Bura','Modogashe','Balambala']
  },
  {
    id: 'education',
    name: 'Department of Education, Vocational Training, Library Services, Information & ICT',
    shortName: 'Education, ICT & Library Services',
    color: '#00695C',
    bg: 'linear-gradient(135deg,#00695C,#004D40)',
    icon: 'school',
    authorized: 697,
    inPost: 605,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Education, Vocational Training, ICT & Library Services',
    chiefOfficers: [
      'Chief Officer — ECDE',
      'Chief Officer — Vocational Training',
      'Chief Officer — Information & Library Services',
      'Chief Officer — ICT & E-Government'
    ],
    directorates: [
      { name: 'Directorate of Education, ECDE', authorized: 604, inPost: 515 },
      { name: 'Directorate of ICT & E-Government', authorized: 15, inPost: 15 },
      { name: 'Directorate of Information & Library Services', authorized: 23, inPost: 23 },
      { name: 'Directorate of Vocational & Technical Training', authorized: 55, inPost: 52 }
    ]
  },
  {
    id: 'trade',
    name: 'Department of Trade, Investment, Industrialization & Enterprise Development',
    shortName: 'Trade, Investment & Enterprise',
    color: '#F57F17',
    bg: 'linear-gradient(135deg,#F57F17,#E65100)',
    icon: 'storefront',
    authorized: 72,
    inPost: 77,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Trade, Investment, Industrialization & Enterprise Development',
    chiefOfficers: [
      'Chief Officer — Trade & Investments',
      'Chief Officer — MSMEs & Industrialization'
    ],
    directorates: [
      { name: 'Directorate of Trade & Investment', authorized: 50, inPost: 55 },
      { name: 'Directorate of Industrialization & Enterprise Development', authorized: 22, inPost: 22 }
    ]
  },
  {
    id: 'finance',
    name: 'Department of Finance & Economic Planning',
    shortName: 'Finance & Economic Planning',
    color: '#1A237E',
    bg: 'linear-gradient(135deg,#1A237E,#283593)',
    icon: 'account_balance_wallet',
    authorized: 200,
    inPost: 213,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Finance & Economic Planning',
    chiefOfficers: [
      'Chief Officer — Finance (County Treasury)',
      'Chief Officer — Economic Planning, Budget & Statistics',
      'Chief Officer — Revenue Management'
    ],
    directorates: [
      { name: 'Directorate of Accounting Services & Economic Planning', authorized: 79, inPost: 80 },
      { name: 'Directorate of Revenue Management', authorized: 67, inPost: 67 },
      { name: 'Directorate of Procurement/Supply Chain Management', authorized: 51, inPost: 58 }
    ]
  },
  {
    id: 'culture',
    name: 'Department of Culture, Gender, Youth & Sport, Social Services & PWDs',
    shortName: 'Culture, Gender, Youth & Sports',
    color: '#880E4F',
    bg: 'linear-gradient(135deg,#880E4F,#6A1B9A)',
    icon: 'diversity_3',
    authorized: 90,
    inPost: 84,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Culture, Gender, Youth & Sport, Social Services & PWDs',
    chiefOfficers: [
      'Chief Officer — Culture & Gender Affairs',
      'Chief Officer — Youth & Sports',
      'Chief Officer — Social Services & PWDs'
    ],
    directorates: [
      { name: 'Directorate of Gender & Culture Affairs', authorized: 54, inPost: 54 },
      { name: 'Directorate of PWDs & Social Services', authorized: 11, inPost: 11 },
      { name: 'Directorate of Youth & Sports', authorized: 22, inPost: 16 }
    ]
  },
  {
    id: 'agriculture',
    name: 'Department of Agriculture, Livestock, Veterinary, Fisheries & Cooperatives',
    shortName: 'Agriculture, Livestock & Fisheries',
    color: '#33691E',
    bg: 'linear-gradient(135deg,#33691E,#1B5E20)',
    icon: 'agriculture',
    authorized: 250,
    inPost: 167,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Agriculture, Livestock, Veterinary, Fisheries & Cooperatives',
    chiefOfficers: [
      'Chief Officer — Agriculture',
      'Chief Officer — Livestock & Pastoral Economy',
      'Chief Officer — Fisheries',
      'Chief Officer — Cooperatives Development'
    ],
    directorates: [
      { name: 'Directorate of Livestock & Veterinary Services', authorized: 55, inPost: 55 },
      { name: 'Directorate of Agriculture', authorized: 171, inPost: 98 },
      { name: 'Directorate of Fisheries', authorized: 6, inPost: 6 },
      { name: 'Directorate of Irrigation', authorized: 15, inPost: 5 }
    ]
  },
  {
    id: 'health',
    name: 'Department of Health & Sanitation Services',
    shortName: 'Health & Sanitation Services',
    color: '#B71C1C',
    bg: 'linear-gradient(135deg,#B71C1C,#880E4F)',
    icon: 'local_hospital',
    authorized: 1562,
    inPost: 1482,
    head: 'County Executive Committee Member',
    headTitle: 'CECM for Health & Sanitation Services',
    chiefOfficers: [
      'Chief Officer — Medical Services',
      'Chief Officer — Public Health & Sanitation'
    ],
    directorates: [
      { name: 'Directorate of Medical Services', authorized: 900, inPost: 860 },
      { name: 'Directorate of Public Health & Sanitation', authorized: 350, inPost: 330 },
      { name: 'Directorate of Nursing Services', authorized: 200, inPost: 185 },
      { name: 'Directorate of Health Management & Support', authorized: 112, inPost: 107 }
    ]
  },
  {
    id: 'cpsb',
    name: 'Garissa County Public Service Board (GCPSB)',
    shortName: 'County Public Service Board',
    color: '#37474F',
    bg: 'linear-gradient(135deg,#37474F,#263238)',
    icon: 'gavel',
    authorized: 500,
    inPost: 500,
    head: 'Chairperson, GCPSB',
    headTitle: 'Garissa County Public Service Board',
    chiefOfficers: ['Secretary/CEO, GCPSB'],
    directorates: [
      { name: 'Office of the Chairperson', authorized: 5, inPost: 5 },
      { name: 'Secretariat & Administration', authorized: 20, inPost: 20 },
      { name: 'Recruitment & Talent Management', authorized: 15, inPost: 15 }
    ]
  }
];

// ─── HR Documents (Kenya PSC Required) ───────────────────────────────────────
const HR_DOCUMENTS = [
  { id:'nid', name:'National Identity Card', required:true, category:'Personal' },
  { id:'kra', name:'KRA PIN Certificate', required:true, category:'Tax' },
  { id:'nhif', name:'NHIF Card / Certificate', required:true, category:'Insurance' },
  { id:'nssf', name:'NSSF Card / Certificate', required:true, category:'Insurance' },
  { id:'academic', name:'Academic Certificates (All)', required:true, category:'Qualifications' },
  { id:'professional', name:'Professional Certificates', required:false, category:'Qualifications' },
  { id:'appointment', name:'First Appointment Letter', required:true, category:'Employment' },
  { id:'confirmation', name:'Confirmation in Appointment Letter', required:true, category:'Employment' },
  { id:'promotion', name:'Promotion Letter(s)', required:false, category:'Employment' },
  { id:'hpf', name:'Housing Provident Fund', required:false, category:'Financial' },
  { id:'birth', name:'Birth Certificate', required:true, category:'Personal' },
  { id:'marriage', name:'Marriage Certificate (if applicable)', required:false, category:'Personal' },
  { id:'passport', name:'Passport Photo (Recent)', required:true, category:'Personal' },
  { id:'bank', name:'Bank Account Evidence', required:true, category:'Financial' },
  { id:'medical', name:'Medical Fitness Certificate', required:true, category:'Health' },
  { id:'police', name:'Certificate of Good Conduct (Police Clearance)', required:true, category:'Background' },
  { id:'helb', name:'HELB Clearance Certificate', required:false, category:'Financial' },
  { id:'ethics', name:'Ethics & Anti-Corruption Clearance', required:true, category:'Integrity' }
];

// ─── Performance Contracting Criteria ────────────────────────────────────────
const PC_CRITERIA = [
  { id:'financial', name:'Financial Management & Revenue', weight:20, description:'Budget absorption, revenue collection, PFM compliance' },
  { id:'service', name:'Service Delivery', weight:25, description:'Quality and timeliness of services to citizens' },
  { id:'hr', name:'Human Resource Management', weight:15, description:'Staff welfare, training, discipline, capacity building' },
  { id:'governance', name:'Governance & Accountability', weight:15, description:'Transparency, audit compliance, records management' },
  { id:'projects', name:'Projects & Programme Delivery', weight:15, description:'Implementation of county development projects' },
  { id:'innovation', name:'Innovation & ICT Adoption', weight:5, description:'Use of technology and innovative service delivery' },
  { id:'partnerships', name:'Partnerships & Resource Mobilization', weight:5, description:'Donor engagement, inter-governmental relations' }
];

// ─── SPAS Forms ──────────────────────────────────────────────────────────────
const SPAS_FORM1 = {
  jobGroups: ['A','B','C','D','E','F','G','H'],
  label: 'Form 1 — Job Groups A–H (Non-Supervisory)',
  sections: [
    { id:'productivity', name:'Productivity & Work Output', maxScore:40,
      items:['Quality of work output','Quantity of work completed','Timeliness of assignments','Initiative and creativity'] },
    { id:'technical', name:'Technical & Professional Skills', maxScore:20,
      items:['Knowledge of job','Application of skills','Problem solving','Use of technology'] },
    { id:'conduct', name:'Conduct & Discipline', maxScore:20,
      items:['Punctuality and attendance','Adherence to rules','Dress code','Ethical conduct'] },
    { id:'teamwork', name:'Teamwork & Cooperation', maxScore:10,
      items:['Cooperation with colleagues','Communication','Team participation','Support to supervisors'] },
    { id:'development', name:'Self Development', maxScore:10,
      items:['Training attended','Skills acquired','Goal achievement','Improvement noted'] }
  ]
};

const SPAS_FORM2 = {
  jobGroups: ['J','K','L','M','N','P','Q','R','S','T'],
  label: 'Form 2 — Job Groups J–T (Supervisory/Management)',
  sections: [
    { id:'planning', name:'Planning & Organisation', maxScore:25,
      items:['Work planning','Target setting','Resource allocation','Priority setting'] },
    { id:'leadership', name:'Leadership & Supervision', maxScore:25,
      items:['Staff motivation','Performance management','Delegation','Decision making'] },
    { id:'results', name:'Results & Accountability', maxScore:20,
      items:['Achievement of targets','Budget management','Reporting','Accountability'] },
    { id:'stakeholder', name:'Stakeholder Management', maxScore:15,
      items:['Public relations','Inter-departmental collaboration','Customer satisfaction','Communication'] },
    { id:'innovation', name:'Innovation & Change Management', maxScore:15,
      items:['Implementation of new ideas','Adoption of technology','Process improvement','Change leadership'] }
  ]
};

// ─── Skills Audit Domains ─────────────────────────────────────────────────────
const SKILLS_DOMAINS = [
  { id:'leadership', name:'Leadership & Management', icon:'manage_accounts',
    competencies:['Strategic thinking','People management','Decision making','Team building','Conflict resolution'] },
  { id:'finance', name:'Financial Management', icon:'account_balance_wallet',
    competencies:['Budgeting','Financial reporting','Revenue management','IFMIS usage','Audit compliance'] },
  { id:'ict', name:'ICT & Digital Literacy', icon:'computer',
    competencies:['Computer literacy','Data management','E-government systems','HRIS-Ke','Cybersecurity awareness'] },
  { id:'legal', name:'Legal & Policy Framework', icon:'gavel',
    competencies:['Constitutional knowledge','County legislation','Public Service rules','Labour laws','Ethics & integrity'] },
  { id:'planning', name:'Planning & M&E', icon:'bar_chart',
    competencies:['Project planning','Monitoring & evaluation','Report writing','CIDP implementation','Statistics'] },
  { id:'hr', name:'Human Resource Management', icon:'groups',
    competencies:['Recruitment','Performance management','Staff welfare','Training & development','Labour relations'] },
  { id:'procurement', name:'Supply Chain Management', icon:'inventory',
    competencies:['PPADA compliance','Procurement planning','Asset management','Contract management','Store management'] },
  { id:'communication', name:'Communication & PR', icon:'campaign',
    competencies:['Written communication','Oral communication','Report preparation','Public relations','Media engagement'] },
  { id:'technical', name:'Technical & Professional', icon:'engineering',
    competencies:['Sector-specific knowledge','Field operations','Technical standards','Professional ethics','Research'] },
  { id:'service', name:'Service Delivery', icon:'support_agent',
    competencies:['Customer care','Citizen engagement','Complaint handling','Service charter','Accessibility'] }
];

// ─── State ────────────────────────────────────────────────────────────────────
let currentUser = null;
let userProfile = null;
let currentPage = 'dashboard';
let profileStep = 1;
const TOTAL_STEPS = 7;

// ─── Utilities ────────────────────────────────────────────────────────────────
function toast(msg, type = 'info', dur = 4000) {
  const c = document.getElementById('toast-container');
  if (!c) {
    const tc = document.createElement('div');
    tc.id = 'toast-container';
    tc.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
    document.body.appendChild(tc);
  }
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  const icons = {success:'check_circle',error:'error',info:'info',warning:'warning'};
  el.innerHTML = `<span class="material-icons" style="font-size:20px;">${icons[type]||'info'}</span><span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), dur);
}

function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const v = document.getElementById('view-' + id);
  if (v) v.classList.add('active');
}

function navigate(page) {
  currentPage = page;
  document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
  const p = document.getElementById('page-' + page);
  if (p) p.style.display = 'block';
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll(`.nav-item`).forEach(n => {
    if (n.getAttribute('onclick')?.includes(`'${page}'`)) n.classList.add('active');
  });
  const titles = {
    dashboard:'Dashboard',profile:'My Profile',documents:'My Documents',
    spas:'SPAS Appraisal',pc:'Performance Contract',skills:'Skills Audit',
    reports:'Reports & Analytics',organogram:'Organisational Structure',
    help:'Help Manual',admin:'Admin Panel'
  };
  const t = document.getElementById('page-title');
  if (t) t.textContent = titles[page] || page;

  if (page === 'profile') renderProfileWizard();
  if (page === 'documents') renderDocuments();
  if (page === 'spas') renderSpas();
  if (page === 'pc') renderPC();
  if (page === 'skills') renderSkills();
  if (page === 'reports') renderReports();
  if (page === 'dashboard') renderDashboard();
  if (page === 'organogram') initOrganogram();
  if (page === 'admin') renderAdmin();
  if (page === 'help') renderHelp();

  if (window.innerWidth < 900) {
    document.getElementById('sidebar').classList.remove('open');
  }
}

window.navigate = navigate;
window.showView = showView;

// ─── Auth ─────────────────────────────────────────────────────────────────────
async function signInWithGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    await ensureUserDoc(result.user);
    logEvent(analytics, 'login', { method: 'google' });
  } catch(e) {
    toast('Google sign-in failed: ' + e.message, 'error');
  }
}

async function signInWithEmail() {
  const email = document.getElementById('login-email')?.value.trim();
  const pwd = document.getElementById('login-password')?.value;
  if (!email || !pwd) { toast('Enter email and password', 'warning'); return; }
  try {
    const result = await signInWithEmailAndPassword(auth, email, pwd);
    await ensureUserDoc(result.user);
    logEvent(analytics, 'login', { method: 'email' });
  } catch(e) {
    toast(e.message, 'error');
  }
}

async function registerWithEmail() {
  const fn = document.getElementById('reg-firstname')?.value.trim();
  const ln = document.getElementById('reg-lastname')?.value.trim();
  const email = document.getElementById('reg-email')?.value.trim();
  const upn = document.getElementById('reg-upn')?.value.trim().toUpperCase();
  const dept = document.getElementById('reg-department')?.value;
  const pwd = document.getElementById('reg-password')?.value;
  const pwd2 = document.getElementById('reg-password2')?.value;
  if (!fn||!ln||!email||!upn||!dept||!pwd) { toast('Fill all required fields','warning'); return; }
  if (pwd !== pwd2) { toast('Passwords do not match','warning'); return; }
  if (pwd.length < 8) { toast('Password must be at least 8 characters','warning'); return; }
  try {
    const cred = await createUserWithEmailAndPassword(auth, email, pwd);
    await setDoc(doc(db,'users',cred.user.uid), {
      uid: cred.user.uid, email, firstName: fn, lastName: ln, displayName: `${fn} ${ln}`,
      upn, department: dept, role:'user', profileComplete: false,
      createdAt: serverTimestamp(), updatedAt: serverTimestamp()
    });
    toast('Account created successfully!', 'success');
    logEvent(analytics, 'sign_up', { method:'email' });
  } catch(e) {
    toast(e.message, 'error');
  }
}

async function ensureUserDoc(fbUser) {
  const ref = doc(db,'users',fbUser.uid);
  const snap = await getDoc(ref);
  if (!snap.exists()) {
    await setDoc(ref, {
      uid: fbUser.uid, email: fbUser.email,
      displayName: fbUser.displayName || fbUser.email,
      photoURL: fbUser.photoURL || null,
      role:'user', profileComplete: false,
      createdAt: serverTimestamp(), updatedAt: serverTimestamp()
    });
  }
}

async function signOut() {
  await fbSignOut(auth);
  currentUser = null; userProfile = null;
  showView('landing');
  toast('Signed out', 'info');
}

async function sendPasswordReset() {
  const email = document.getElementById('login-email')?.value.trim();
  if (!email) { toast('Enter your email address first','warning'); return; }
  try {
    await sendPasswordResetEmail(auth, email);
    toast('Password reset email sent','success');
  } catch(e) {
    toast(e.message,'error');
  }
}

window.signInWithGoogle = signInWithGoogle;
window.signInWithEmail = signInWithEmail;
window.registerWithEmail = registerWithEmail;
window.signOut = signOut;
window.sendPasswordReset = sendPasswordReset;

// ─── Auth State ───────────────────────────────────────────────────────────────
onAuthStateChanged(auth, async user => {
  if (user) {
    currentUser = user;
    const snap = await getDoc(doc(db,'users',user.uid));
    if (snap.exists()) {
      userProfile = snap.data();
      updateSidebarUser();
      showView('app');
      navigate('dashboard');
      if (userProfile.role === 'admin' || userProfile.role === 'hr_director' || userProfile.role === 'hr_officer') {
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = '');
      }
    } else {
      showView('auth');
    }
  } else {
    showView('landing');
  }
});

function updateSidebarUser() {
  if (!userProfile) return;
  const name = userProfile.displayName || `${userProfile.firstName || ''} ${userProfile.lastName || ''}`.trim() || 'Staff';
  const el = document.getElementById('sidebar-name'); if (el) el.textContent = name;
  const re = document.getElementById('sidebar-role'); if (re) re.textContent = userProfile.role || 'Employee';
  const av = document.getElementById('sidebar-avatar');
  if (av) {
    if (userProfile.photoURL) {
      av.innerHTML = `<img src="${userProfile.photoURL}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
    } else {
      av.textContent = (name[0] || 'U').toUpperCase();
    }
  }
}

// ─── Sidebar / Topbar ─────────────────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar')?.classList.toggle('open');
}
window.toggleSidebar = toggleSidebar;

function setAuthTab(tab) {
  document.getElementById('auth-login').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('auth-register').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
}
window.setAuthTab = setAuthTab;

// ─── Department Dropdown Populate ─────────────────────────────────────────────
function populateDeptDropdowns() {
  ['reg-department','profile-department','admin-dept-filter'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const blank = id === 'admin-dept-filter' ? '<option value="">All Departments</option>' : '<option value="">Select Department...</option>';
    el.innerHTML = blank + DEPARTMENTS.map(d => `<option value="${d.id}">${d.shortName}</option>`).join('');
  });
  const orgSel = document.getElementById('dept-organogram-select');
  if (orgSel) {
    orgSel.innerHTML = '<option value="">— Select Department —</option>' +
      DEPARTMENTS.map(d => `<option value="${d.id}">${d.shortName}</option>`).join('');
  }
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
function renderDashboard() {
  const name = userProfile?.displayName || userProfile?.firstName || 'Staff';
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening';
  const wEl = document.getElementById('dash-welcome'); if (wEl) wEl.textContent = `${greeting}, ${name}!`;
  const detEl = document.getElementById('dash-my-details');
  if (detEl && userProfile) {
    const dept = DEPARTMENTS.find(d => d.id === userProfile.department);
    detEl.innerHTML = `
      <div style="display:grid;gap:10px;">
        ${row('UPN',userProfile.upn||'—')}
        ${row('Department',dept?.shortName||userProfile.department||'—')}
        ${row('Job Group',userProfile.jobGroup||'—')}
        ${row('Designation',userProfile.designation||'—')}
        ${row('Employment Type',userProfile.employmentType||'—')}
      </div>`;
  }
  renderDashStats();
}

function row(label, val) {
  return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--brd);font-size:13px;">
    <span style="color:var(--t2)">${label}</span><strong>${val}</strong></div>`;
}

async function renderDashStats() {
  const statsEl = document.getElementById('dash-stats');
  if (!statsEl) return;
  const docSnap = await getDoc(doc(db,'users',currentUser.uid));
  const profileData = docSnap.exists() ? docSnap.data() : {};
  const docsRef = collection(db,'users',currentUser.uid,'documents');
  const docsSnap = await getDocs(docsRef);
  const docsCount = docsSnap.size;
  const spasRef = collection(db,'users',currentUser.uid,'spas');
  const spasSnap = await getDocs(spasRef);
  const spasCount = spasSnap.size;
  statsEl.innerHTML = `
    <div class="stat-card blue" onclick="navigate('documents')">
      <div class="stat-icon"><span class="material-icons">folder</span></div>
      <div class="stat-val">${docsCount}/${HR_DOCUMENTS.length}</div>
      <div class="stat-label">Documents Uploaded</div>
    </div>
    <div class="stat-card green" onclick="navigate('spas')">
      <div class="stat-icon"><span class="material-icons">star</span></div>
      <div class="stat-val">${spasCount > 0 ? 'Submitted' : 'Pending'}</div>
      <div class="stat-label">SPAS Status</div>
    </div>
    <div class="stat-card orange" onclick="navigate('profile')">
      <div class="stat-icon"><span class="material-icons">person</span></div>
      <div class="stat-val">${profileData.profileComplete ? '100%' : 'Incomplete'}</div>
      <div class="stat-label">Profile Completion</div>
    </div>
    <div class="stat-card purple" onclick="navigate('skills')">
      <div class="stat-icon"><span class="material-icons">psychology</span></div>
      <div class="stat-val">${SKILLS_DOMAINS.length} Domains</div>
      <div class="stat-label">Skills Audit</div>
    </div>`;
}

// ─── Profile Wizard ────────────────────────────────────────────────────────────
const stepLabels = ['Personal Info','Employment Details','Contact & Family','Education & Qualifications',
  'Skills & Experience','Bank & Payroll','Review & Submit'];

function renderProfileWizard() {
  const container = document.getElementById('profile-wizard-container');
  if (!container) return;
  const dept = DEPARTMENTS.find(d => d.id === userProfile?.department);
  const jobGroupOptions = ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T'].map(g=>`<option>${g}</option>`).join('');
  const deptOptions = DEPARTMENTS.map(d=>`<option value="${d.id}" ${userProfile?.department===d.id?'selected':''}>${d.shortName}</option>`).join('');
  container.innerHTML = `
    <div class="wizard-progress">
      ${stepLabels.map((l,i)=>`<div class="wizard-step ${i+1===profileStep?'active':i+1<profileStep?'done':''}">
        <div class="step-circle">${i+1<profileStep?'✓':i+1}</div>
        <div class="step-label">${l}</div></div>`).join('<div class="step-line"></div>')}
    </div>
    <div class="card" style="margin-top:20px;">
      <div class="card-header">
        <div class="card-title">Step ${profileStep} of ${TOTAL_STEPS}: ${stepLabels[profileStep-1]}</div>
      </div>
      <div id="wizard-step-content">${renderStep(profileStep, deptOptions, jobGroupOptions)}</div>
      <div style="display:flex;justify-content:space-between;margin-top:20px;">
        <button class="btn btn-secondary" onclick="profilePrev()" ${profileStep===1?'disabled':''}>← Previous</button>
        ${profileStep < TOTAL_STEPS
          ? `<button class="btn btn-primary" onclick="profileNext()">Next →</button>`
          : `<button class="btn btn-success" onclick="submitProfile()"><span class="material-icons" style="font-size:18px;">save</span> Save Profile</button>`}
      </div>
    </div>`;
  // Pre-fill saved values
  if (userProfile) {
    Object.entries(userProfile).forEach(([k,v]) => {
      const el = document.getElementById(`prof-${k}`);
      if (el && v) { el.value = v; }
    });
  }
}

function renderStep(step, deptOptions, jobGroupOptions) {
  switch(step) {
    case 1: return `
      <div class="form-row">
        <div class="form-group"><label>First Name <span class="required">*</span></label><input id="prof-firstName" class="form-control" placeholder="First name"></div>
        <div class="form-group"><label>Middle Name</label><input id="prof-middleName" class="form-control" placeholder="Middle name"></div>
        <div class="form-group"><label>Last Name <span class="required">*</span></label><input id="prof-lastName" class="form-control" placeholder="Last name"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Date of Birth <span class="required">*</span></label><input id="prof-dob" type="date" class="form-control"></div>
        <div class="form-group"><label>Gender <span class="required">*</span></label>
          <select id="prof-gender" class="form-control"><option value="">Select...</option><option>Male</option><option>Female</option></select></div>
        <div class="form-group"><label>Nationality</label><input id="prof-nationality" class="form-control" value="Kenyan"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>ID Number <span class="required">*</span></label><input id="prof-idNumber" class="form-control" placeholder="National ID"></div>
        <div class="form-group"><label>KRA PIN</label><input id="prof-kraPin" class="form-control" placeholder="A000000000X"></div>
        <div class="form-group"><label>NSSF Number</label><input id="prof-nssfNumber" class="form-control"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>NHIF Number</label><input id="prof-nhifNumber" class="form-control"></div>
        <div class="form-group"><label>Religion</label>
          <select id="prof-religion" class="form-control"><option value="">Select...</option><option>Islam</option><option>Christianity</option><option>Other</option></select></div>
        <div class="form-group"><label>Marital Status</label>
          <select id="prof-maritalStatus" class="form-control"><option value="">Select...</option><option>Single</option><option>Married</option><option>Divorced</option><option>Widowed</option></select></div>
      </div>`;
    case 2: return `
      <div class="form-row">
        <div class="form-group"><label>UPN / Staff Number <span class="required">*</span></label><input id="prof-upn" class="form-control" placeholder="UPN-YYYY-XXXXXX" style="text-transform:uppercase;"></div>
        <div class="form-group"><label>Department <span class="required">*</span></label>
          <select id="prof-department" class="form-control"><option value="">Select...</option>${deptOptions}</select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Directorate / Division</label><input id="prof-directorate" class="form-control" placeholder="Your directorate"></div>
        <div class="form-group"><label>Designation / Job Title <span class="required">*</span></label><input id="prof-designation" class="form-control" placeholder="e.g. Administrative Officer I"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Job Group <span class="required">*</span></label>
          <select id="prof-jobGroup" class="form-control"><option value="">Select...</option>${jobGroupOptions}</select></div>
        <div class="form-group"><label>Salary Scale</label><input id="prof-salaryScale" class="form-control" placeholder="e.g. CPSB 5"></div>
        <div class="form-group"><label>Employment Type</label>
          <select id="prof-employmentType" class="form-control"><option value="">Select...</option><option>Permanent</option><option>Contract</option><option>Intern</option><option>Casual</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Date of First Appointment</label><input id="prof-firstAppointment" type="date" class="form-control"></div>
        <div class="form-group"><label>Date of Confirmation</label><input id="prof-confirmationDate" type="date" class="form-control"></div>
        <div class="form-group"><label>Date of Last Promotion</label><input id="prof-lastPromotion" type="date" class="form-control"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Station / Sub-County</label><input id="prof-station" class="form-control" placeholder="e.g. Garissa Town"></div>
        <div class="form-group"><label>Supervisor's Name</label><input id="prof-supervisorName" class="form-control"></div>
      </div>`;
    case 3: return `
      <div class="form-row">
        <div class="form-group"><label>Work Phone</label><input id="prof-workPhone" class="form-control" placeholder="+254..."></div>
        <div class="form-group"><label>Personal Phone <span class="required">*</span></label><input id="prof-personalPhone" class="form-control" placeholder="+254..."></div>
        <div class="form-group"><label>Personal Email</label><input id="prof-personalEmail" type="email" class="form-control" placeholder="personal@email.com"></div>
      </div>
      <div class="form-group"><label>Postal Address</label><input id="prof-postalAddress" class="form-control" placeholder="P.O. Box XXXX - XXXXX, Town"></div>
      <div class="form-row">
        <div class="form-group"><label>Number of Dependants</label><input id="prof-dependants" type="number" class="form-control" min="0"></div>
        <div class="form-group"><label>Next of Kin Name</label><input id="prof-nokName" class="form-control"></div>
        <div class="form-group"><label>Next of Kin Phone</label><input id="prof-nokPhone" class="form-control" placeholder="+254..."></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Next of Kin Relationship</label>
          <select id="prof-nokRelationship" class="form-control"><option>Spouse</option><option>Parent</option><option>Sibling</option><option>Child</option><option>Other</option></select></div>
        <div class="form-group"><label>Emergency Contact</label><input id="prof-emergencyContact" class="form-control" placeholder="+254..."></div>
      </div>`;
    case 4: return `
      <div class="form-group"><label>Highest Academic Qualification <span class="required">*</span></label>
        <select id="prof-highestQualification" class="form-control">
          <option value="">Select...</option><option>Certificate</option><option>Diploma</option><option>Higher Diploma</option>
          <option>Bachelor's Degree</option><option>Postgraduate Diploma</option><option>Master's Degree</option><option>PhD/Doctorate</option>
        </select></div>
      <div class="form-row">
        <div class="form-group"><label>Field of Study / Specialization</label><input id="prof-fieldOfStudy" class="form-control" placeholder="e.g. Public Administration"></div>
        <div class="form-group"><label>Institution</label><input id="prof-institution" class="form-control" placeholder="e.g. University of Nairobi"></div>
        <div class="form-group"><label>Year of Graduation</label><input id="prof-graduationYear" type="number" class="form-control" min="1970" max="2030" placeholder="YYYY"></div>
      </div>
      <div class="form-group"><label>Professional Certifications (separate with commas)</label>
        <textarea id="prof-certifications" class="form-control" rows="3" placeholder="e.g. CPS(K), CPAK, CFA..."></textarea></div>
      <div class="form-group"><label>Other Trainings Attended</label>
        <textarea id="prof-trainings" class="form-control" rows="3" placeholder="List key trainings and capacity building attended..."></textarea></div>`;
    case 5: return `
      <div class="form-group"><label>Years of Work Experience</label>
        <select id="prof-yearsExperience" class="form-control">
          <option>Less than 1 year</option><option>1–3 years</option><option>3–5 years</option>
          <option>5–10 years</option><option>10–15 years</option><option>15–20 years</option><option>20+ years</option>
        </select></div>
      <div class="form-group"><label>Key Skills (list main competencies)</label>
        <textarea id="prof-keySkills" class="form-control" rows="4" placeholder="e.g. Public financial management, Policy development, ICT systems..."></textarea></div>
      <div class="form-group"><label>Previous Employers / Work History</label>
        <textarea id="prof-workHistory" class="form-control" rows="4" placeholder="List previous employment (employer, position, period)..."></textarea></div>
      <div class="form-row">
        <div class="form-group"><label>Languages Spoken</label><input id="prof-languages" class="form-control" placeholder="e.g. English, Swahili, Somali"></div>
        <div class="form-group"><label>Disability Status</label>
          <select id="prof-disability" class="form-control"><option>None</option><option>Physical</option><option>Visual</option><option>Hearing</option><option>Other</option></select></div>
      </div>`;
    case 6: return `
      <div class="form-row">
        <div class="form-group"><label>Bank Name <span class="required">*</span></label>
          <select id="prof-bankName" class="form-control">
            <option value="">Select Bank...</option>
            <option>Kenya Commercial Bank (KCB)</option><option>Equity Bank</option><option>Co-operative Bank</option>
            <option>Absa Bank Kenya</option><option>Standard Chartered</option><option>NCBA Bank</option>
            <option>Family Bank</option><option>Prime Bank</option><option>National Bank</option><option>Other</option>
          </select></div>
        <div class="form-group"><label>Branch</label><input id="prof-bankBranch" class="form-control" placeholder="e.g. Garissa Branch"></div>
        <div class="form-group"><label>Account Number <span class="required">*</span></label><input id="prof-bankAccount" class="form-control" placeholder="Account number"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Basic Salary (KES)</label><input id="prof-basicSalary" type="number" class="form-control" placeholder="0.00"></div>
        <div class="form-group"><label>HELB Repayment</label><select id="prof-helbRepay" class="form-control"><option>No</option><option>Yes</option></select></div>
        <div class="form-group"><label>Pension Scheme</label>
          <select id="prof-pensionScheme" class="form-control"><option>LAPFUND</option><option>LAPTRUST</option><option>CPF</option><option>Other</option></select></div>
      </div>
      <div class="form-group"><label>Housing Provident Fund (HPF) Reference</label>
        <input id="prof-hpfRef" class="form-control" placeholder="HPF reference number"></div>`;
    case 7: return `
      <div style="padding:20px;background:#f8f9fa;border-radius:12px;margin-bottom:20px;">
        <h4 style="margin-bottom:16px;color:var(--p);">Profile Summary</h4>
        <div id="profile-summary-content" style="font-size:14px;"></div>
      </div>
      <div class="form-group">
        <label>Upload Profile Photo</label>
        <input type="file" id="prof-photo" class="form-control" accept="image/*">
        <p class="form-hint">JPEG/PNG, max 5MB</p>
      </div>
      <div style="padding:16px;background:#e8f5e9;border-radius:8px;border-left:4px solid var(--ok);">
        <strong>Declaration:</strong> I confirm that the information provided is accurate and complete to the best of my knowledge.
        I understand that providing false information may result in disciplinary action.
      </div>`;
    default: return '<p>Invalid step</p>';
  }
}

function profilePrev() { if (profileStep > 1) { profileStep--; renderProfileWizard(); } }
window.profilePrev = profilePrev;

async function profileNext() {
  collectStepData(profileStep);
  profileStep++;
  renderProfileWizard();
  if (profileStep === TOTAL_STEPS) renderProfileSummary();
}
window.profileNext = profileNext;

function collectStepData(step) {
  const fields = document.querySelectorAll('#wizard-step-content [id^="prof-"]');
  const data = {};
  fields.forEach(f => {
    const key = f.id.replace('prof-','');
    if (f.value) data[key] = f.value;
  });
  userProfile = { ...userProfile, ...data };
}

function renderProfileSummary() {
  const el = document.getElementById('profile-summary-content');
  if (!el || !userProfile) return;
  const dept = DEPARTMENTS.find(d => d.id === userProfile.department);
  el.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      ${[
        ['Name', `${userProfile.firstName||''} ${userProfile.lastName||''}`.trim()],
        ['UPN', userProfile.upn || '—'],
        ['Department', dept?.shortName || '—'],
        ['Designation', userProfile.designation || '—'],
        ['Job Group', userProfile.jobGroup || '—'],
        ['Employment Type', userProfile.employmentType || '—'],
        ['Qualification', userProfile.highestQualification || '—'],
        ['Bank', userProfile.bankName || '—'],
      ].map(([l,v]) => `<div style="padding:6px;border-bottom:1px solid #e2e8f0;"><span style="color:#666;font-size:12px;">${l}</span><br><strong>${v}</strong></div>`).join('')}
    </div>`;
}

async function submitProfile() {
  collectStepData(profileStep);
  if (!userProfile?.firstName || !userProfile?.upn) {
    toast('Please fill all required fields in Step 1 and 2', 'warning'); return;
  }
  try {
    const photoInput = document.getElementById('prof-photo');
    if (photoInput?.files[0]) {
      const file = photoInput.files[0];
      const photoRef = ref(storage, `profilePhotos/${currentUser.uid}`);
      await uploadBytes(photoRef, file);
      userProfile.photoURL = await getDownloadURL(photoRef);
    }
    await setDoc(doc(db,'users',currentUser.uid), {
      ...userProfile, profileComplete: true, updatedAt: serverTimestamp()
    }, { merge: true });
    userProfile.profileComplete = true;
    updateSidebarUser();
    toast('Profile saved successfully!', 'success');
    profileStep = 1;
    logEvent(analytics, 'profile_complete');
  } catch(e) {
    toast('Error saving profile: ' + e.message, 'error');
  }
}
window.submitProfile = submitProfile;

// ─── Documents ────────────────────────────────────────────────────────────────
let uploadingDocId = null;

async function renderDocuments() {
  const grid = document.getElementById('doc-grid');
  if (!grid) return;
  const snap = await getDocs(collection(db,'users',currentUser.uid,'documents'));
  const uploaded = {};
  snap.forEach(d => { uploaded[d.data().docType] = d.data(); });

  const byCategory = {};
  HR_DOCUMENTS.forEach(d => {
    if (!byCategory[d.category]) byCategory[d.category] = [];
    byCategory[d.category].push(d);
  });

  grid.innerHTML = Object.entries(byCategory).map(([cat, docs]) => `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header"><div class="card-title">${cat}</div>
        <span class="badge badge-blue">${docs.filter(d=>uploaded[d.id]).length}/${docs.length}</span></div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;">
        ${docs.map(doc => {
          const up = uploaded[doc.id];
          return `<div class="doc-card ${up?'uploaded':''}">
            <div class="doc-icon"><span class="material-icons">${up?'check_circle':'upload_file'}</span></div>
            <div class="doc-info">
              <p class="doc-name">${doc.name}</p>
              <p class="doc-status">${up ? `Uploaded: ${new Date(up.uploadedAt?.seconds*1000||Date.now()).toLocaleDateString('en-GB')}` : doc.required?'Required — Not uploaded':'Optional'}</p>
            </div>
            <div class="doc-actions">
              ${up ? `<button class="btn btn-sm btn-secondary" onclick="viewDoc('${up.url}')"><span class="material-icons" style="font-size:14px;">visibility</span></button>
                      <button class="btn btn-sm btn-danger" onclick="deleteDoc('${doc.id}','${up.fileRef}')"><span class="material-icons" style="font-size:14px;">delete</span></button>` :
                      `<button class="btn btn-sm btn-primary" onclick="openDocModal('${doc.id}','${doc.name}')"><span class="material-icons" style="font-size:14px;">upload</span> Upload</button>`}
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>`).join('');
}

function openDocModal(docId, docName) {
  uploadingDocId = docId;
  document.getElementById('doc-modal-title').textContent = `Upload: ${docName}`;
  document.getElementById('doc-modal-body').innerHTML = `
    <div class="form-group"><label>Select File</label>
      <input type="file" id="doc-file-input" class="form-control" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx">
      <p class="form-hint">PDF, JPG, PNG or Word. Max 20MB.</p></div>`;
  document.getElementById('doc-modal-confirm').onclick = uploadDoc;
  document.getElementById('doc-modal').classList.remove('hidden');
}

async function uploadDoc() {
  const file = document.getElementById('doc-file-input')?.files[0];
  if (!file) { toast('Select a file first','warning'); return; }
  if (file.size > 20*1024*1024) { toast('File exceeds 20MB','error'); return; }
  const upn = userProfile?.upn || currentUser.uid;
  const fileRef = ref(storage, `staff/${upn}/${uploadingDocId}_${Date.now()}_${file.name}`);
  try {
    toast('Uploading...','info',10000);
    const snap = await uploadBytes(fileRef, file);
    const url = await getDownloadURL(snap.ref);
    await setDoc(doc(db,'users',currentUser.uid,'documents',uploadingDocId), {
      docType: uploadingDocId, url, fileRef: snap.ref.fullPath,
      fileName: file.name, uploadedAt: serverTimestamp()
    });
    closeDocModal();
    toast('Document uploaded successfully!','success');
    renderDocuments();
    logEvent(analytics,'document_upload',{type:uploadingDocId});
  } catch(e) {
    toast('Upload failed: '+e.message,'error');
  }
}

async function deleteDoc(docId, fileRefPath) {
  if (!confirm('Delete this document?')) return;
  try {
    await deleteObject(ref(storage, fileRefPath));
    await setDoc(doc(db,'users',currentUser.uid,'documents',docId), {deleted:true},{merge:true});
    await getDocs(collection(db,'users',currentUser.uid,'documents')).then(async snap=>{
      for (const d of snap.docs) { if (d.id===docId) { await d.ref.delete?.(); } }
    });
    toast('Document deleted','info');
    renderDocuments();
  } catch(e) { toast('Delete failed: '+e.message,'error'); }
}

function viewDoc(url) { window.open(url,'_blank'); }
function closeDocModal() { document.getElementById('doc-modal')?.classList.add('hidden'); }
window.openDocModal = openDocModal;
window.viewDoc = viewDoc;
window.deleteDoc = deleteDoc;
window.closeDocModal = closeDocModal;

// ─── SPAS ─────────────────────────────────────────────────────────────────────
function renderSpas() {
  const container = document.getElementById('spas-container');
  if (!container) return;
  const jg = userProfile?.jobGroup || 'H';
  const isForm1 = SPAS_FORM1.jobGroups.includes(jg);
  const form = isForm1 ? SPAS_FORM1 : SPAS_FORM2;
  const yr = new Date().getFullYear();

  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header">
        <div class="card-title">SPAS — Staff Performance Appraisal System</div>
        <span class="badge badge-blue">FY ${yr-1}/${yr}</span>
      </div>
      <p style="font-size:13px;color:var(--t2);margin-bottom:8px;">Form: <strong>${form.label}</strong> | Job Group: <strong>${jg}</strong></p>
      <div style="background:#e3f2fd;padding:12px;border-radius:8px;font-size:13px;margin-bottom:12px;">
        <strong>Rating Scale:</strong> Excellent (130–200%): 1.00–2.40 | Very Good (100–130%): 2.40–3.00 | Good (70–100%): 3.00–3.60 | Fair (50–70%): 3.60–4.00 | Poor (&lt;50%): 4.00–5.00
      </div>
    </div>
    <form id="spas-form">
      ${form.sections.map((sec,si) => `
        <div class="card" style="margin-bottom:16px;">
          <div class="card-header">
            <div class="card-title">${si+1}. ${sec.name}</div>
            <span class="badge badge-gold">Max: ${sec.maxScore} pts</span>
          </div>
          ${sec.items.map((item,ii) => `
            <div style="padding:12px 0;border-bottom:1px solid var(--brd);">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;">
                <label style="font-size:14px;flex:1;">${item}</label>
                <div style="display:flex;gap:6px;align-items:center;">
                  <input type="number" id="spas-${si}-${ii}" class="form-control" style="width:80px;" min="0" max="${Math.floor(sec.maxScore/sec.items.length)}" placeholder="0">
                  <span style="font-size:12px;color:var(--t2);">/${Math.floor(sec.maxScore/sec.items.length)}</span>
                </div>
              </div>
            </div>`).join('')}
          <div style="padding:8px 0;font-size:13px;color:var(--t2);">Section Score: <span id="spas-sec-${si}">0</span> / ${sec.maxScore}</div>
        </div>`).join('')}
      <div class="card" style="margin-bottom:16px;">
        <div class="card-header"><div class="card-title">Appraisee's Comments</div></div>
        <div class="form-group"><textarea id="spas-comments" class="form-control" rows="4" placeholder="Your comments and achievements during this review period..."></textarea></div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <button type="button" class="btn btn-secondary" onclick="calcSpasScore()"><span class="material-icons" style="font-size:18px;">calculate</span> Calculate Score</button>
        <button type="button" class="btn btn-primary" onclick="submitSpas()"><span class="material-icons" style="font-size:18px;">send</span> Submit SPAS</button>
      </div>
    </form>
    <div id="spas-result" style="display:none;margin-top:20px;"></div>`;

  // Live score calc
  document.querySelectorAll('[id^="spas-"]').forEach(inp => {
    if (inp.type === 'number') inp.addEventListener('input', calcSpasScore);
  });
}

function calcSpasScore() {
  const jg = userProfile?.jobGroup || 'H';
  const form = SPAS_FORM1.jobGroups.includes(jg) ? SPAS_FORM1 : SPAS_FORM2;
  let total = 0;
  form.sections.forEach((sec,si) => {
    let secScore = 0;
    sec.items.forEach((_,ii) => {
      secScore += parseFloat(document.getElementById(`spas-${si}-${ii}`)?.value||0);
    });
    secScore = Math.min(secScore, sec.maxScore);
    total += secScore;
    const el = document.getElementById(`spas-sec-${si}`); if (el) el.textContent = secScore.toFixed(1);
  });
  const pct = total;
  const rating = pct >= 130 ? 'Excellent' : pct >= 100 ? 'Very Good' : pct >= 70 ? 'Good' : pct >= 50 ? 'Fair' : 'Poor';
  const ratingClass = { Excellent:'badge-green', 'Very Good':'badge-blue', Good:'badge-gold', Fair:'badge-orange', Poor:'badge-red' };
  const res = document.getElementById('spas-result');
  if (res) {
    res.style.display = 'block';
    res.innerHTML = `<div class="card"><div class="card-header">
      <div class="card-title">Score Summary</div>
      <span class="badge ${ratingClass[rating]||'badge-gray'}">${rating}</span>
    </div>
    <div style="font-size:24px;font-weight:700;color:var(--p);margin-bottom:8px;">${total.toFixed(1)} / 100</div>
    <p style="font-size:14px;color:var(--t2);">Rating: <strong>${rating}</strong></p></div>`;
  }
}

async function submitSpas() {
  calcSpasScore();
  const jg = userProfile?.jobGroup || 'H';
  const form = SPAS_FORM1.jobGroups.includes(jg) ? SPAS_FORM1 : SPAS_FORM2;
  const data = { formType: form.label, jobGroup: jg, period: `${new Date().getFullYear()-1}/${new Date().getFullYear()}`,
    sections:{}, comments: document.getElementById('spas-comments')?.value,
    submittedAt: serverTimestamp(), status:'submitted' };
  form.sections.forEach((sec,si) => {
    data.sections[sec.id] = { name:sec.name, scores: {} };
    sec.items.forEach((item,ii) => {
      data.sections[sec.id].scores[ii] = { item, score: parseFloat(document.getElementById(`spas-${si}-${ii}`)?.value||0) };
    });
  });
  try {
    await addDoc(collection(db,'users',currentUser.uid,'spas'), data);
    toast('SPAS submitted successfully!','success');
    logEvent(analytics,'spas_submit');
  } catch(e) { toast('Submit failed: '+e.message,'error'); }
}
window.calcSpasScore = calcSpasScore;
window.submitSpas = submitSpas;

// ─── Performance Contracting ──────────────────────────────────────────────────
function renderPC() {
  const container = document.getElementById('pc-container');
  if (!container) return;
  const yr = new Date().getFullYear();
  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header">
        <div class="card-title">Performance Contracting FY ${yr}/${yr+1}</div>
        <span class="badge badge-orange">Due: July 31, ${yr}</span>
      </div>
      <p style="font-size:13px;color:var(--t2);">Rate each criterion achievement (0–100%). Weighted scores sum to 100%.</p>
    </div>
    <div id="pc-criteria-list">
      ${PC_CRITERIA.map((c,i) => `
        <div class="card" style="margin-bottom:12px;">
          <div class="card-header">
            <div><div class="card-title">${c.name}</div><p style="font-size:12px;color:var(--t2);">${c.description}</p></div>
            <span class="badge badge-blue">Weight: ${c.weight}%</span>
          </div>
          <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
            <div class="form-group" style="flex:1;margin:0;">
              <label>Achievement (%)</label>
              <input type="number" id="pc-${c.id}" class="form-control" min="0" max="200" placeholder="0"
                oninput="calcPC()" style="max-width:150px;">
            </div>
            <div style="flex:2;">
              <div style="height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;">
                <div id="pc-bar-${c.id}" style="height:100%;background:var(--p);border-radius:4px;width:0%;transition:width .3s;"></div>
              </div>
              <p style="font-size:12px;color:var(--t2);margin-top:4px;">Weighted score: <span id="pc-wscore-${c.id}">0.00</span>%</p>
            </div>
          </div>
        </div>`).join('')}
    </div>
    <div class="card">
      <div class="card-header"><div class="card-title">Overall Score</div></div>
      <div style="font-size:32px;font-weight:700;color:var(--p);" id="pc-total">0.00%</div>
      <div id="pc-rating-badge" style="margin-top:8px;"></div>
      <div class="form-group" style="margin-top:16px;"><label>Remarks / Comments</label>
        <textarea id="pc-remarks" class="form-control" rows="3"></textarea></div>
      <button class="btn btn-primary" onclick="submitPC()">
        <span class="material-icons" style="font-size:18px;">save</span> Save Performance Contract
      </button>
    </div>`;
}

function calcPC() {
  let total = 0;
  PC_CRITERIA.forEach(c => {
    const val = parseFloat(document.getElementById(`pc-${c.id}`)?.value||0);
    const wscore = (val * c.weight) / 100;
    total += wscore;
    const barEl = document.getElementById(`pc-bar-${c.id}`);
    if (barEl) barEl.style.width = Math.min(val,100) + '%';
    const wEl = document.getElementById(`pc-wscore-${c.id}`);
    if (wEl) wEl.textContent = wscore.toFixed(2);
  });
  const totalEl = document.getElementById('pc-total'); if (totalEl) totalEl.textContent = total.toFixed(2) + '%';
  const rating = total >= 80 ? 'Excellent' : total >= 60 ? 'Very Good' : total >= 40 ? 'Good' : total >= 20 ? 'Fair' : 'Poor';
  const rb = document.getElementById('pc-rating-badge');
  const cls = {Excellent:'badge-green','Very Good':'badge-blue',Good:'badge-gold',Fair:'badge-orange',Poor:'badge-red'};
  if (rb) rb.innerHTML = `<span class="badge ${cls[rating]}">${rating}</span>`;
}
window.calcPC = calcPC;

async function submitPC() {
  const scores = {};
  PC_CRITERIA.forEach(c => { scores[c.id] = parseFloat(document.getElementById(`pc-${c.id}`)?.value||0); });
  const yr = new Date().getFullYear();
  try {
    await addDoc(collection(db,'performanceContracts'), {
      userId: currentUser.uid, department: userProfile?.department,
      period: `${yr}/${yr+1}`, scores, remarks: document.getElementById('pc-remarks')?.value,
      submittedAt: serverTimestamp(), status:'submitted'
    });
    toast('Performance Contract saved!','success');
    logEvent(analytics,'pc_submit');
  } catch(e) { toast('Error: '+e.message,'error'); }
}
window.submitPC = submitPC;

// ─── Skills Audit ─────────────────────────────────────────────────────────────
function renderSkills() {
  const container = document.getElementById('skills-container');
  if (!container) return;
  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header"><div class="card-title">Skills Audit — HRIS-Ke Competency Framework</div></div>
      <p style="font-size:13px;color:var(--t2);">Rate your competency level: 1=Awareness, 2=Basic, 3=Proficient, 4=Advanced, 5=Expert</p>
    </div>
    ${SKILLS_DOMAINS.map((domain,di) => `
      <div class="card" style="margin-bottom:16px;">
        <div class="card-header">
          <div style="display:flex;align-items:center;gap:12px;">
            <span class="material-icons" style="color:var(--p);font-size:28px;">${domain.icon}</span>
            <div class="card-title">${domain.name}</div>
          </div>
        </div>
        <div style="display:grid;gap:12px;">
          ${domain.competencies.map((comp,ci) => `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--brd);gap:12px;flex-wrap:wrap;">
              <label style="font-size:14px;flex:1;">${comp}</label>
              <div style="display:flex;gap:6px;">
                ${[1,2,3,4,5].map(n=>`<label style="cursor:pointer;text-align:center;">
                  <input type="radio" name="skill-${di}-${ci}" value="${n}" style="display:block;margin:0 auto 4px;">
                  <span style="font-size:11px;color:var(--t2);">${n}</span></label>`).join('')}
              </div>
            </div>`).join('')}
        </div>
      </div>`).join('')}
    <div class="card">
      <div class="form-group"><label>Additional Skills / Competencies</label>
        <textarea id="skills-additional" class="form-control" rows="3" placeholder="Any other skills not listed above..."></textarea></div>
      <div class="form-group"><label>Training Needs Identified</label>
        <textarea id="skills-training-needs" class="form-control" rows="3" placeholder="Areas you'd like training in..."></textarea></div>
      <button class="btn btn-primary" onclick="submitSkills()">
        <span class="material-icons" style="font-size:18px;">save</span> Submit Skills Audit
      </button>
    </div>`;
}

async function submitSkills() {
  const data = { domains:{}, additional: document.getElementById('skills-additional')?.value,
    trainingNeeds: document.getElementById('skills-training-needs')?.value,
    submittedAt: serverTimestamp() };
  SKILLS_DOMAINS.forEach((domain,di) => {
    data.domains[domain.id] = { name: domain.name, scores:{} };
    domain.competencies.forEach((comp,ci) => {
      const sel = document.querySelector(`input[name="skill-${di}-${ci}"]:checked`);
      data.domains[domain.id].scores[ci] = { competency: comp, score: sel ? parseInt(sel.value) : 0 };
    });
  });
  try {
    await addDoc(collection(db,'users',currentUser.uid,'skillsAudit'), data);
    toast('Skills Audit submitted!','success');
    logEvent(analytics,'skills_audit_submit');
  } catch(e) { toast('Error: '+e.message,'error'); }
}
window.submitSkills = submitSkills;

// ─── Reports ──────────────────────────────────────────────────────────────────
function renderReports() {
  const container = document.getElementById('reports-container');
  if (!container) return;
  const isAdmin = ['admin','hr_director','hr_officer'].includes(userProfile?.role);
  container.innerHTML = `
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-bottom:20px;">
      <div class="card report-card" onclick="generateReport('profile_summary')">
        <span class="material-icons" style="font-size:40px;color:var(--p);margin-bottom:12px;">person</span>
        <h4>My Profile Report</h4><p style="font-size:13px;color:var(--t2);">Download your complete employee profile as PDF</p>
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button class="btn btn-sm btn-primary" onclick="generateReport('profile_pdf');event.stopPropagation()">PDF</button>
        </div>
      </div>
      <div class="card report-card" onclick="generateReport('spas')">
        <span class="material-icons" style="font-size:40px;color:#2E7D32;margin-bottom:12px;">star_rate</span>
        <h4>SPAS Appraisal Report</h4><p style="font-size:13px;color:var(--t2);">View and download your performance appraisal</p>
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button class="btn btn-sm btn-primary" onclick="generateReport('spas_pdf');event.stopPropagation()">PDF</button>
        </div>
      </div>
      <div class="card report-card" onclick="generateReport('documents')">
        <span class="material-icons" style="font-size:40px;color:#E65100;margin-bottom:12px;">folder</span>
        <h4>Document Checklist</h4><p style="font-size:13px;color:var(--t2);">HR documents submission status report</p>
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button class="btn btn-sm btn-primary" onclick="generateReport('docs_pdf');event.stopPropagation()">PDF</button>
        </div>
      </div>
      ${isAdmin ? `
      <div class="card report-card">
        <span class="material-icons" style="font-size:40px;color:#6A1B9A;margin-bottom:12px;">groups</span>
        <h4>Staff Register</h4><p style="font-size:13px;color:var(--t2);">Full staff establishment report by department</p>
        <div style="margin-top:12px;display:flex;gap:8px;">
          <button class="btn btn-sm btn-primary" onclick="generateReport('staff_pdf');event.stopPropagation()">PDF</button>
          <button class="btn btn-sm btn-secondary" onclick="generateReport('staff_excel');event.stopPropagation()">Excel</button>
        </div>
      </div>` : ''}
    </div>`;
}

async function generateReport(type) {
  toast(`Generating ${type} report...`, 'info', 3000);
  if (type === 'profile_pdf') await generateProfilePDF();
  else if (type === 'docs_pdf') await generateDocsPDF();
  else toast('Report generation in progress','info');
}
window.generateReport = generateReport;

async function generateProfilePDF() {
  if (!window.jspdf) { toast('PDF library loading, try again','warning'); return; }
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF();
  const dept = DEPARTMENTS.find(d => d.id === userProfile?.department);
  pdf.setFontSize(16); pdf.text('COUNTY GOVERNMENT OF GARISSA', 105, 20, {align:'center'});
  pdf.setFontSize(12); pdf.text('EMPLOYEE PROFILE REPORT', 105, 30, {align:'center'});
  pdf.setFontSize(10);
  let y = 45;
  [
    ['Name', `${userProfile?.firstName||''} ${userProfile?.lastName||''}`.trim()],
    ['UPN', userProfile?.upn||'—'],
    ['Department', dept?.shortName||'—'],
    ['Designation', userProfile?.designation||'—'],
    ['Job Group', userProfile?.jobGroup||'—'],
    ['Date of Birth', userProfile?.dob||'—'],
    ['Date of Appointment', userProfile?.firstAppointment||'—'],
    ['Employment Type', userProfile?.employmentType||'—'],
    ['Bank', userProfile?.bankName||'—'],
  ].forEach(([l,v]) => { pdf.text(`${l}: ${v}`, 20, y); y += 8; });
  pdf.text(`Generated: ${new Date().toLocaleDateString('en-GB')}`, 20, 280);
  pdf.save(`${userProfile?.upn||'employee'}_profile.pdf`);
  toast('Profile PDF downloaded!','success');
}

async function generateDocsPDF() {
  if (!window.jspdf) { toast('PDF library loading, try again','warning'); return; }
  const { jsPDF } = window.jspdf;
  const snap = await getDocs(collection(db,'users',currentUser.uid,'documents'));
  const uploaded = {}; snap.forEach(d => { uploaded[d.data().docType] = d.data(); });
  const pdf = new jsPDF();
  pdf.setFontSize(14); pdf.text('DOCUMENT SUBMISSION CHECKLIST', 105, 20, {align:'center'});
  pdf.setFontSize(10); pdf.text(`Employee: ${userProfile?.displayName||''}  |  UPN: ${userProfile?.upn||'—'}`, 105, 30, {align:'center'});
  let y = 45;
  HR_DOCUMENTS.forEach(doc => {
    const up = uploaded[doc.id];
    pdf.text(`${up?'[✓]':'[ ]'} ${doc.name} ${doc.required?'(Required)':'(Optional)'}`, 20, y);
    y += 8; if (y > 270) { pdf.addPage(); y = 20; }
  });
  pdf.text(`Generated: ${new Date().toLocaleDateString('en-GB')}`, 20, 280);
  pdf.save(`${userProfile?.upn||'employee'}_documents_checklist.pdf`);
  toast('Document checklist PDF downloaded!','success');
}

// ─── Organogram (Colorful 3D) ─────────────────────────────────────────────────
function initOrganogram() {
  populateDeptDropdowns();
  showOrganogram('county');
}

function showOrganogram(target) {
  const container = document.getElementById('organogram-container');
  if (!container) return;

  if (target === 'county' || target === '') {
    renderCountyOrganogram(container);
  } else {
    const dept = DEPARTMENTS.find(d => d.id === target);
    if (dept) renderDeptOrganogram(container, dept);
  }
}
window.showOrganogram = showOrganogram;

function oBox(label, sub, color, bg, icon, size='normal', extra='') {
  const fs = size === 'large' ? '15px' : size === 'small' ? '11px' : '13px';
  const pd = size === 'large' ? '18px 24px' : size === 'small' ? '8px 14px' : '12px 18px';
  const minW = size === 'large' ? '220px' : size === 'small' ? '160px' : '190px';
  return `
    <div class="org-box" style="background:${bg};color:${color};padding:${pd};min-width:${minW};font-size:${fs};${extra}"
         title="${label}">
      ${icon?`<div class="org-icon"><span class="material-icons" style="font-size:18px;">${icon}</span></div>`:''}
      <div class="org-label">${label}</div>
      ${sub?`<div class="org-sub">${sub}</div>`:''}
    </div>`;
}

function renderCountyOrganogram(container) {
  const totalAuth = DEPARTMENTS.reduce((s,d)=>s+d.authorized,0);
  const totalPost = DEPARTMENTS.reduce((s,d)=>s+d.inPost,0);

  container.innerHTML = `
    <style>
      .org-container { overflow-x: auto; padding: 20px 0; }
      .org-box { border-radius: 12px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,.18), 0 2px 8px rgba(0,0,0,.12);
        cursor: pointer; transition: all .3s; transform: perspective(600px) rotateX(2deg);
        border: 2px solid rgba(255,255,255,.3); display:inline-block; margin:4px; }
      .org-box:hover { transform: perspective(600px) rotateX(0deg) scale(1.06) translateY(-4px);
        box-shadow: 0 16px 48px rgba(0,0,0,.25), 0 4px 16px rgba(0,0,0,.15); }
      .org-icon { margin-bottom: 6px; }
      .org-label { font-weight: 700; line-height: 1.3; }
      .org-sub { font-size: 11px; opacity: .85; margin-top: 4px; line-height: 1.4; }
      .org-level { display: flex; align-items: flex-start; justify-content: center; flex-wrap: wrap; gap: 12px; margin: 12px 0; }
      .org-connector-v { width: 2px; background: #CBD5E1; height: 32px; margin: 0 auto; }
      .org-connector-h { height: 2px; background: #CBD5E1; flex: 1; max-width: 40px; align-self: center; }
      .dept-card { border-radius:16px; padding:18px 14px; text-align:center; cursor:pointer;
        box-shadow:0 8px 32px rgba(0,0,0,.18); transform:perspective(600px) rotateX(3deg) rotateY(-1deg);
        transition:all .3s; border:2px solid rgba(255,255,255,.25); min-width:160px; max-width:200px; }
      .dept-card:hover { transform:perspective(600px) rotateX(0) rotateY(0) scale(1.08) translateY(-6px);
        box-shadow:0 20px 60px rgba(0,0,0,.28); }
      .dept-icon { font-size:36px; margin-bottom:8px; }
      .dept-name { font-size:12px; font-weight:700; color:#fff; line-height:1.3; margin-bottom:6px; }
      .dept-stats { font-size:11px; color:rgba(255,255,255,.85); }
      .org-summary { display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px; }
      .org-sum-card { background:#fff;border-radius:12px;padding:16px 24px;flex:1;min-width:180px;
        box-shadow:0 4px 16px rgba(0,0,0,.08);border:1px solid #e2e8f0;text-align:center; }
      .org-sum-val { font-size:28px;font-weight:800;color:var(--p); }
      .org-sum-label { font-size:12px;color:var(--t2);margin-top:4px; }
    </style>
    <div class="org-summary">
      <div class="org-sum-card"><div class="org-sum-val">4,755</div><div class="org-sum-label">Total Authorized Establishment</div></div>
      <div class="org-sum-card"><div class="org-sum-val" style="color:#2E7D32;">${totalPost.toLocaleString()}</div><div class="org-sum-label">Staff in Post</div></div>
      <div class="org-sum-card"><div class="org-sum-val" style="color:#E65100;">12</div><div class="org-sum-label">Departments / Entities</div></div>
      <div class="org-sum-card"><div class="org-sum-val" style="color:#6A1B9A;">6</div><div class="org-sum-label">Municipal Boards</div></div>
    </div>

    <div class="org-container">
      <!-- Governor Level -->
      <div class="org-level">
        ${oBox('H.E. The Governor','County Government of Garissa','#fff','linear-gradient(135deg,#1565C0,#0D47A1)','account_balance','large','min-width:260px;')}
      </div>
      <div class="org-connector-v"></div>

      <!-- County Secretary / Deputy Governor -->
      <div class="org-level">
        ${oBox('Deputy Governor','Office of the Deputy Governor','#fff','linear-gradient(135deg,#1976D2,#1565C0)','supervisor_account')}
        ${oBox('County Secretary & HPS','Head of Public Service','#fff','linear-gradient(135deg,#2E7D32,#1B5E20)','manage_accounts')}
        ${oBox('County Attorney','Legal Advisory Services','#fff','linear-gradient(135deg,#5D4037,#3E2723)','gavel','small')}
        ${oBox('GCPSB','County Public Service Board','#fff','linear-gradient(135deg,#37474F,#263238)','gavel','small')}
      </div>
      <div class="org-connector-v"></div>

      <!-- County Cabinet -->
      <div style="text-align:center;margin-bottom:12px;">
        <div style="background:#F3F4F6;border-radius:8px;padding:8px 24px;display:inline-block;font-size:13px;font-weight:700;color:var(--t2);">
          COUNTY EXECUTIVE COMMITTEE (CEC) — 11 Members
        </div>
      </div>
      <div class="org-connector-v"></div>

      <!-- Departments Grid -->
      <div style="display:flex;flex-wrap:wrap;gap:14px;justify-content:center;padding:8px;">
        ${DEPARTMENTS.filter(d=>d.id!=='governor'&&d.id!=='cpsb').map(d => `
          <div class="dept-card" style="background:${d.bg};" onclick="showOrganogram('${d.id}')" title="Click to view department organogram">
            <div class="dept-icon"><span class="material-icons" style="color:rgba(255,255,255,.9);">${d.icon}</span></div>
            <div class="dept-name">${d.shortName}</div>
            <div class="dept-stats">
              <div>Auth: <strong>${d.authorized}</strong></div>
              <div>In Post: <strong>${d.inPost}</strong></div>
              <div style="margin-top:4px;font-size:10px;background:rgba(255,255,255,.2);border-radius:4px;padding:2px 6px;">
                ${d.chiefOfficers.length} Chief Officer${d.chiefOfficers.length!==1?'s':''}
              </div>
            </div>
          </div>`).join('')}
      </div>
    </div>
    <p style="text-align:center;font-size:12px;color:var(--t2);margin-top:16px;">
      Click any department card to view its detailed organogram
    </p>`;
}

function renderDeptOrganogram(container, dept) {
  const fillPct = dept.authorized > 0 ? Math.round((dept.inPost/dept.authorized)*100) : 0;
  const fillColor = fillPct >= 90 ? '#2E7D32' : fillPct >= 70 ? '#F57F17' : '#B71C1C';

  container.innerHTML = `
    <style>
      .org-container{overflow-x:auto;padding:20px 0;}
      .org-box{border-radius:12px;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,.18);cursor:pointer;
        transition:all .3s;transform:perspective(600px) rotateX(2deg);border:2px solid rgba(255,255,255,.3);display:inline-block;margin:4px;}
      .org-box:hover{transform:perspective(600px) rotateX(0deg) scale(1.06) translateY(-4px);
        box-shadow:0 16px 48px rgba(0,0,0,.25);}
      .org-icon{margin-bottom:6px;}
      .org-label{font-weight:700;line-height:1.3;}
      .org-sub{font-size:11px;opacity:.85;margin-top:4px;}
      .org-level{display:flex;align-items:flex-start;justify-content:center;flex-wrap:wrap;gap:12px;margin:12px 0;}
      .org-connector-v{width:2px;background:#CBD5E1;height:28px;margin:0 auto;}
      .dir-card{border-radius:12px;padding:14px;text-align:center;box-shadow:0 6px 24px rgba(0,0,0,.14);
        transform:perspective(500px) rotateX(3deg);transition:all .3s;min-width:180px;max-width:220px;
        border:2px solid rgba(255,255,255,.2);}
      .dir-card:hover{transform:perspective(500px) rotateX(0) scale(1.07) translateY(-5px);
        box-shadow:0 16px 40px rgba(0,0,0,.22);}
    </style>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
      <button class="btn btn-sm btn-secondary" onclick="showOrganogram('county')">← County Overview</button>
      <h3 style="color:var(--t1);">${dept.shortName}</h3>
    </div>

    <!-- Stats Bar -->
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px;">
      <div style="background:${dept.bg};color:#fff;border-radius:12px;padding:16px 24px;flex:1;min-width:160px;text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,.18);transform:perspective(400px) rotateX(3deg);">
        <div style="font-size:32px;font-weight:800;">${dept.authorized}</div>
        <div style="font-size:12px;opacity:.85;">Authorized Establishment</div>
      </div>
      <div style="background:linear-gradient(135deg,#2E7D32,#1B5E20);color:#fff;border-radius:12px;padding:16px 24px;flex:1;min-width:160px;text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,.18);transform:perspective(400px) rotateX(3deg);">
        <div style="font-size:32px;font-weight:800;">${dept.inPost}</div>
        <div style="font-size:12px;opacity:.85;">Staff in Post</div>
      </div>
      <div style="background:linear-gradient(135deg,#1565C0,#0D47A1);color:#fff;border-radius:12px;padding:16px 24px;flex:1;min-width:160px;text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,.18);transform:perspective(400px) rotateX(3deg);">
        <div style="font-size:32px;font-weight:800;color:${fillColor};">${fillPct}%</div>
        <div style="font-size:12px;opacity:.85;">Staffing Level</div>
        <div style="height:6px;background:rgba(255,255,255,.3);border-radius:3px;margin-top:8px;overflow:hidden;">
          <div style="height:100%;width:${Math.min(fillPct,100)}%;background:${fillColor};border-radius:3px;transition:width .5s;"></div>
        </div>
      </div>
      <div style="background:linear-gradient(135deg,#E65100,#BF360C);color:#fff;border-radius:12px;padding:16px 24px;flex:1;min-width:160px;text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,.18);transform:perspective(400px) rotateX(3deg);">
        <div style="font-size:32px;font-weight:800;">${dept.chiefOfficers.length || dept.directorates.length}</div>
        <div style="font-size:12px;opacity:.85;">${dept.chiefOfficers.length ? 'Chief Officers' : 'Directorates'}</div>
      </div>
    </div>

    <div class="org-container">
      <!-- CECM -->
      <div class="org-level">
        ${oBox(dept.headTitle,'County Executive Committee Member','#fff',dept.bg,dept.icon,'large','min-width:280px;')}
      </div>
      <div class="org-connector-v"></div>

      <!-- Chief Officers -->
      ${dept.chiefOfficers.length > 0 ? `
        <div class="org-level">
          ${dept.chiefOfficers.map(co => oBox(co,'Chief Officer (Accounting Officer)','#fff','linear-gradient(135deg,#1565C0,#0D47A1)','person_outline')).join('')}
        </div>
        <div class="org-connector-v"></div>` : ''}

      <!-- Directorates -->
      <div style="text-align:center;margin-bottom:12px;">
        <div style="background:#F3F4F6;border-radius:8px;padding:6px 20px;display:inline-block;font-size:12px;font-weight:700;color:var(--t2);">
          DIRECTORATES & UNITS
        </div>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;padding:8px;">
        ${dept.directorates.map((dir, i) => {
          const colors = ['#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#1A237E','#880E4F','#33691E','#37474F','#F57F17','#0277BD','#5D4037'];
          const bg = `linear-gradient(135deg,${colors[i%colors.length]},${colors[(i+1)%colors.length]})`;
          const pct = dir.authorized > 0 ? Math.round((dir.inPost/dir.authorized)*100) : 0;
          return `<div class="dir-card" style="background:${bg};color:#fff;">
            <div style="font-size:13px;font-weight:700;line-height:1.3;margin-bottom:8px;">${dir.name}</div>
            <div style="font-size:11px;opacity:.85;">Auth: ${dir.authorized} | In Post: ${dir.inPost}</div>
            <div style="height:5px;background:rgba(255,255,255,.3);border-radius:3px;margin-top:8px;overflow:hidden;">
              <div style="height:100%;width:${Math.min(pct,100)}%;background:rgba(255,255,255,.8);border-radius:3px;"></div>
            </div>
            <div style="font-size:10px;opacity:.7;margin-top:4px;">${pct}% filled</div>
          </div>`;
        }).join('')}
      </div>

      ${dept.keyPosts ? `
        <div style="margin-top:24px;">
          <div style="text-align:center;margin-bottom:12px;">
            <div style="background:#F3F4F6;border-radius:8px;padding:6px 20px;display:inline-block;font-size:12px;font-weight:700;color:var(--t2);">KEY POSTS</div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
            ${dept.keyPosts.map(p=>`<div style="background:#fff;border:2px solid ${dept.color};color:${dept.color};border-radius:8px;padding:6px 14px;font-size:12px;font-weight:600;">${p}</div>`).join('')}
          </div>
        </div>` : ''}

      ${dept.municipalities ? `
        <div style="margin-top:24px;">
          <div style="text-align:center;margin-bottom:12px;">
            <div style="background:#F3F4F6;border-radius:8px;padding:6px 20px;display:inline-block;font-size:12px;font-weight:700;color:var(--t2);">MUNICIPAL BOARDS (6)</div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
            ${dept.municipalities.map((m,i)=>{
              const mcs=['#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#880E4F'];
              return `<div style="background:${mcs[i]};color:#fff;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:700;
                box-shadow:0 4px 16px rgba(0,0,0,.15);transform:perspective(300px) rotateX(3deg);">${m} Municipality</div>`;
            }).join('')}
          </div>
        </div>` : ''}
    </div>
    <p style="text-align:center;font-size:12px;color:var(--t2);margin-top:16px;">
      Source: Approved Staff Establishment — 27th March 2026 | Signed by CS Rakia F. Ibrahim (GCPSB) & County Secretary Mohamed Hassan Mursal
    </p>`;
}

// ─── Help Manual ──────────────────────────────────────────────────────────────
function renderHelp() {
  const container = document.getElementById('help-container');
  if (!container) return;
  const topics = [
    { title:'Getting Started', icon:'rocket_launch', content:'Sign in using your official Gmail account or email/password. Complete your profile in the 7-step wizard to activate all modules. Your UPN (Unique Personnel Number) is required and must match HRIS-Ke records.' },
    { title:'Employee Profile', icon:'person', content:'The 7-step profile wizard covers: Personal Info, Employment Details, Contact & Family, Education & Qualifications, Skills & Experience, Bank & Payroll, and Review & Submit. All required (*) fields must be completed. Upload a professional passport photo.' },
    { title:'HR Documents', icon:'folder_open', content:'Upload 18 required HR documents including: National ID, KRA PIN, NHIF/NSSF cards, Academic certificates, Appointment letters, Bank details, Medical certificate, Police clearance, and Ethics clearance. Files must be PDF/JPG/PNG, max 20MB each.' },
    { title:'SPAS Appraisal', icon:'star_rate', content:'The Staff Performance Appraisal System (SPAS) has two forms: Form 1 for Job Groups A–H and Form 2 for Job Groups J–T. Rating: Excellent (≥130%): 1.00–2.40, Very Good (100–130%): 2.40–3.00, Good (70–100%): 3.00–3.60, Fair (50–70%): 3.60–4.00, Poor (<50%): 4.00–5.00.' },
    { title:'Performance Contracting', icon:'assignment_turned_in', content:'Rate your department\'s achievement (0–200%) across 7 weighted criteria: Service Delivery (25%), Financial Management (20%), HR Management (15%), Governance & Accountability (15%), Projects & Programmes (15%), Innovation & ICT (5%), Partnerships (5%). Deadline: July 31 each year.' },
    { title:'Skills Audit', icon:'psychology', content:'Complete skills audit across 10 domains: Leadership, Financial Management, ICT, Legal, Planning & M&E, HRM, Supply Chain, Communication, Technical/Professional, and Service Delivery. Rate competencies 1–5 (Awareness to Expert). Required for KDSP II compliance.' },
    { title:'Organogram', icon:'account_tree', content:'View the colorful 3D county organogram showing all 12 departments/entities based on the Approved Staff Establishment of March 27, 2026 (4,755 total cadres). Click any department to see its detailed structure, Chief Officers, Directorates, and staffing levels.' },
    { title:'Reports', icon:'bar_chart', content:'Generate and download PDF reports: Employee Profile Report, SPAS Appraisal Report, and Document Submission Checklist. HR Administrators can generate staff registers by department in PDF or Excel format.' },
    { title:'Technical Support', icon:'support_agent', content:'For technical support contact the ICT Directorate: Director James M. Mburu, Department of Education, Vocational Training, ICT & Library Services. Email: ict@garissa.go.ke | Tel: 020-XXXXXXX. System: Garissa HRMS v1.0 (KDSP II)' },
  ];
  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header"><div class="card-title">Help Manual & User Guide</div></div>
      <p style="font-size:14px;color:var(--t2);">Garissa County HRMS — Human Resource Management System | KDSP II Programme</p>
    </div>
    <div style="display:grid;gap:12px;">
      ${topics.map((t,i) => `
        <div class="card" style="cursor:pointer;" onclick="this.querySelector('.help-content').style.display=this.querySelector('.help-content').style.display==='none'?'block':'none'">
          <div class="card-header" style="cursor:pointer;">
            <div style="display:flex;align-items:center;gap:12px;">
              <span class="material-icons" style="color:var(--p);">${t.icon}</span>
              <div class="card-title">${i+1}. ${t.title}</div>
            </div>
            <span class="material-icons" style="color:var(--t2);">expand_more</span>
          </div>
          <div class="help-content" style="display:none;padding-top:8px;font-size:14px;color:var(--t2);line-height:1.7;">${t.content}</div>
        </div>`).join('')}
    </div>`;
}

// ─── Admin Panel ──────────────────────────────────────────────────────────────
async function renderAdmin() {
  const container = document.getElementById('admin-container');
  if (!container) return;
  if (!['admin','hr_director','hr_officer'].includes(userProfile?.role)) {
    container.innerHTML = '<div class="card"><p style="color:var(--err);">Access denied. Admin role required.</p></div>';
    return;
  }
  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header"><div class="card-title">Staff Search & Management</div></div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <input type="text" id="admin-search" class="form-control" style="flex:1;" placeholder="Search by name, UPN, email...">
        <select id="admin-dept-filter" class="form-control" style="width:220px;">
          <option value="">All Departments</option>
          ${DEPARTMENTS.map(d=>`<option value="${d.id}">${d.shortName}</option>`).join('')}
        </select>
        <button class="btn btn-primary" onclick="adminSearch()">
          <span class="material-icons" style="font-size:16px;">search</span> Search
        </button>
      </div>
    </div>
    <div id="admin-results"></div>
    <div class="card" style="margin-top:20px;">
      <div class="card-header"><div class="card-title">Staff Establishment Summary (2026)</div></div>
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <thead><tr style="background:#f3f4f6;">
            <th style="padding:10px;text-align:left;border-bottom:2px solid var(--brd);">Department</th>
            <th style="padding:10px;text-align:center;">Authorized</th>
            <th style="padding:10px;text-align:center;">In Post</th>
            <th style="padding:10px;text-align:center;">Vacancy</th>
            <th style="padding:10px;text-align:center;">Fill Rate</th>
          </tr></thead>
          <tbody>
            ${DEPARTMENTS.map(d=>{
              const vac = d.authorized - d.inPost;
              const pct = Math.round((d.inPost/d.authorized)*100);
              const pctColor = pct>=90?'#2E7D32':pct>=70?'#F57F17':'#B71C1C';
              return `<tr style="border-bottom:1px solid var(--brd);">
                <td style="padding:10px;font-weight:600;">${d.shortName}</td>
                <td style="padding:10px;text-align:center;">${d.authorized}</td>
                <td style="padding:10px;text-align:center;">${d.inPost}</td>
                <td style="padding:10px;text-align:center;color:${vac>0?'#B71C1C':'#2E7D32'};">${vac}</td>
                <td style="padding:10px;text-align:center;">
                  <div style="display:flex;align-items:center;gap:6px;">
                    <div style="flex:1;height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;">
                      <div style="height:100%;width:${Math.min(pct,100)}%;background:${pctColor};border-radius:3px;"></div>
                    </div>
                    <span style="color:${pctColor};font-weight:700;min-width:38px;">${pct}%</span>
                  </div>
                </td>
              </tr>`;}).join('')}
            <tr style="background:#f3f4f6;font-weight:700;">
              <td style="padding:10px;">TOTAL</td>
              <td style="padding:10px;text-align:center;">4,755</td>
              <td style="padding:10px;text-align:center;">${DEPARTMENTS.reduce((s,d)=>s+d.inPost,0)}</td>
              <td style="padding:10px;text-align:center;color:#B71C1C;">${4755-DEPARTMENTS.reduce((s,d)=>s+d.inPost,0)}</td>
              <td style="padding:10px;text-align:center;">${Math.round(DEPARTMENTS.reduce((s,d)=>s+d.inPost,0)/4755*100)}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>`;
}

async function adminSearch() {
  const q = document.getElementById('admin-search')?.value.trim().toLowerCase();
  const dept = document.getElementById('admin-dept-filter')?.value;
  const res = document.getElementById('admin-results');
  if (!res) return;
  try {
    let qRef = collection(db,'users');
    const snap = await getDocs(qRef);
    let users = [];
    snap.forEach(d => {
      const data = d.data();
      if (dept && data.department !== dept) return;
      if (q) {
        const str = `${data.displayName||''} ${data.email||''} ${data.upn||''}`.toLowerCase();
        if (!str.includes(q)) return;
      }
      users.push(data);
    });
    if (users.length === 0) { res.innerHTML = '<div class="card"><p style="color:var(--t2);">No staff found.</p></div>'; return; }
    res.innerHTML = `<div class="card"><div class="card-header"><div class="card-title">Results (${users.length})</div></div>
      <div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead><tr style="background:#f3f4f6;">
          <th style="padding:8px;text-align:left;">Name</th>
          <th style="padding:8px;">UPN</th>
          <th style="padding:8px;">Department</th>
          <th style="padding:8px;">Designation</th>
          <th style="padding:8px;">Role</th>
          <th style="padding:8px;">Profile</th>
        </tr></thead><tbody>
        ${users.slice(0,100).map(u => {
          const d = DEPARTMENTS.find(dd=>dd.id===u.department);
          return `<tr style="border-bottom:1px solid var(--brd);">
            <td style="padding:8px;font-weight:600;">${u.displayName||u.firstName||'—'}</td>
            <td style="padding:8px;">${u.upn||'—'}</td>
            <td style="padding:8px;">${d?.shortName||u.department||'—'}</td>
            <td style="padding:8px;">${u.designation||'—'}</td>
            <td style="padding:8px;"><span class="badge badge-blue">${u.role||'user'}</span></td>
            <td style="padding:8px;"><span class="badge ${u.profileComplete?'badge-green':'badge-orange'}">${u.profileComplete?'Complete':'Pending'}</span></td>
          </tr>`;}).join('')}
        </tbody></table></div></div>`;
  } catch(e) { toast('Search failed: '+e.message,'error'); }
}
window.adminSearch = adminSearch;

function saveSettings() {
  toast('Settings saved', 'success');
}
window.saveSettings = saveSettings;

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  populateDeptDropdowns();

  // Add CSS for stat cards, doc cards, etc.
  const style = document.createElement('style');
  style.textContent = `
    .stat-card{background:#fff;border-radius:16px;padding:20px;text-align:center;cursor:pointer;
      box-shadow:0 4px 24px rgba(0,0,0,.09);border:1px solid #e2e8f0;transition:all .2s;}
    .stat-card:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.14);}
    .stat-card.blue .stat-icon{color:#1565C0;} .stat-card.green .stat-icon{color:#2E7D32;}
    .stat-card.orange .stat-icon{color:#E65100;} .stat-card.purple .stat-icon{color:#6A1B9A;}
    .stat-val{font-size:22px;font-weight:800;margin:8px 0;}
    .stat-label{font-size:12px;color:var(--t2);}
    #dash-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;margin-bottom:24px;}
    .doc-card{display:flex;align-items:center;gap:12px;padding:12px;border:2px solid var(--brd);border-radius:10px;background:#fafafa;}
    .doc-card.uploaded{border-color:#4CAF50;background:#f1f8f1;}
    .doc-icon{color:#9CA3AF;font-size:32px;flex-shrink:0;}
    .doc-card.uploaded .doc-icon{color:#2E7D32;}
    .doc-name{font-size:13px;font-weight:600;color:var(--t1);}
    .doc-status{font-size:11px;color:var(--t2);margin-top:2px;}
    .doc-actions{margin-left:auto;display:flex;gap:6px;flex-shrink:0;}
    .report-card{cursor:pointer;transition:all .2s;text-align:center;}
    .report-card:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.14);}
    #toast-container{position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:10px;}
    .wizard-progress{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:4px;margin-bottom:24px;}
    .wizard-step{display:flex;align-items:center;flex-direction:column;gap:4px;min-width:80px;}
    .step-circle{width:32px;height:32px;border-radius:50%;background:#e2e8f0;color:var(--t2);
      display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;}
    .wizard-step.active .step-circle{background:var(--p);color:#fff;}
    .wizard-step.done .step-circle{background:#2E7D32;color:#fff;}
    .step-label{font-size:10px;color:var(--t2);text-align:center;max-width:70px;}
    .wizard-step.active .step-label{color:var(--p);font-weight:600;}
    .step-line{height:2px;flex:1;background:#e2e8f0;min-width:20px;align-self:flex-start;margin-top:15px;}
  `;
  document.head.appendChild(style);
});
