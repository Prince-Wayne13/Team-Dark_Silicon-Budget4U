document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('transaction-table-body');
    const addForm = document.getElementById("new-transaction");
    const container = document.getElementById('container');
    const modal = document.getElementById('modal-container');

    function toggleModal(show) {
        if (show) {
            modal.classList.remove('hidden');
            modal.classList.add('modal-container');
            container.classList.add('blurred');
        } else {
            modal.classList.add('hidden');
            modal.classList.remove('modal-container');
            container.classList.remove('blurred');
        }
    }

    async function loadTransactions() {
        const res = await fetch('/api/transactions');
        const data = await res.json();
        tableBody.innerHTML = '';

        data.forEach(item => {
            const isInc = item.Direction === 'INCOMING';
            const row = `
                <tr>
                    <td>${item.date}</td>
                    <td><strong>${item.fromTo}</strong></td>
                    <td>${item.description}</td>
                    <td><span class="badge ${isInc ? 'positive' : 'negative'}">${item.Direction}</span></td>
                    <td>MK ${Number(item.amount).toLocaleString()}</td>
                    <td><button class="btn-delete">Delete</button></td>
                </tr>`;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    }

    addForm.onsubmit = async (e) => {
        e.preventDefault();
        const payload = Object.fromEntries(new FormData(addForm).entries());

        const res = await fetch('/api/transactions/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            toggleModal(false);
            addForm.reset();
            loadTransactions();
        }
    };

    document.getElementById('openBtn').onclick = () => toggleModal(true);
    document.getElementById('closeBtn').onclick = () => toggleModal(false);

    loadTransactions(); // Run on startup
});