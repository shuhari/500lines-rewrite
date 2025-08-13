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

QUnit.module('Spreadsheet', hooks => {

  const sheet = new Spreadsheet();

  hooks.before(() => {
    sheet.clear();
  });

  QUnit.test('calc for simple value', assert => {
    const values = {
      'abc': 'abc',
      '12.5': 12.5,
    };
    for (let value in values) {
      sheet.setInput('A1', value);
      const result = sheet.calc();
      assert.equal(values[value], result['A1']);
    }
  });

  QUnit.test('calc for formula without dependencies', assert => {
    sheet.setInput('A1', '=new Date()');
    const result = sheet.calc();
    assert.true(result['A1'] instanceof Date);
  });

  QUnit.test('calc for invalid formula', assert => {
    sheet.setInput('A1', '=balabala');
    const result = sheet.calc();
    assert.true(result['A1'] instanceof Error);
  });

  QUnit.test('calc for formula unimplemented', assert => {
    sheet.setInput('A1', '=B2');
    const result = sheet.calc();
    assert.true(result['A1'] instanceof Error);
  });
});