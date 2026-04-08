from datetime import datetime
from io import BytesIO
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from PIL import Image, ImageTk, UnidentifiedImageError

from api_service import OMDbService
from repositorio import RepositorioConsultas


class InterfaceFilmes:
    POSTER_LARGURA = 250
    POSTER_ALTURA = 320
    COR_DESTAQUE = "#c1121f"
    COR_DESTAQUE_HOVER = "#a30f1a"

    CAMPOS_ORDENACAO = {
        "ID": "id",
        "Termo": "termo_pesquisado",
        "Titulo": "titulo",
        "Ano": "ano",
        "Diretor": "diretor",
        "Data": "data_consulta",
    }

    def __init__(self, root: tk.Tk, api_service: OMDbService, repositorio: RepositorioConsultas) -> None:
        self.root = root
        self.api_service = api_service
        self.repositorio = repositorio

        self.filme_atual = None
        self.termo_atual = ""
        self.poster_imagem = None

        self._configurar_janela()
        self._criar_widgets()
        self.recarregar_consultas()

    def _configurar_janela(self) -> None:
        self.root.title("SearchFlix")
        self.root.geometry("1050x760")
        self.root.minsize(960, 700)

    def _criar_botao(self, parent, texto, comando, largura):
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            width=largura,
            bg=self.COR_DESTAQUE,
            fg="white",
            activebackground=self.COR_DESTAQUE_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
        )

    def _criar_widgets(self) -> None:
        frame_principal = tk.Frame(self.root, padx=12, pady=12)
        frame_principal.pack(fill="both", expand=True)

        tk.Label(frame_principal, text="SearchFlix", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 10))

        frame_busca = tk.LabelFrame(frame_principal, text="Busca", padx=8, pady=8)
        frame_busca.pack(fill="x", pady=(0, 10))

        tk.Label(frame_busca, text="Titulo:").pack(side="left")
        self.entry_busca = tk.Entry(frame_busca, width=55)
        self.entry_busca.pack(side="left", padx=8)
        self.entry_busca.bind("<Return>", lambda _: self.buscar_filme())

        self.btn_buscar = self._criar_botao(frame_busca, "Buscar", self.buscar_filme, 12)
        self.btn_buscar.pack(side="left")

        frame_resultado = tk.Frame(frame_principal)
        frame_resultado.pack(fill="x", pady=(0, 10))

        frame_texto = tk.LabelFrame(frame_resultado, text="Detalhes do Filme", padx=8, pady=8)
        frame_texto.pack(side="left", fill="both", expand=True)

        self.txt_resultado = tk.Text(frame_texto, height=10, width=72, wrap="word")
        self.txt_resultado.pack(fill="both", expand=True)
        self._atualizar_texto_resultado("Nenhuma consulta realizada.")

        frame_poster = tk.LabelFrame(frame_resultado, text="Poster", padx=8, pady=8)
        frame_poster.pack(side="left", padx=(10, 0), fill="y")

        self.frame_poster = tk.Frame(
            frame_poster,
            width=self.POSTER_LARGURA,
            height=self.POSTER_ALTURA,
            relief="groove",
            bd=1,
        )
        self.frame_poster.pack()
        self.frame_poster.pack_propagate(False)

        self.lbl_poster = tk.Label(self.frame_poster, text="Poster indisponivel", justify="center")
        self.lbl_poster.pack(fill="both", expand=True)

        frame_acoes = tk.LabelFrame(frame_principal, text="Acoes", padx=8, pady=8)
        frame_acoes.pack(fill="x", pady=(0, 10))

        self._criar_botao(frame_acoes, "Salvar consulta", self.salvar_consulta, 15).pack(side="left", padx=3)
        self._criar_botao(frame_acoes, "Recarregar consultas", self.recarregar_consultas, 18).pack(side="left", padx=3)
        self._criar_botao(frame_acoes, "Carregar consulta", self.carregar_consulta, 15).pack(side="left", padx=3)
        self._criar_botao(frame_acoes, "Editar consulta", self.editar_consulta, 13).pack(side="left", padx=3)
        self._criar_botao(frame_acoes, "Excluir consulta", self.excluir_consulta, 13).pack(side="left", padx=3)

        tk.Label(frame_acoes, text="  Ordenar por:").pack(side="left", padx=(10, 0))

        self.combo_ordenacao = ttk.Combobox(
            frame_acoes,
            values=list(self.CAMPOS_ORDENACAO.keys()),
            state="readonly",
            width=12,
        )
        self.combo_ordenacao.pack(side="left", padx=5)
        self.combo_ordenacao.set("ID")

        self.var_decrescente = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_acoes, text="Decrescente", variable=self.var_decrescente).pack(side="left", padx=4)
        self._criar_botao(frame_acoes, "Aplicar", self.recarregar_consultas, 8).pack(side="left", padx=4)

        frame_lista = tk.LabelFrame(frame_principal, text="Consultas Registradas", padx=8, pady=8)
        frame_lista.pack(fill="both", expand=True)

        colunas = ("id", "termo", "titulo", "ano", "diretor", "data")
        self.tree_consultas = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=12)
        self.tree_consultas.heading("id", text="ID")
        self.tree_consultas.heading("termo", text="Termo")
        self.tree_consultas.heading("titulo", text="Titulo")
        self.tree_consultas.heading("ano", text="Ano")
        self.tree_consultas.heading("diretor", text="Diretor")
        self.tree_consultas.heading("data", text="Data da consulta")

        self.tree_consultas.column("id", width=50, anchor="center")
        self.tree_consultas.column("termo", width=150)
        self.tree_consultas.column("titulo", width=230)
        self.tree_consultas.column("ano", width=80, anchor="center")
        self.tree_consultas.column("diretor", width=200)
        self.tree_consultas.column("data", width=170, anchor="center")
        self.tree_consultas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_consultas.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_consultas.configure(yscrollcommand=scrollbar.set)

        self.lbl_status = tk.Label(frame_principal, text="Pronto.", anchor="w")
        self.lbl_status.pack(fill="x", pady=(8, 0))

    def _set_status(self, mensagem: str) -> None:
        self.lbl_status.config(text=mensagem)

    def _set_busca_habilitada(self, habilitado: bool) -> None:
        self.btn_buscar.config(state="normal" if habilitado else "disabled")

    def _atualizar_texto_resultado(self, texto: str) -> None:
        self.txt_resultado.config(state="normal")
        self.txt_resultado.delete("1.0", tk.END)
        self.txt_resultado.insert(tk.END, texto)
        self.txt_resultado.config(state="disabled")

    def _limpar_poster(self, mensagem: str = "Poster indisponivel") -> None:
        self.poster_imagem = None
        self.lbl_poster.config(image="", text=mensagem)

    def _data_atual(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def buscar_filme(self) -> None:
        termo = self.entry_busca.get().strip()
        if not termo:
            messagebox.showwarning("Aviso", "Digite um titulo para pesquisar.")
            return
        self._iniciar_busca(termo, "Buscando filme na API...")

    def _iniciar_busca(self, termo: str, status: str) -> None:
        self._set_busca_habilitada(False)
        self._set_status(status)
        self._limpar_poster("Carregando...")
        threading.Thread(target=self._buscar_filme_background, args=(termo,), daemon=True).start()

    def _buscar_filme_background(self, termo: str) -> None:
        try:
            filme = self.api_service.buscar_filme_por_titulo(termo)
            self.root.after(0, lambda: self._on_busca_sucesso(termo, filme))
        except (ValueError, ConnectionError) as erro:
            self.root.after(0, lambda: self._on_busca_erro(str(erro)))

    def _on_busca_sucesso(self, termo: str, filme: dict) -> None:
        self._set_busca_habilitada(True)
        self.filme_atual = filme
        self.termo_atual = termo

        texto = (
            f"Titulo: {filme['Title']}\n"
            f"Ano: {filme['Year']}\n"
            f"Diretor: {filme['Director']}\n"
            f"Atores: {filme['Actors']}\n\n"
            f"Sinopse: {filme['Plot']}\n\n"
            f"Poster URL: {filme['Poster']}"
        )
        self._atualizar_texto_resultado(texto)
        self._set_status("Filme encontrado com sucesso.")
        self._carregar_poster_async(filme.get("Poster", "N/A"))

    def _on_busca_erro(self, erro: str) -> None:
        self._set_busca_habilitada(True)
        self._set_status("Falha na busca.")
        self._limpar_poster("Poster indisponivel")
        messagebox.showerror("Erro na busca", erro)

    def _carregar_poster_async(self, poster_url: str) -> None:
        if not poster_url or poster_url == "N/A":
            self._limpar_poster("Poster indisponivel")
            return
        threading.Thread(target=self._baixar_poster_background, args=(poster_url,), daemon=True).start()

    def _baixar_poster_background(self, poster_url: str) -> None:
        try:
            conteudo = self.api_service.baixar_poster(poster_url)
            self.root.after(0, lambda: self._renderizar_poster(conteudo))
        except (ValueError, ConnectionError):
            self.root.after(0, lambda: self._limpar_poster("Poster indisponivel"))

    def _renderizar_poster(self, conteudo: bytes) -> None:
        try:
            imagem = Image.open(BytesIO(conteudo))
            largura, altura = imagem.size
            escala = min(self.POSTER_LARGURA / largura, self.POSTER_ALTURA / altura)
            nova_largura = max(1, int(largura * escala))
            nova_altura = max(1, int(altura * escala))
            imagem = imagem.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
            self.poster_imagem = ImageTk.PhotoImage(imagem)
            self.lbl_poster.config(image=self.poster_imagem, text="")
        except (UnidentifiedImageError, OSError):
            self._limpar_poster("Poster invalido")

    def salvar_consulta(self) -> None:
        if self.filme_atual is None:
            messagebox.showwarning("Aviso", "Pesquise um filme antes de salvar.")
            return

        self.repositorio.create(
            termo_pesquisado=self.termo_atual,
            titulo=self.filme_atual["Title"],
            ano=self.filme_atual["Year"],
            diretor=self.filme_atual["Director"],
            data_consulta=self._data_atual(),
        )
        self.recarregar_consultas()
        self._set_status("Consulta salva com sucesso.")
        messagebox.showinfo("Sucesso", "Consulta salva com sucesso.")

    def recarregar_consultas(self) -> None:
        self.tree_consultas.delete(*self.tree_consultas.get_children())
        order_by = self.CAMPOS_ORDENACAO.get(self.combo_ordenacao.get(), "id")
        consultas = self.repositorio.read_all(order_by=order_by, descending=self.var_decrescente.get())

        for consulta in consultas:
            self.tree_consultas.insert(
                "",
                tk.END,
                values=(
                    consulta.id,
                    consulta.termo_pesquisado,
                    consulta.titulo,
                    consulta.ano,
                    consulta.diretor,
                    consulta.data_consulta,
                ),
            )

        self._set_status(f"{len(consultas)} consulta(s) listada(s).")

    def carregar_consulta(self) -> None:
        consulta_id = self._obter_id_selecionado()
        if consulta_id is None:
            messagebox.showwarning("Aviso", "Selecione uma consulta para carregar.")
            return

        consulta = self.repositorio.read_by_id(consulta_id)
        if consulta is None:
            messagebox.showerror("Erro", "Consulta nao encontrada.")
            return

        termo = consulta.titulo.strip() or consulta.termo_pesquisado.strip()
        if not termo:
            messagebox.showerror("Erro", "Consulta sem titulo para busca.")
            return

        self.entry_busca.delete(0, tk.END)
        self.entry_busca.insert(0, termo)
        self._iniciar_busca(termo, "Carregando detalhes da consulta...")

    def _obter_id_selecionado(self):
        selecionados = self.tree_consultas.selection()
        if not selecionados:
            return None
        valores = self.tree_consultas.item(selecionados[0], "values")
        if not valores:
            return None
        return int(valores[0])

    def editar_consulta(self) -> None:
        consulta_id = self._obter_id_selecionado()
        if consulta_id is None:
            messagebox.showwarning("Aviso", "Selecione uma consulta para editar.")
            return

        consulta = self.repositorio.read_by_id(consulta_id)
        if consulta is None:
            messagebox.showerror("Erro", "Consulta nao encontrada.")
            return

        novo_termo = simpledialog.askstring("Editar termo", "Novo termo pesquisado:", initialvalue=consulta.termo_pesquisado, parent=self.root)
        if novo_termo is None:
            return

        novo_titulo = simpledialog.askstring("Editar titulo", "Novo titulo:", initialvalue=consulta.titulo, parent=self.root)
        if novo_titulo is None:
            return

        novo_ano = simpledialog.askstring("Editar ano", "Novo ano:", initialvalue=consulta.ano, parent=self.root)
        if novo_ano is None:
            return

        novo_diretor = simpledialog.askstring("Editar diretor", "Novo diretor:", initialvalue=consulta.diretor, parent=self.root)
        if novo_diretor is None:
            return

        if not novo_termo.strip() or not novo_titulo.strip():
            messagebox.showwarning("Aviso", "Termo e titulo nao podem ficar vazios.")
            return

        atualizado = self.repositorio.update(
            consulta_id=consulta_id,
            termo_pesquisado=novo_termo.strip(),
            titulo=novo_titulo.strip(),
            ano=novo_ano.strip() if novo_ano.strip() else "N/A",
            diretor=novo_diretor.strip() if novo_diretor.strip() else "N/A",
            data_consulta=self._data_atual(),
        )

        if atualizado:
            self.recarregar_consultas()
            self._set_status("Consulta atualizada com sucesso.")
            messagebox.showinfo("Sucesso", "Consulta atualizada com sucesso.")
        else:
            messagebox.showerror("Erro", "Nao foi possivel atualizar a consulta.")

    def excluir_consulta(self) -> None:
        consulta_id = self._obter_id_selecionado()
        if consulta_id is None:
            messagebox.showwarning("Aviso", "Selecione uma consulta para excluir.")
            return

        if not messagebox.askyesno("Confirmacao", "Deseja excluir a consulta selecionada?"):
            return

        excluido = self.repositorio.delete(consulta_id)
        if excluido:
            self.recarregar_consultas()
            self._set_status("Consulta excluida com sucesso.")
            messagebox.showinfo("Sucesso", "Consulta excluida com sucesso.")
        else:
            messagebox.showerror("Erro", "Nao foi possivel excluir a consulta.")

    def fechar(self) -> None:
        self.repositorio.close()
        self.root.destroy()