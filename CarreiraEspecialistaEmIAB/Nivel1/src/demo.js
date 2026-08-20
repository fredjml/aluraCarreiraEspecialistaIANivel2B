import { calcularNps, consultarPrazo, processarResposta } from './hermex.js';

const handoff = {
  P001: { cliente: 'Ana Souza', email_cliente: 'ana.souza@email.com' },
  P002: { cliente: 'Bruno Lima', email_cliente: 'bruno.lima@email.com' }
};

console.log('Consulta de prazo:', consultarPrazo('BA', 'expresso'));
console.log('Detrator:', processarResposta({ id_pedido: 'P002', nota_nps: 4, comentario: 'Entrega atrasou e a caixa veio amassada' }, handoff));
console.log('Promotor:', processarResposta({ id_pedido: 'P001', nota_nps: 9, comentario: 'Entrega perfeita' }, handoff));
console.log('NPS:', calcularNps([9, 10, 8, 6, 4]));
