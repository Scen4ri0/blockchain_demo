# !/bin/bash
docker build -t blockchain-demo .
docker run --rm --network host blockchain-demo

