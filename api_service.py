from typing import Dict

import requests


class OMDbService:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://www.omdbapi.com/"

    def buscar_filme_por_titulo(self, titulo: str) -> Dict[str, str]:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("Digite um titulo para pesquisar.")
        if not self.api_key:
            raise ValueError("Defina sua API key da OMDb no arquivo main.py.")

        try:
            resposta = requests.get(
                self.base_url,
                params={"apikey": self.api_key, "t": titulo},
                timeout=10,
            )
            resposta.raise_for_status()
        except requests.RequestException as exc:
            raise ConnectionError("Falha de conexao com a API OMDb.") from exc

        dados = resposta.json()
        if dados.get("Response") == "False":
            erro = dados.get("Error", "Filme nao encontrado.")
            raise ValueError(erro)

        return {
            "Title": dados.get("Title", "N/A"),
            "Year": dados.get("Year", "N/A"),
            "Director": dados.get("Director", "N/A"),
            "Actors": dados.get("Actors", "N/A"),
            "Plot": dados.get("Plot", "N/A"),
            "Poster": dados.get("Poster", "N/A"),
        }

    def baixar_poster(self, poster_url: str) -> bytes:
        if not poster_url or poster_url == "N/A":
            raise ValueError("Poster indisponivel.")

        try:
            resposta = requests.get(poster_url, timeout=10)
            resposta.raise_for_status()
        except requests.RequestException as exc:
            raise ConnectionError("Falha ao baixar o poster.") from exc

        return resposta.content
