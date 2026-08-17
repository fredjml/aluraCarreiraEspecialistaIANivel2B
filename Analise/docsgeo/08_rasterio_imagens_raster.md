---
titulo: Dados raster e GeoTIFF com Rasterio
origem: Projeto Rasterio
url: https://rasterio.readthedocs.io/en/stable/quickstart.html
licenca: BSD-3-Clause
aprovado_em: 2026-08-17
revisar_em: 2026-11-17
confidencialidade: publico
---

# Dados raster e GeoTIFF com Rasterio

Rasterio fornece uma API Python para leitura e escrita de dados raster, incluindo GeoTIFF. Um dataset apresenta bandas, largura, altura, tipo de dado, limites espaciais, CRS, transformação afim e valor de ausência.

Os pixels de um raster georreferenciado correspondem a posições no espaço. Projetos devem conferir CRS, resolução, extensão, transformação, bandas, tipo numérico e `nodata` antes de calcular estatísticas ou combinar imagens. Rasterio pode ler bandas como arrays NumPy, consultar pixels por coordenadas e salvar novos rasters com metadados explícitos.

Tópicos recuperáveis: Rasterio, raster, GeoTIFF, banda, pixel, CRS, transformação afim, resolução, nodata, imagem de satélite.

Fonte oficial: [Rasterio Python Quickstart](https://rasterio.readthedocs.io/en/stable/quickstart.html).
