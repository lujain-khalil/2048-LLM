/**
 * Updates the grid display with the given grid data
 * @param {Array} grid - 2D array representing the game grid
 */
export function updateGrid(grid) {
    if (!grid || !Array.isArray(grid)) {
        console.error('Invalid grid data:', grid);
        return;
    }
    
    const gridContainer = document.getElementById('grid-container');
    if (!gridContainer) {
        console.error('Grid container element not found');
        return;
    }
    
    // Build the HTML table
    let html = '<table>';
    for (let i = 0; i < grid.length; i++) {
        html += '<tr>';
        for (let j = 0; j < grid[i].length; j++) {
            const value = grid[i][j];
            const cellValue = value === 0 ? '' : value;
            const tileClass = `tile-${value}`;
            html += `<td class="${tileClass}">${cellValue}</td>`;
        }
        html += '</tr>';
    }
    html += '</table>';
    
    // Update the DOM
    gridContainer.innerHTML = html;
}