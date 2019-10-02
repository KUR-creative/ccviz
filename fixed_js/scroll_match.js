const pipe2 = (a, b) => (arg) => b(a(arg));
const pipe = (...ops) => ops.reduce(pipe2)
const tup = f => argtup => f(...argtup)
tap = x => {console.log(x); return x}

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
