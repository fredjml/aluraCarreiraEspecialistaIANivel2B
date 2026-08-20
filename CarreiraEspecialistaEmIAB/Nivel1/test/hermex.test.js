import test from 'node:test';
import assert from 'node:assert/strict';
import { calcularNps, classificarComentario, consultarPrazo, normalizarCategoria, processarResposta } from '../src/hermex.js';

const handoff = { P001: { cliente: 'Ana', email_cliente: 'ana@example.com' }, P002: { cliente: 'Bruno', email_cliente: 'bruno@example.com' } };

test('SLA é exato de 5 dias corridos em SP, BA e AM', () => {
  for (const [uf, regiao] of [['SP', 'Sudeste'], ['BA', 'Nordeste'], ['AM', 'Norte']]) {
    const resultado = consultarPrazo(uf, 'comum');
    assert.equal(resultado.regiao, regiao);
    assert.equal(resultado.prazoMinimo, 5);
    assert.equal(resultado.prazoMaximo, 5);
    assert.equal(resultado.unidade, 'dias corridos');
  }
});

test('fretes comum e expresso têm o mesmo SLA', () => assert.deepEqual(consultarPrazo('SP', 'comum').prazoMaximo, consultarPrazo('SP', 'expresso').prazoMaximo));
test('rejeita UF e frete inválidos', () => {
  assert.throws(() => consultarPrazo('XX'), /UF inválida/);
  assert.throws(() => consultarPrazo('SP', 'premium'), /Frete/);
});
test('classificação fechada cobre categorias e fallback', () => {
  assert.equal(classificarComentario('Entrega atrasou muito'), 'Atraso');
  assert.equal(classificarComentario('Produto com defeito'), 'Defeito');
  assert.equal(classificarComentario('Suporte não respondeu'), 'Atendimento');
  assert.equal(classificarComentario('Caixa amassada'), 'Embalagem');
  assert.equal(classificarComentario('Gostei da cor'), 'Outro');
  assert.equal(normalizarCategoria('qualquer explicação'), 'Outro');
});
test('nota 5 segue alerta e nota 6 segue agradecimento conforme regra < 6', () => {
  assert.equal(processarResposta({ id_pedido: 'P001', nota_nps: 5, comentario: 'atrasou' }, handoff).rota, 'alerta_pos_venda');
  assert.equal(processarResposta({ id_pedido: 'P001', nota_nps: 6, comentario: '' }, handoff).rota, 'agradecimento_cliente');
});
test('todo envio permanece aguardando aprovação humana', () => assert.equal(processarResposta({ id_pedido: 'P001', nota_nps: 10 }, handoff).status, 'aguardando_aprovacao_humana'));
test('pedido ausente no handoff é desviado para revisão manual', () => assert.equal(processarResposta({ id_pedido: 'P060', nota_nps: 2 }, handoff).status, 'revisao_manual'));
test('NPS analítico usa promotores >8 e detratores <7', () => assert.deepEqual(calcularNps([10, 9, 8, 6, 0]), { total: 5, promotores: 2, detratores: 2, nps: 0 }));
test('valida notas e campos obrigatórios', () => {
  assert.throws(() => calcularNps([11]), /0 a 10/);
  assert.throws(() => processarResposta({ nota_nps: 5 }, handoff), /id_pedido/);
});
