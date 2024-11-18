async function fetchChain() {
    const response = await fetch('/api/chain');
    const chain = await response.json();
    const chainContainer = document.getElementById('chain');
    chainContainer.innerHTML = ''; // Clear previous content

    chain.forEach(block => {
        const blockDiv = document.createElement('div');
        blockDiv.classList.add('block');
        blockDiv.innerHTML = `
            <p><strong>Index:</strong> ${block.index}</p>
            <p><strong>Hash:</strong> ${block.hash.slice(0, 10)}...</p>
            <p><strong>Data:</strong> ${block.data}</p>
        `;
        chainContainer.appendChild(blockDiv);
    });
}

async function addBlock() {
    const blockData = document.getElementById('blockData').value;
    if (!blockData) {
        alert('Please enter data for the block.');
        return;
    }

    const response = await fetch('/api/add_block', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: blockData })
    });

    const result = await response.json();
    document.getElementById('output').innerText = result.message;
    fetchChain();
}

// Initial fetch to populate the chain
fetchChain();
