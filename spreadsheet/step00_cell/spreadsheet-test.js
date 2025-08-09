QUnit.module('Cell', hooks => {

    QUnit.test('value types decided by input', assert => {
      const valueTypes = {
        'abc': 'text',
        '12.5': 'number',
        '=A1': 'formula'
      };
      let cell = new Cell();
      for (const value in valueTypes) {
        cell.setInput(value);
        assert.equal(valueTypes[value], cell.valueType());
      }
    });
});
