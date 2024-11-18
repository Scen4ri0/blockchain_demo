async function loadChain() {
    try {
        const response = await fetch('/api/chain');
        if (!response.ok) throw new Error(`Failed to fetch blockchain: ${response.statusText}`);

        const chain = await response.json();
        const blockchainContainer = document.getElementById("blockchain-visualization");
        blockchainContainer.innerHTML = ""; // Очистка контейнера перед отрисовкой

        if (chain.length === 0) {
            blockchainContainer.innerHTML = "<p>No blocks in the blockchain.</p>";
            return;
        }

        chain.forEach(block => {
            const blockDiv = document.createElement("div");
            blockDiv.className = "block";

            blockDiv.innerHTML = `
                <h3>Block Index: ${block.index}</h3>
                <p><strong>Timestamp:</strong> ${new Date(block.timestamp * 1000).toLocaleString()}</p>
                <p><strong>Hash:</strong> ${block.hash}</p>
                <p><strong>Previous Hash:</strong> ${block.previous_hash}</p>
                <p><strong>Transactions:</strong></p>
                <ul>
                    ${
                        block.transactions.length > 0
                            ? block.transactions.map(tx => `
                                <li>
                                    <strong>Sender:</strong> ${tx.sender}, 
                                    <strong>Recipient:</strong> ${tx.recipient}, 
                                    <strong>Amount:</strong> ${tx.amount}
                                </li>
                            `).join("")
                            : "<li>No transactions</li>"
                    }
                </ul>
            `;

            blockchainContainer.appendChild(blockDiv);
        });
    } catch (error) {
        console.error("Error loading blockchain:", error);
        const blockchainContainer = document.getElementById("blockchain-visualization");
        blockchainContainer.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}

// Загружаем блокчейн при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    loadChain();
});
