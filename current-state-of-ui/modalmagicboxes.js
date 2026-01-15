const openCreateBox = document.getElementById('openCreateBox');
const closeCreateBox = document.getElementById('closeCreateBox');
const createBoxModal = document.getElementById('create-box-modal');
const container = document.getElementById('container');

openCreateBox.addEventListener('click', () => {
    createBoxModal.classList.remove('hidden');
    createBoxModal.classList.add('modal-container');
    container.classList.add('blurred');
});

closeCreateBox.addEventListener('click', () => {
    createBoxModal.classList.remove('modal-container');
    createBoxModal.classList.add('hidden');
    container.classList.remove('blurred');
});

// EDIT BOX MODAL
const openEditBox = document.getElementById('openEditBox');
const closeEditBox = document.getElementById('closeEditBox');
const editBoxModal = document.getElementById('edit-box-modal');

openEditBox.addEventListener('click', () => {
    editBoxModal.classList.remove('hidden');
    editBoxModal.classList.add('modal-container');
    container.classList.add('blurred');
});

closeEditBox.addEventListener('click', () => {
    editBoxModal.classList.remove('modal-container');
    editBoxModal.classList.add('hidden');
    container.classList.remove('blurred');
});
