export function updateGrid(grid) {
    console.log("Rendering Grid:", grid);  // DEBUG LOG
    const gridContainer = document.getElementById("grid-container");
    console.log("Grid Container Element:", gridContainer);  // DEBUG LOG

    let html = "<table>";
    for (let i = 0; i < grid.length; i++) {
        html += "<tr>";
        for (let j = 0; j < grid[i].length; j++) {
            const value = grid[i][j];
            const cellValue = value === 0 ? "" : value;
            let tileClass = "tile-" + (value || 0);
            html += `<td class="${tileClass}">${cellValue}</td>`;
        }
        html += "</tr>";
    }
    html += "</table>";
    gridContainer.innerHTML = html;
}