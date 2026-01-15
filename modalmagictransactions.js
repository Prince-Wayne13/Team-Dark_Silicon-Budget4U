// --- SELECTORS ---
const editTransactionModal = document.getElementById('edit-transaction-modal');
const importModal = document.getElementById('import-modal');
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

// --- IMPORT MODAL FUNCTIONS ---
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
document.getElementById('openEditTransaction').addEventListener('click', showEditModal);
document.getElementById('closeEditTransaction').addEventListener('click', hideEditModal);

document.getElementById('openImport').addEventListener('click', showImportModal);
document.getElementById('closeImport').addEventListener('click', hideImportModal);

document.getElementById('openBtn').addEventListener('click', showGeneralModal);
document.getElementById('closeBtn').addEventListener('click', hideGeneralModal);