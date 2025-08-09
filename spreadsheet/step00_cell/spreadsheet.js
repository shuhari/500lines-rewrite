class Cell {
    setInput(value) {
        value = String(value).trim();
        this._input = value;

        let type = 'text';
        if (!Number.isNaN(+value)) {
            type = 'number';
        }
        else if (value.length > 0 && value.charAt(0) == '=') {
            type = 'formula';
        }
        this._type = type;
    }

    valueType() { return this._type; }
    input() { return this._input; }
}
