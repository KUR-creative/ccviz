const pipe2 = (a, b) => (arg) => b(a(arg));
const pipe = (...ops) => ops.reduce(pipe2)
const tup = f => argtup => f(...argtup)
tap = x => {console.log(x); return x}

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

function scroll(div, lineno, max,min) {
    const real_h = div.scrollHeight - div.clientHeight 
    a = real_h / (max - min) // 913, 26 is 
    b = -min * a
    div.scrollTop = a * lineno + b
}

[...document.querySelectorAll('.comp_table tr')].slice(1).forEach(
    tr => tr.addEventListener('click', (() => {
        const [a_mid, b_mid] =
            [...tr.children]
            .map(x => x.textContent)
            .slice(0,2)
            .map(pipe(
                s => s.split(' ~ '),
                arr => arr.map(Number), 
                //tup( (b,e) => (b+e)/2 )))
                tup( (b,e) => Math.trunc( (b+e)/2 ) )))
                 
        const [a_div,b_div] = 
            [...document.querySelectorAll('.row .column')].slice(0,2);

        const [min, bottom_offset] = [22, 29] // FIXED!
        const [a_max, b_max] = 
            [...document.querySelectorAll('.linenos')]
            .map(pipe(
                x => x.textContent,
                s => s.split('\n'),
                ns => ns[ns.length -1],
                Number,
                n => n - bottom_offset
            ))

        scroll(a_div, a_mid, a_max, min) // same view line
        scroll(b_div, b_mid, b_max, min)
    }
)))
