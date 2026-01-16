// --- SELECTORS ---
const container = document.getElementById('container');
const modalWrapper = document.getElementById('modal-container'); // General wrapper

// Specific Modals
const editTransactionModal = document.getElementById('edit-transaction-modal');
const importModal = document.getElementById('import-modal');
const smsModal = document.getElementById('sms-redirect-modal');

// SMS View Elements
const initialView = document.getElementById('initial-view');
const loadingView = document.querySelector('.loading-view');
const runSyncBtn = document.getElementById('runSyncBtn');

// --- HELPER FUNCTIONS ---
// Simplifies opening/closing and handles the blur
function toggleModal(modalTarget, show = true) {
    if (show) {
        modalTarget.classList.remove('hidden');
        modalTarget.classList.add('modal-container');
        container.classList.add('blurred');
    } else {
        modalTarget.classList.remove('modal-container');
        modalTarget.classList.add('hidden');
        container.classList.remove('blurred');
    }
}

// --- EDIT TRANSACTION FUNCTIONS ---
function showEditModal() {
    toggleModal(editTransactionModal, true);
}

function hideEditModal() {
    toggleModal(editTransactionModal, false);
}

// --- IMPORT MODAL FUNCTIONS (General) ---
function showImportModal() {
    toggleModal(importModal, true);
}

function hideImportModal() {
    toggleModal(importModal, false);
}

// --- SMS REDIRECT MODAL FUNCTIONS ---
function showSmsModal() {
    // RESET: Ensure we always see the promo view first when opening
    if (initialView && loadingView) {
        initialView.classList.remove('hidden');
        loadingView.classList.add('hidden');
    }
    toggleModal(smsModal, true);
}

function hideSmsModal() {
    toggleModal(smsModal, false);
}

// THE "VIEW SWAPPER" FOR SYNCING
function startSmsSync() {
    if (initialView && loadingView) {
        initialView.classList.add('hidden');
        loadingView.classList.remove('hidden');
        console.log("Fintel4U: AI Sync Process Initiated...");
    }
}

// --- GENERAL MODAL FUNCTIONS ---
function showGeneralModal() {
    toggleModal(modalWrapper, true);
}

function hideGeneralModal() {
    toggleModal(modalWrapper, false);
}

// --- EVENT LISTENERS ---

// Use Optional Chaining (?.) so script doesn't break if an ID is missing on certain pages

// 1. Edit Transactions
document.getElementById('openEditTransaction')?.addEventListener('click', showEditModal);
document.getElementById('closeEditTransaction')?.addEventListener('click', hideEditModal);

// 2. SMS Import / Redirect
document.getElementById('openImport')?.addEventListener('click', showSmsModal); 
document.getElementById('closeRedirect')?.addEventListener('click', hideSmsModal);
runSyncBtn?.addEventListener('click', startSmsSync);

// 3. General Buttons
document.getElementById('openBtn')?.addEventListener('click', showGeneralModal);
document.getElementById('closeBtn')?.addEventListener('click', hideGeneralModal);

// 4. Close on Click Outside (Optional UX fix)
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-container')) {
        hideEditModal();
        hideImportModal();
        hideSmsModal();
        hideGeneralModal();
    }
});