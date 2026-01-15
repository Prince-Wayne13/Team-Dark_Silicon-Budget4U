// EDIT TRANSACTION MODAL
const openEditTransaction = document.getElementById('openEditTransaction');
const closeEditTransaction = document.getElementById('closeEditTransaction');
const editTransactionModal = document.getElementById('edit-transaction-modal');

openEditTransaction.addEventListener('click', () => {
    editTransactionModal.classList.remove('hidden');
    editTransactionModal.classList.add('modal-container');
    container.classList.add('blurred');
});

closeEditTransaction.addEventListener('click', () => {
    editTransactionModal.classList.remove('modal-container');
    editTransactionModal.classList.add('hidden');
    container.classList.remove('blurred');
});

// IMPORT MODAL
const openImport = document.getElementById('openImport');
const closeImport = document.getElementById('closeImport');
const importModal = document.getElementById('import-modal');

openImport.addEventListener('click', () => {
    importModal.classList.remove('hidden');
    importModal.classList.add('modal-container');
    container.classList.add('blurred');
});

closeImport.addEventListener('click', () => {
    importModal.classList.remove('modal-container');
    importModal.classList.add('hidden');
    container.classList.remove('blurred');
});
const openBtn = document.getElementById('openBtn');
const closeBtn = document.getElementById('closeBtn');
const modal = document.getElementById('modal-container');
const container = document.getElementById('container');

// Open Modal
openBtn.addEventListener('click', () => {
  modal.classList.remove('hidden');
  modal.classList.add('modal-container');
  container.classList.add('blurred');
});

// Close Modal
closeBtn.addEventListener('click', () => {
  modal.classList.remove('modal-container');
  modal.classList.add('hidden');
  container.classList.remove('blurred');
});
