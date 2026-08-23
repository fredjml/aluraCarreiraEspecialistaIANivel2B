"""Interface Gradio opcional para o protótipo multiagente."""
import argparse

from .multiagent_graph import build_graph


def respond(question: str) -> tuple[str, str]:
    result = build_graph().invoke({"mensagem": question})
    return result["classificacao"], result["resposta_final"]


def create_demo():
    try:
        import gradio as gr
    except ImportError as error:
        raise SystemExit("Instale requirements.txt para habilitar a interface Gradio.") from error
    return gr.Interface(
        fn=respond,
        inputs=gr.Textbox(label="Pergunta"),
        outputs=[gr.Textbox(label="Intenção"), gr.Textbox(label="Resposta")],
        title="Bytebank AI - protótipo local",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    create_demo().launch(server_name="127.0.0.1", server_port=args.port)


if __name__ == "__main__":
    main()
