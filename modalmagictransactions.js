// --- SELECTORS ---
const editTransactionModal = document.getElementById('edit-transaction-modal');
const importModal = document.getElementById('import-modal');
const smsModal = document.getElementById('sms-redirect-modal'); // New Selector
const modal = document.getElementById('modal-container');
const container = document.getElementById('container');

// --- EDIT TRANSACTION FUNCTIONS ---
function showEditModal() {
    editTransactionModal.classList.remove('hidden');
    editTransactionModal.classList.add('modal-container');
    container.classList.add('blurred');
}

function hideEditModal() {
    editTransactionModal.classList.remove('modal-container');
    editTransactionModal.classList.add('hidden');
    container.classList.remove('blurred');
}

// --- IMPORT MODAL FUNCTIONS (General) ---
function showImportModal() {
    importModal.classList.remove('hidden');
    importModal.classList.add('modal-container');
    container.classList.add('blurred');
}

function hideImportModal() {
    importModal.classList.remove('modal-container');
    importModal.classList.add('hidden');
    container.classList.remove('blurred');
}

// --- SMS REDIRECT MODAL FUNCTIONS ---
function showSmsModal() {
    smsModal.classList.remove('hidden');
    smsModal.classList.add('modal-container');
    container.classList.add('blurred');
}

function hideSmsModal() {
    smsModal.classList.remove('modal-container');
    smsModal.classList.add('hidden');
    container.classList.remove('blurred');
}

// --- GENERAL MODAL FUNCTIONS ---
function showGeneralModal() {
    modal.classList.remove('hidden');
    modal.classList.add('modal-container');
    container.classList.add('blurred');
}

function hideGeneralModal() {
    modal.classList.remove('modal-container');
    modal.classList.add('hidden');
    container.classList.remove('blurred');
}

// --- EVENT LISTENERS ---

// Edit
document.getElementById('openEditTransaction').addEventListener('click', showEditModal);
document.getElementById('closeEditTransaction').addEventListener('click', hideEditModal);

// SMS / Import Redirect
// We point the "Import" button to the SMS modal now
document.getElementById('openImport').addEventListener('click', showSmsModal); 
document.getElementById('closeRedirect').addEventListener('click', hideSmsModal);

// General
document.getElementById('openBtn').addEventListener('click', showGeneralModal);
document.getElementById('closeBtn').addEventListener('click', hideGeneralModal);
