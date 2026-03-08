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

  const sheet = new Spreadsheet(4, 4);

  hooks.before(() => {
    sheet.reset(4, 4);
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

  QUnit.test('serialize/deserialize', assert => {
    sheet.setInput('A1', '123');
    sheet.setInput('B2', 'abc');
    const value = sheet.serialize();
    
    const target = new Spreadsheet(); 
    target.deserialize(value);
    assert.equal('123', target.input('A1'));
    assert.equal('abc', target.input('B2'));
  });
});

QUnit.module('Spreadsheet with formula', hooks => {

  const sheet = new Spreadsheet(6, 6);

  hooks.before(() => {
    sheet.reset(6, 6);
  });

  QUnit.test('transform formula', assert => {
    const formulas = {
      '=A1': '=this.A1',
      '=A1+C1': '=this.A1+this.C1',
    }
    for (let origin in formulas) {
      const transformed = transformFormula(origin);
      assert.equal(formulas[origin], transformed);
    }
  });

  QUnit.test('calc with single formula', assert => {
    sheet.setInput('A1', '1874');
    sheet.setInput('C1', '2046');
    sheet.setInput('E1', '=A1+C1');
    const result = sheet.calc();
    assert.equal(3920, result['E1']);
  });

  QUnit.test('calc with multiple formula', assert => {
    sheet.setInput('A1', '12');
    sheet.setInput('B2', '34');
    sheet.setInput('C1', '=A1+B2');
    sheet.setInput('D2', '=56+C1');
    const result = sheet.calc();
    assert.equal(12+34+56, result['D2']);
  });

  QUnit.test('calc with empty value', assert => {
    sheet.setInput('A1', '1874');
    sheet.setInput('C1', '2046');
    sheet.setInput('E1', '=A1+B1');
    const result = sheet.calc();
    assert.equal(1874, result['E1']);
  });
});