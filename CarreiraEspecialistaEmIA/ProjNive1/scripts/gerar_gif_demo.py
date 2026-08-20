"""Gera um GIF leve e reproduzível da experiência do GeoAI Mentor."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


LARGURA, ALTURA = 1100, 680
FUNDO = "#F7F9FC"
AZUL = "#173B57"
VERDE = "#1B8A6B"
TEXTO = "#263238"
BORDA = "#D8E1E8"


def fonte(tamanho: int, negrito: bool = False) -> ImageFont.FreeTypeFont:
    nome = "arialbd.ttf" if negrito else "arial.ttf"
    return ImageFont.truetype(nome, tamanho)


def quebrar(draw: ImageDraw.ImageDraw, texto: str, largura: int, font) -> list[str]:
    palavras, linhas, atual = texto.split(), [], ""
    for palavra in palavras:
        candidata = f"{atual} {palavra}".strip()
        if draw.textlength(candidata, font=font) <= largura:
            atual = candidata
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def balao(draw, xy, texto, cor, largura=670):
    x, y = xy
    font = fonte(20)
    linhas = quebrar(draw, texto, largura - 42, font)
    altura = 28 * len(linhas) + 34
    draw.rounded_rectangle((x, y, x + largura, y + altura), 18, fill=cor)
    for indice, linha in enumerate(linhas):
        draw.text((x + 21, y + 16 + indice * 28), linha, font=font, fill=TEXTO)
    return y + altura + 16


def quadro(mensagens, digitando=False):
    imagem = Image.new("RGB", (LARGURA, ALTURA), FUNDO)
    draw = ImageDraw.Draw(imagem)
    draw.rectangle((0, 0, 280, ALTURA), fill=AZUL)
    draw.text((32, 42), "GeoAI Mentor", font=fonte(27, True), fill="white")
    draw.text((32, 94), "Memória por sessão", font=fonte(18), fill="#D8EEF5")
    draw.rounded_rectangle((32, 145, 248, 196), 12, fill=VERDE)
    draw.text((62, 160), "Nova conversa", font=fonte(18, True), fill="white")
    draw.text((32, 235), "OpenAI + LangChain", font=fonte(17), fill="#D8EEF5")
    draw.text((32, 265), "+ Streamlit", font=fonte(17), fill="#D8EEF5")

    draw.ellipse((326, 43, 348, 65), fill=VERDE)
    draw.text((365, 35), "GeoAI Mentor", font=fonte(31, True), fill=AZUL)
    draw.text(
        (324, 78),
        "Orientação para geocientistas em transição para Dados",
        font=fonte(17),
        fill="#607D8B",
    )
    y = 126
    for papel, texto in mensagens:
        x = 350 if papel == "assistant" else 390
        cor = "#E5F4EF" if papel == "assistant" else "#E8EEF8"
        y = balao(draw, (x, y), texto, cor)
    if digitando:
        draw.text((370, y + 4), "GeoAI Mentor está analisando...", font=fonte(17), fill=VERDE)
    draw.rounded_rectangle((324, 608, 1065, 657), 15, fill="white", outline=BORDA, width=2)
    draw.text((348, 623), "Digite sua pergunta para o GeoAI Mentor", font=fonte(18), fill="#8797A1")
    return imagem


def main() -> None:
    inicial = (
        "assistant",
        "Olá! Posso ajudar você a planejar sua transição de geociências para Ciência de Dados.",
    )
    pergunta1 = ("user", "Sou geofísico. Qual linguagem devo aprender primeiro?")
    resposta1 = ("assistant", "Comece por Python: ela une análise de dados, automação e aprendizado de máquina.")
    pergunta2 = ("user", "E qual projeto de portfólio posso criar usando essa linguagem?")
    resposta2 = ("assistant", "Em Python, crie uma análise de dados sísmicos com mapa, gráficos e conclusões técnicas.")
    frames = [
        quadro([inicial]),
        quadro([inicial, pergunta1], digitando=True),
        quadro([pergunta1, resposta1, pergunta2], digitando=True),
        quadro([resposta1, pergunta2, resposta2]),
    ]
    destino = Path(__file__).parents[1] / "assets" / "geoai-mentor-demo.gif"
    frames[0].save(
        destino,
        save_all=True,
        append_images=frames[1:],
        duration=[1400, 1200, 1200, 2600],
        loop=0,
        optimize=True,
    )


if __name__ == "__main__":
    main()
