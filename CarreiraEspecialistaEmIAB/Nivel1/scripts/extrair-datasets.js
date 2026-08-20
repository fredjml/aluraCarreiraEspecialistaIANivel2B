import { readFile, writeFile, mkdir } from 'node:fs/promises';

const fonte = await readFile(new URL('../projNivel1EspIAB.txt', import.meta.url), 'utf8');

function extrair(cabecalho, proximoMarcador) {
  const inicio = fonte.indexOf(cabecalho);
  if (inicio < 0) throw new Error(`Cabeçalho não encontrado: ${cabecalho}`);
  const fim = fonte.indexOf(proximoMarcador, inicio);
  const bloco = fonte.slice(inicio, fim < 0 ? undefined : fim).trim();
  return `${bloco}\n`;
}

const pesquisa = extrair('id_pedido,cliente,email_cliente,estado,data_pedido,data_envio,data_recebimento,nota_nps,comentario', 'handoff_vendas_posvenda.csv');
const handoff = extrair('id_pedido,cliente,email_cliente,telefone,valor_pedido,data_pedido,estado,status_pagamento,responsavel_posvenda,observacoes', '1ª Etapa:');
const linhasPesquisa = pesquisa.trim().split(/\r?\n/);
const linhasHandoff = handoff.trim().split(/\r?\n/);
if (linhasPesquisa.length !== 61) throw new Error(`Pesquisa deveria ter 60 registros; encontrados ${linhasPesquisa.length - 1}`);
if (linhasHandoff.length !== 31) throw new Error(`Handoff deveria ter 30 registros; encontrados ${linhasHandoff.length - 1}`);

await mkdir(new URL('../dados/', import.meta.url), { recursive: true });
await writeFile(new URL('../dados/pesquisa_satisfacao.csv', import.meta.url), pesquisa, 'utf8');
await writeFile(new URL('../dados/handoff_vendas_posvenda.csv', import.meta.url), handoff, 'utf8');
console.log(`Dados validados: ${linhasPesquisa.length - 1} respostas NPS e ${linhasHandoff.length - 1} registros de handoff.`);
