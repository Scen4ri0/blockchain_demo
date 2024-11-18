async function loadChain() {
      try {
          const response = await fetch('/api/chain');
          if (!response.ok) throw new Error(`Failed to fetch blockchain: ${response.statusText}`);
  
          const chain = await response.json();
          const visualization = d3.select("#blockchain-visualization")
                                  .html("") // Очистка перед отрисовкой
                                  .append("svg")
                                  .attr("width", 800) // Фиксированная ширина
                                  .attr("height", Math.ceil(chain.length / 4) * 200); // Высота зависит от количества блоков
  
          if (chain.length === 0) {
              d3.select("#output").html("<p>No blocks in the blockchain.</p>");
              return;
          }
  
          const blockWidth = 150;
          const blockHeight = 100;
          const blockSpacingX = 200; // Расстояние между блоками по горизонтали
          const blockSpacingY = 150; // Расстояние между блоками по вертикали
  
          const blocks = visualization.selectAll(".block")
                                      .data(chain)
                                      .enter()
                                      .append("g")
                                      .attr("class", "block")
                                      .attr("transform", (d, i) => {
                                          const row = Math.floor(i / 4); // Четыре блока в ряду
                                          const col = i % 4; // Колонка
                                          return `translate(${col * blockSpacingX + 50}, ${row * blockSpacingY + 50})`;
                                      })
                                      .on("click", (event, d) => {
                                          alert(`Block Index: ${d.index}\nHash: ${d.hash}\nPrevious Hash: ${d.previous_hash}\nData: ${d.data}`);
                                      }); // Интерактивность на клике
  
          // Прямоугольники для блоков
          blocks.append("rect")
                .attr("width", blockWidth)
                .attr("height", blockHeight)
                .attr("rx", 10)
                .attr("ry", 10)
                .style("fill", "#4caf50")
                .style("stroke", "#333")
                .style("stroke-width", 2);
  
          // Текст: индекс блока
          blocks.append("text")
                .attr("x", blockWidth / 2)
                .attr("y", blockHeight / 4)
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .style("fill", "white")
                .style("font-size", "14px")
                .text(d => `Index: ${d.index}`);
  
          // Текст: хэш блока
          blocks.append("text")
                .attr("x", blockWidth / 2)
                .attr("y", blockHeight / 2)
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .style("fill", "white")
                .style("font-size", "12px")
                .text(d => `Hash: ${d.hash.slice(0, 6)}...`)
                .append("title")
                .text(d => `Full Hash: ${d.hash}`);
  
          // Текст: предыдущий хэш
          blocks.append("text")
                .attr("x", blockWidth / 2)
                .attr("y", (blockHeight / 4) * 3)
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .style("fill", "white")
                .style("font-size", "12px")
                .text(d => `Prev: ${d.previous_hash.slice(0, 6)}...`)
                .append("title")
                .text(d => `Previous Hash: ${d.previous_hash}`);
      } catch (error) {
          d3.select("#output").html(`<p style="color:red;">Error: ${error.message}</p>`);
          console.error("Blockchain Visualization Error:", error);
      }
  }
  