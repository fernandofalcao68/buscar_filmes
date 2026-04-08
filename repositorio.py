import sqlite3
from typing import List, Optional

from modelo import ConsultaFilme


class RepositorioConsultas:
    CAMPOS_ORDENACAO = {
        "id": "id",
        "termo_pesquisado": "termo_pesquisado",
        "titulo": "titulo",
        "ano": "ano",
        "diretor": "diretor",
        "data_consulta": "data_consulta",
    }

    def __init__(self, caminho_banco: str = "consultas_filmes.db") -> None:
        self._conexao = sqlite3.connect(caminho_banco)
        self._conexao.row_factory = sqlite3.Row
        self._criar_tabela()

    def _criar_tabela(self) -> None:
        self._conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                termo_pesquisado TEXT NOT NULL,
                titulo TEXT NOT NULL,
                ano TEXT NOT NULL,
                diretor TEXT NOT NULL,
                data_consulta TEXT NOT NULL
            )
            """
        )
        self._conexao.commit()

    def create(
        self,
        termo_pesquisado: str,
        titulo: str,
        ano: str,
        diretor: str,
        data_consulta: str,
    ) -> ConsultaFilme:
        cursor = self._conexao.execute(
            """
            INSERT INTO consultas (termo_pesquisado, titulo, ano, diretor, data_consulta)
            VALUES (?, ?, ?, ?, ?)
            """,
            (termo_pesquisado, titulo, ano, diretor, data_consulta),
        )
        self._conexao.commit()
        return ConsultaFilme(
            id=cursor.lastrowid,
            termo_pesquisado=termo_pesquisado,
            titulo=titulo,
            ano=ano,
            diretor=diretor,
            data_consulta=data_consulta,
        )

    def read_all(self, order_by: str = "id", descending: bool = False) -> List[ConsultaFilme]:
        campo = self.CAMPOS_ORDENACAO.get(order_by, "id")
        direcao = "DESC" if descending else "ASC"
        cursor = self._conexao.execute(
            f"""
            SELECT id, termo_pesquisado, titulo, ano, diretor, data_consulta
            FROM consultas
            ORDER BY {campo} {direcao}
            """
        )
        return [self._linha_para_objeto(linha) for linha in cursor.fetchall()]

    def read_by_id(self, consulta_id: int) -> Optional[ConsultaFilme]:
        cursor = self._conexao.execute(
            """
            SELECT id, termo_pesquisado, titulo, ano, diretor, data_consulta
            FROM consultas
            WHERE id = ?
            """,
            (consulta_id,),
        )
        linha = cursor.fetchone()
        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    def update(
        self,
        consulta_id: int,
        termo_pesquisado: str,
        titulo: str,
        ano: str,
        diretor: str,
        data_consulta: str,
    ) -> bool:
        cursor = self._conexao.execute(
            """
            UPDATE consultas
            SET termo_pesquisado = ?, titulo = ?, ano = ?, diretor = ?, data_consulta = ?
            WHERE id = ?
            """,
            (termo_pesquisado, titulo, ano, diretor, data_consulta, consulta_id),
        )
        self._conexao.commit()
        return cursor.rowcount > 0

    def delete(self, consulta_id: int) -> bool:
        cursor = self._conexao.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))
        self._conexao.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self._conexao.close()

    @staticmethod
    def _linha_para_objeto(linha: sqlite3.Row) -> ConsultaFilme:
        return ConsultaFilme(
            id=int(linha["id"]),
            termo_pesquisado=str(linha["termo_pesquisado"]),
            titulo=str(linha["titulo"]),
            ano=str(linha["ano"]),
            diretor=str(linha["diretor"]),
            data_consulta=str(linha["data_consulta"]),
        )
