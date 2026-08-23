"""Interface Gradio opcional para o protótipo multiagente."""
from .multiagent_graph import build_graph


def respond(question: str) -> tuple[str, str]:
    result = build_graph().invoke({"mensagem": question})
    return result["classificacao"], result["resposta_final"]


def main() -> None:
    try:
        import gradio as gr
    except ImportError as error:
        raise SystemExit("Instale requirements.txt para habilitar a interface Gradio.") from error
    demo = gr.Interface(
        fn=respond,
        inputs=gr.Textbox(label="Pergunta"),
        outputs=[gr.Textbox(label="Intenção"), gr.Textbox(label="Resposta")],
        title="Bytebank AI - protótipo local",
    )
    demo.launch()


if __name__ == "__main__":
    main()
