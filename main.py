import tkinter as tk
from pathlib import Path

from api_service import OMDbService
from interface import InterfaceFilmes
from repositorio import RepositorioConsultas


def main() -> None:
    # chave da OMDb API
    api_key = "d7ad9e07"

    caminho_banco = Path(__file__).resolve().parent / "consultas_filmes.db"
    repositorio = RepositorioConsultas(caminho_banco=str(caminho_banco))
    api_service = OMDbService(api_key=api_key)

    root = tk.Tk()
    interface = InterfaceFilmes(root=root, api_service=api_service, repositorio=repositorio)
    root.protocol("WM_DELETE_WINDOW", interface.fechar)
    root.mainloop()


if __name__ == "__main__":
    main()
