// https://stackoverflow.com/a/49041392
const getCellValue = (tr, idx) => 
    tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => (
    (v1, v2) => 
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? 
            v1 - v2 : 
            v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

// https://stackoverflow.com/questions/22097155/javascript-get-entire-2nd-column
function column(tab, col) {
    var arr = []
    const n = tab.rows.length;

    for (var i = 0; i < n; i++) {
        const tr = tab.rows[i];
        if (tr.cells.length > col) {
            const td = tr.cells[col];     
            arr.push(td)
        }
    }
    return arr;
}

// do the work...
document.querySelectorAll('th:not(.center_th)')
    .forEach(th => th.addEventListener('click', (() => {
    const table = th.closest('table');
    const col_cells = column(table, 0);
    const txts = column(table, 0).map(c => c.innerText);

    Array.from(table.querySelectorAll('.comp_table_row:nth-child(n+2)'))
        .sort(comparer(
            Array.from(th.parentNode.children).indexOf(th), 
            this.asc = !this.asc))
        .forEach(tr => table.appendChild(tr) );
    for(var y = 0; y < col_cells.length; y++){
        //console.log(y, console.log(col_cells.map(c => c.innerText)))
        table.rows[y].cells[0].innerText = txts[y]
    }
})));
