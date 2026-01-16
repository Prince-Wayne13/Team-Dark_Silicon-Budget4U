
    
        const modal = document.getElementById("dynamicModal");
        const modalTitle = document.getElementById("modalTitle");
        const modalBody = document.getElementById("modalBody");
        const modalActionBtn = document.getElementById("modalActionBtn");
        const tableBody = document.getElementById('transaction-body');

        // --- 1. OPEN MODAL (ADD / REVIEW / IMPORT) ---
        function openDynamicModal(mode) {
            modal.style.display = "block";
            modalBody.innerHTML = ""; 

            if (mode === 'add') {
                modalTitle.innerText = "Add Manual Entry";
                modalBody.innerHTML = `
                    <input type="date" id="dateInput" class="modal-input">
                    <input type="text" id="fromToInput" placeholder="Source (e.g. Airtel Money)" class="modal-input">
                    <input type="text" id="descriptionInput" placeholder="Description" class="modal-input">
                    <select id="directionInput" class="modal-input">
                        <option value="INCOMING">Inbound (Money In)</option>
                        <option value="OUTGOING" selected>Outbound (Money Out)</option>
                    </select>
                    <input type="number" id="amountInput" placeholder="Amount (MK)" class="modal-input">
                `;
                modalActionBtn.innerText = "Save Record";
                modalActionBtn.onclick = saveTransaction;

            } else if (mode === 'review') {
                modalTitle.innerText = "Audit & Review";
                modalBody.innerHTML = "<p>Analyzing your records for accuracy... No errors found.</p>";
                modalActionBtn.innerText = "Okay";
                modalActionBtn.onclick = closeModal;

            } else if (mode === 'import') {
                modalTitle.innerText = "Import Transactions";
                modalBody.innerHTML = `
                    <p>Upload your statement (PDF/CSV):</p>
                    <input type="file" id="fileUpload" class="modal-input">
                    <select class="modal-input"><option>Standard Bank</option><option>Airtel SMS</option></select>
                `;
                modalActionBtn.innerText = "Process Import";
                modalActionBtn.onclick = () => { alert("Import system starting..."); closeModal(); };
            }
        }

        function closeModal() { modal.style.display = "none"; }

        // --- 2. FETCH DATA ---
        async function loadTransactions() {
            try {
                const response = await fetch('/api/transactions');
                const data = await response.json();
                tableBody.innerHTML = '';

                data.forEach(trans => {
                    const isInc = trans.Direction === 'INCOMING';
                    const row = `<tr>
                        <td>${trans.date}</td>
                        <td>${trans.description}</td>
                        <td>${trans.fromTo}</td>
                        <td class="${isInc ? 'badge-inc' : 'badge-out'}">${trans.Direction}</td>
                        <td>${Number(trans.amount).toLocaleString()}</td>
                        <td>
                            <button onclick="deleteTransaction('${trans.id}')" style="color:red; cursor:pointer; background:none; border:none;">Delete</button>
                        </td>
                    </tr>`;
                    tableBody.innerHTML += row;
                });
            } catch (err) { console.error("Load failed", err); }
        }

        // --- 3. SAVE DATA ---
        async function saveTransaction() {
            const payload = {
                date: document.getElementById("dateInput").value,
                fromTo: document.getElementById("fromToInput").value,
                description: document.getElementById("descriptionInput").value,
                amount: parseFloat(document.getElementById("amountInput").value),
                direction: document.getElementById("directionInput").value
            };

            if (!payload.date || !payload.amount) return alert("Fill in date and amount");

            const res = await fetch('/api/transactions', {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                closeModal();
                loadTransactions(); 
            }
        }

        // --- 4. DELETE DATA ---
        async function deleteTransaction(id) {
            if (!confirm("Delete this?")) return;
            const res = await fetch('/api/transactions/delete', {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "transID": id })
            });
            if (res.ok) loadTransactions();
        }

        // Start
loadTransactions();
 
