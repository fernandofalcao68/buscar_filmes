from dataclasses import dataclass


@dataclass
class ConsultaFilme:
    id: int
    termo_pesquisado: str
    titulo: str
    ano: str
    diretor: str
    data_consulta: str

    def resumo(self) -> str:
        return (
            f"ID {self.id} | Termo: {self.termo_pesquisado} | "
            f"Titulo: {self.titulo} ({self.ano}) | Diretor: {self.diretor} | "
            f"Data: {self.data_consulta}"
        )
