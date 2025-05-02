export function updateGrid(grid, previousGrid=null, newTilePosition = null) {
    const gridContainer = document.getElementById("grid-container");

    let html = "<table>";
    for (let i = 0; i < grid.length; i++) { 
        html += "<tr>";
        for (let j = 0; j < grid[i].length; j++) {
            const value = grid[i][j];
            const prevValue = previousGrid ? previousGrid[i][j] : 0; 
            const cellValue = value === 0 ? "" : value;
            
            // Determine if tile is new or merged
            let extraClass = "";
            if (value !== 0) {
                if (previousGrid === null) {
                    // Initial grid load, no animations
                    extraClass = "";
                } else if (newTilePosition && newTilePosition[0] === i && newTilePosition[1] === j) {
                    // Only apply new animation to the actual new tile
                    extraClass = "tile-new";
                } else if (value === prevValue * 2) {
                    // Tiles merged
                    extraClass = "tile-merged";
                }
            }
            const tileClass = `tile-${value || 0} ${extraClass}`.trim();
            html += `<td class="${tileClass}">${cellValue}</td>`;
        }
        html += "</tr>";
    }
        html += "</table>";
        gridContainer.innerHTML = html;
}