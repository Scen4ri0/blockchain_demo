async function handleError(response) {
    const errorText = await response.text();
    console.error("Error response:", errorText);
    return errorText || response.statusText;
}

async function addBlock() {
    const blockData = document.getElementById("blockData").value.trim();
    if (!blockData) {
        alert("Please enter block data.");
        return;
    }

    try {
        const response = await fetch('/api/add_block', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: blockData }),
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            fetchChain(); // Обновление цепочки
        } else {
            const errorText = await handleError(response);
            alert(`Error: ${errorText}`);
        }
    } catch (error) {
        console.error("Error adding block:", error);
        alert("Failed to add block. Please try again.");
    }
}

async function validateBlockchain() {
    try {
        const response = await fetch('/api/validate');
        const result = await response.json();

        const outputDiv = document.getElementById("output");
        outputDiv.innerHTML = ""; // Очистка предыдущего вывода

        // Показ результата валидации
        const resultText = document.createElement("div");
        resultText.textContent = result.steps[0].details;
        resultText.style.color = result.valid ? "green" : "red";
        resultText.style.fontWeight = "bold";
        resultText.style.marginBottom = "20px";
        outputDiv.appendChild(resultText);

        // Отображение отладочной информации
        result.steps.slice(1).forEach(step => {
            const stepDiv = document.createElement("div");
            stepDiv.className = "validation-step";
            stepDiv.style.border = step.status === "valid" ? "1px solid green" : "1px solid red";
            stepDiv.style.backgroundColor = step.status === "valid" ? "#e8ffe8" : "#ffe8e8";

            const blockInfo = document.createElement("p");
            blockInfo.textContent = `Block: ${step.block}`;
            stepDiv.appendChild(blockInfo);

            const stepInfo = document.createElement("p");
            stepInfo.textContent = `Step: ${step.step}`;
            stepDiv.appendChild(stepInfo);

            const details = document.createElement("p");
            details.textContent = `Details: ${step.details}`;
            stepDiv.appendChild(details);

            outputDiv.appendChild(stepDiv);
        });
    } catch (error) {
        console.error("Error validating blockchain:", error);
        alert("Failed to validate blockchain. Please try again.");
    }
}

async function createTransaction() {
    const sender = document.getElementById("transactionSender").value;
    const recipient = document.getElementById("transactionRecipient").value;
    const amount = document.getElementById("transactionAmount").value;

    if (!sender || !recipient || !amount) {
        alert("Please fill in all transaction fields.");
        return;
    }

    try {
        const response = await fetch('/api/create_transaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender, recipient, amount }),
        });

        const result = await response.json();
        if (response.ok) {
            alert("Transaction created successfully!");
            fetchPendingTransactions(); // Обновляем ожидающие транзакции
        } else {
            const errorText = await handleError(response);
            alert(`Error: ${errorText}`);
        }
    } catch (error) {
        console.error("Error creating transaction:", error);
        alert("Failed to create transaction. Please try again.");
    }
}

async function fetchPendingTransactions() {
    try {
        const response = await fetch('/api/pending_transactions');
        const transactions = await response.json();

        const outputDiv = document.getElementById("pendingTransactionsOutput");
        outputDiv.innerHTML = ""; // Очистка предыдущих данных

        transactions.forEach(tx => {
            const txDiv = document.createElement("div");
            txDiv.className = "validation-step";
            txDiv.style.border = "1px solid #ccc";
            txDiv.style.marginBottom = "10px";
            txDiv.style.padding = "10px";
            txDiv.innerHTML = `
                <p><strong>Sender:</strong> ${tx.sender}</p>
                <p><strong>Recipient:</strong> ${tx.recipient}</p>
                <p><strong>Amount:</strong> ${tx.amount}</p>
            `;
            outputDiv.appendChild(txDiv);
        });
    } catch (error) {
        console.error("Error fetching pending transactions:", error);
        alert("Failed to load pending transactions.");
    }
}

async function fetchChain() {
    try {
        const response = await fetch('/api/chain');
        const chain = await response.json();

        const chainDiv = document.getElementById("blockchainOutput");
        chainDiv.innerHTML = ""; // Очистка предыдущих данных

        chain.forEach(block => {
            const blockDiv = document.createElement("div");
            blockDiv.className = "validation-step";
            blockDiv.style.border = "1px solid #ccc";
            blockDiv.style.marginBottom = "10px";
            blockDiv.style.padding = "10px";
            blockDiv.innerHTML = `
                <p><strong>Index:</strong> ${block.index}</p>
                <p><strong>Timestamp:</strong> ${new Date(block.timestamp * 1000).toLocaleString()}</p>
                <p><strong>Hash:</strong> ${block.hash}</p>
                <p><strong>Previous Hash:</strong> ${block.previous_hash}</p>
                <p><strong>Transactions:</strong></p>
                <ul>
                    ${block.transactions.map(tx => `
                        <li>Sender: ${tx.sender}, Recipient: ${tx.recipient}, Amount: ${tx.amount}</li>
                    `).join("")}
                </ul>
            `;
            chainDiv.appendChild(blockDiv);
        });
    } catch (error) {
        console.error("Error fetching chain:", error);
        alert("Failed to load blockchain.");
    }
}

async function mineTransactions() {
    const minerAddress = prompt("Enter miner address:");
    if (!minerAddress) {
        alert("Miner address is required.");
        return;
    }

    try {
        const response = await fetch('/api/mine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ miner: minerAddress }),
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById("output").innerText = result.message;
            alert("Block mined successfully!");
            fetchChain(); // Обновление блокчейна
            fetchPendingTransactions(); // Очистка ожидающих транзакций
        } else {
            const errorText = await handleError(response);
            alert(`Error: ${errorText}`);
        }
    } catch (error) {
        console.error("Error mining transactions:", error);
        alert(`Failed to mine transactions: ${error.message}`);
    }
}


document.addEventListener("DOMContentLoaded", () => {
    fetchChain();
    fetchPendingTransactions();
});
