// --- SELECTORS ---
const tableBody = document.getElementById('transaction-table-body');
const form = document.getElementById("new-transaction"); 
const editForm = document.getElementById("edit-transaction-form");

// --- FAKE DATABASE (Stored in your RAM for testing) ---
let mockTransactions = [
    { id: 101, date: "2026-01-15", from: "Airtel", to: "Food", description: "Lunch at Mamma Mia", amount: 15000 },
    { id: 102, date: "2026-01-14", from: "Standard Bank", to: "Rent", description: "January Rent", amount: 250000 },
    { id: 103, date: "2026-01-13", from: "Cash", to: "Fuel", description: "Puma Station", amount: 45000 }
];

// 1. Load History (Uses the array above)
function loadTransactions() {
    tableBody.innerHTML = '';
    
    mockTransactions.forEach(element => {
        const rowID = `txn-${element.id}`;
        const row = `
        <tr id="${rowID}">
            <td>${element.date}</td>
            <td>${element.from} -> ${element.to}</td>
            <td>${element.description}</td>
            <td>${Number(element.amount).toLocaleString()}</td>
            <td>
                <div class="table-btn">
                    <button onclick="handleEdit('${rowID}')" class="btn-edit">
                        <img src="../icons/edit-2-svgrepo-com.svg" alt="Edit">
                    </button>
                    <button onclick="deleteTransaction('${rowID}')" class="btn-delete">
                        <img src="../icons/delete-1487-svgrepo-com.svg" alt="Delete">
                    </button>
                </div>
            </td>
        </tr>`;  
        tableBody.insertAdjacentHTML('beforeend', row);
    });
}

// 2. Form Submission (Adds to our fake array)
function newTransaction() {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Create a fake new ID
    const newEntry = {
        id: Math.floor(Math.random() * 1000),
        date: data.date,
        from: "New", // Simplified for test
        to: "Entry",
        description: data.description,
        amount: Number(data.amount)
    };

    mockTransactions.unshift(newEntry); // Add to start of list
    loadTransactions(); 
    form.reset();
    console.log("Mock Add Successful");
}

// 3. Delete Transaction
function deleteTransaction(transID) {
    const numericId = parseInt(transID.replace('txn-', ''));
    mockTransactions = mockTransactions.filter(t => t.id !== numericId);
    
    const row = document.getElementById(transID);
    if (row) row.remove();
    console.log("Mock Delete Successful");
}

// 4. Handle Edit (Fills the form)
function handleEdit(transID) {
    const row = document.getElementById(transID);
    
    // Grab data from the row
    const date = row.cells[0].innerText;
    const desc = row.cells[2].innerText;
    const amount = row.cells[3].innerText.replace(/,/g, '');

    // Fill Edit Form
    editForm.querySelector('[name="edit-date"]').value = date;
    editForm.querySelector('[name="edit-description"]').value = desc;
    editForm.querySelector('[name="edit-amount"]').value = amount;
    
    editForm.dataset.editingId = transID;
    showEditModal(); // Calling your UI function!
}

// 5. Update Transaction
function editTransaction() {
    const transID = editForm.dataset.editingId;
    const numericId = parseInt(transID.replace('txn-', ''));
    
    const formData = new FormData(editForm);
    const updatedData = Object.fromEntries(formData.entries());

    // Update the record in our fake array
    const index = mockTransactions.findIndex(t => t.id === numericId);
    if (index !== -1) {
        mockTransactions[index].date = updatedData['edit-date'];
        mockTransactions[index].description = updatedData['edit-description'];
        mockTransactions[index].amount = Number(updatedData['edit-amount']);
    }

    hideEditModal();
    loadTransactions();
    console.log("Mock Update Successful");
}

// --- EVENT LISTENERS ---
document.addEventListener('DOMContentLoaded', () => {
    // Re-select them here to be absolutely safe
    const form = document.getElementById("new-transaction"); 
    const editForm = document.getElementById("edit-transaction-form");

    if (form) {
        form.addEventListener('submit', (e) => { 
            e.preventDefault(); 
            newTransaction(); 
        });
        console.log("Add Form found and connected.");
    } else {
        console.error("CRITICAL: Form 'new-transaction' NOT found. Check for spaces in your HTML ID!");
    }

    if (editForm) {
        editForm.addEventListener('submit', (e) => { 
            e.preventDefault(); 
            editTransaction(); 
        });
        console.log("Edit Form found and connected.");
    }

    // Initial Load
    loadTransactions();
});