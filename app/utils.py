def pretty_print_block(block):
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "data": block.data,
        "previous_hash": block.previous_hash,
        "hash": block.hash,
        "nonce": block.nonce
    }
