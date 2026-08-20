---
titulo: Processamento sismológico com ObsPy
origem: ObsPy Development Team
url: https://docs.obspy.org/master/packages/obspy.core.html
licenca: LGPL-3.0
aprovado_em: 2026-08-17
revisar_em: 2026-11-17
confidencialidade: publico
---

# Processamento sismológico com ObsPy

ObsPy fornece estruturas e rotinas Python para sismologia. A função `read` importa formatos de formas de onda como SAC e MiniSEED para um objeto `Stream`, que contém objetos `Trace`. Cada traço mantém os valores numéricos em um array NumPy e os metadados em `stats`.

Projetos podem envolver leitura, inspeção de metadados, seleção temporal, filtragem, remoção de tendência, visualização, comparação de estações e análise de eventos. Filtros e transformações devem registrar parâmetros, frequência de amostragem e efeitos introduzidos no sinal.

Tópicos recuperáveis: ObsPy, sismologia, sismograma, waveform, Stream, Trace, SAC, MiniSEED, filtro, estação, evento sísmico.

Fonte oficial: [ObsPy Core](https://docs.obspy.org/master/packages/obspy.core.html).
