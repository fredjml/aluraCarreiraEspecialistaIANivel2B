const UF_REGIAO = Object.freeze({
  AC: 'Norte', AL: 'Nordeste', AP: 'Norte', AM: 'Norte', BA: 'Nordeste', CE: 'Nordeste', DF: 'Centro-Oeste', ES: 'Sudeste',
  GO: 'Centro-Oeste', MA: 'Nordeste', MT: 'Centro-Oeste', MS: 'Centro-Oeste', MG: 'Sudeste', PA: 'Norte', PB: 'Nordeste',
  PR: 'Sul', PE: 'Nordeste', PI: 'Nordeste', RJ: 'Sudeste', RN: 'Nordeste', RS: 'Sul', RO: 'Norte', RR: 'Norte',
  SC: 'Sul', SP: 'Sudeste', SE: 'Nordeste', TO: 'Norte'
});

export const CATEGORIAS = Object.freeze(['Atraso', 'Defeito', 'Atendimento', 'Embalagem', 'Outro']);

export function consultarPrazo(estado, frete = 'comum') {
  const uf = String(estado ?? '').trim().toUpperCase();
  const modalidade = String(frete ?? '').trim().toLowerCase();
  if (!UF_REGIAO[uf]) throw new Error('UF inválida ou não informada');
  if (!['comum', 'expresso'].includes(modalidade)) throw new Error('Frete deve ser comum ou expresso');
  return {
    estado: uf,
    regiao: UF_REGIAO[uf],
    frete: modalidade,
    prazoMinimo: 5,
    prazoMaximo: 5,
    unidade: 'dias corridos',
    observacoes: 'Prazo estimado oficial; sujeito à confirmação operacional e aprovação humana.'
  };
}

export function classificarComentario(comentario) {
  const texto = String(comentario ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  if (/atras|demor|prazo|extravi|rastre/.test(texto)) return 'Atraso';
  if (/defeit|quebrad|avari|produto errado/.test(texto)) return 'Defeito';
  if (/atend|suporte|resposta|inform/.test(texto)) return 'Atendimento';
  if (/embalag|caixa|amassad/.test(texto)) return 'Embalagem';
  return 'Outro';
}

export function normalizarCategoria(valor) {
  const candidata = String(valor ?? '').trim();
  const encontrada = CATEGORIAS.find((item) => item.toLowerCase() === candidata.toLowerCase());
  return encontrada ?? 'Outro';
}

export function calcularNps(notas) {
  if (!Array.isArray(notas) || notas.length === 0) throw new Error('Informe ao menos uma nota');
  const valores = notas.map(Number);
  if (valores.some((nota) => !Number.isInteger(nota) || nota < 0 || nota > 10)) throw new Error('Notas devem ser inteiros de 0 a 10');
  const promotores = valores.filter((nota) => nota > 8).length;
  const detratores = valores.filter((nota) => nota < 7).length;
  return { total: valores.length, promotores, detratores, nps: ((promotores - detratores) / valores.length) * 100 };
}

export function processarResposta(resposta, handoff, agora = new Date()) {
  const nota = Number(resposta?.nota_nps);
  if (!resposta?.id_pedido) throw new Error('id_pedido obrigatório');
  if (!Number.isInteger(nota) || nota < 0 || nota > 10) throw new Error('nota_nps deve ser inteiro de 0 a 10');
  const cliente = handoff?.[resposta.id_pedido];
  if (!cliente?.cliente || !cliente?.email_cliente) {
    return { status: 'revisao_manual', motivo: 'Pedido sem correspondência completa no handoff', id_pedido: resposta.id_pedido };
  }
  const detratorOperacional = nota < 6;
  const base = {
    status: 'aguardando_aprovacao_humana',
    id_pedido: resposta.id_pedido,
    cliente: cliente.cliente,
    email_cliente: cliente.email_cliente,
    nota_nps: nota,
    comentario: String(resposta.comentario ?? ''),
    criado_em: agora.toISOString(),
    expira_em: new Date(agora.getTime() + 2 * 86400000).toISOString(),
    excluir_ate: new Date(agora.getTime() + 7 * 86400000).toISOString()
  };
  if (detratorOperacional) {
    return { ...base, rota: 'alerta_pos_venda', destinatario: 'fredbrhermex@gmail.com', categoria: classificarComentario(base.comentario) };
  }
  return { ...base, rota: 'agradecimento_cliente', destinatario: cliente.email_cliente };
}
