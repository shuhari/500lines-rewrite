class Cell {
    
    constructor() {
        this.setInput('');
    }

    setInput(value) {
        value = String(value).trim();
        this._input = value;

        let type = 'text';
        if (!Number.isNaN(parseFloat(value))) {
            type = 'number';
        }
        else if (value.length > 0 && value.charAt(0) == '=') {
            type = 'formula';
        }
        this._type = type;
    }

    valueType() { return this._type; }
    input() { return this._input; }
    formula() {
        const formula = this._input.substring(1);
        const hasRef = /[A-Z]+\d+/.test(this._input);
        return [formula, hasRef];
    }
    calc() {
        const value = this.input();
        switch (this.valueType()) {
            case 'text':
                return value;
            case 'number':
                return parseFloat(value);
            case 'formula':
                let [formula, hasRef] = this.formula();
                try {
                    return eval(formula);
                } catch(e) {
                    return e;
                }
            default:
                return new Error(`Unsupported value: ${this._input}`);
        }
    }
}


class Spreadsheet {
    
    constructor(rows, cols) {
        this.reset(rows, cols);
    }

    reset(rows, cols) {
        this._rows = rows;
        this._cols = cols;
        this._cells = {};
        for (let row=0; row<this._rows; row++) {
            for (let col=0; col<this._cols; col++) {
                const coord = getCoord(row, col);
                this._cells[coord] = new Cell();
            }
        }
    }

    setInput(coord, value) {
        let cell = new Cell();
        cell.setInput(value);
        this._cells[coord] = cell;
    }

    serialize() {
        let data = { rows: this._rows, cols: this._cols, cells: {} };
        for (let coord in this._cells) {
            data.cells[coord] = this._cells[coord].input();
        }
        return JSON.stringify(data);
    }

    deserialize(value) {
        if (typeof(value) === 'string') {
            value = JSON.parse(value);
        }
        let { rows, cols, cells } = value;
        this.reset(rows, cols);
        for (let coord in cells) {
            this.setInput(coord, cells[coord]);
        }
    }

    input(coord) {
        return this._cells[coord].input();
    }

    calc() {
        /*
        impl calc, but formula with empty cell return NaN

        const coords = Object.keys(this._cells);

        let container = {};
        coords.forEach(coord => {
            let cell = this._cells[coord];
            let getter = undefined;
            if (!cell.isFormula() || !cell.hasRef()) {
                getter = () => cell.calc();
            } else {
                let formula = cell.formula();
                let transformed = 'return ' + Spreadsheet.transformFormula(formula); 
                getter = () => new Function(transformed).call(container);
            }
            Object.defineProperty(container, coord, {get: getter });
        });

        let result = {};
        coords.forEach(coord => {
            result[coord] = container[coord];
        });
        return result;
        */
        const coords = Object.keys(this._cells);
        let container = {};
        coords.forEach(coord => {
            let cell = this._cells[coord];
            const [formula, hasRef] = cell.formula();
            let getter = undefined;
            if (!formula || !hasRef) {
                getter = () => cell.calc();
            } else {
                let transformed = 'return ' + transformFormula(formula); 
                getter = () => new Function(transformed).call(container);
            }
            Object.defineProperty(container, coord, { get: getter });
        });

        let result = {};
        coords.forEach(coord => {
            result[coord] = container[coord];
        });
        return result;
    }
}

function getCoord(row, col) {
    let colName = String.fromCharCode('A'.charCodeAt() + col);
    let rowName = String(row + 1);
    return `${colName}${rowName}`;
}


function transformFormula(formula) {
    const pattern = /(?<![a-zA-Z.$])([A-Z]+)(\d+)/g;
    return formula.replace(pattern, (match, letters, numbers) => {
        return `this.${letters}${numbers}`;
    });
}
