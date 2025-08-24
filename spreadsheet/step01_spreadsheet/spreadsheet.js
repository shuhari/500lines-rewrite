class Cell {
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
    
    constructor() {
        this.clear();
    }

    clear() {
        this._cells = {};
    }

    setInput(coord, value) {
        let cell = new Cell();
        cell.setInput(value);
        this._cells[coord] = cell;
    }

    calc() {
        const result = {};
        for (let coord in this._cells) {
            let cell = this._cells[coord];
            result[coord] = cell.calc();
        }
        return result;
    }
}