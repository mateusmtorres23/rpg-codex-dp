from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from InquirerPy import inquirer
from rich import print as rich_print

from gameplay.combate import combate
from models.inimigo import Inimigo
from models.personagem import Personagem
from utills import digitar


class EtapaNarrativa(ABC):
    @abstractmethod
    def executar(self, personagem: Personagem) -> str | None:
        """Executa a etapa e retorna o destino da próxima cena, ou None para continuar."""


@dataclass
class Narracao(EtapaNarrativa):
    texto: str
    com_rich: bool = False

    def executar(self, personagem: Personagem) -> str | None:
        mensagem = self.texto.format(nick=personagem.nick)
        if self.com_rich:
            rich_print(mensagem)
        else:
            digitar(mensagem)
        return None


@dataclass
class Acao(EtapaNarrativa):
    funcao: Callable[[Personagem], None]

    def executar(self, personagem: Personagem) -> str | None:
        self.funcao(personagem)
        return None


@dataclass
class IrPara(EtapaNarrativa):
    destino: str

    def executar(self, personagem: Personagem) -> str | None:
        return self.destino


@dataclass
class Combate(EtapaNarrativa):
    inimigo: Inimigo
    ao_perder: EtapaNarrativa

    def executar(self, personagem: Personagem) -> str | None:
        vencedor = combate(personagem, self.inimigo)
        if vencedor == personagem:
            return None
        return self.ao_perder.executar(personagem)


@dataclass
class Sequencia(EtapaNarrativa):
    etapas: list[EtapaNarrativa]

    def executar(self, personagem: Personagem) -> str | None:
        for etapa in self.etapas:
            destino = etapa.executar(personagem)
            if destino is not None:
                return destino

        return None


@dataclass
class Escolha(EtapaNarrativa):
    mensagem: str
    opcoes: dict[str, EtapaNarrativa]

    def executar(self, personagem: Personagem) -> str | None:
        while True:
            selecionada = inquirer.select(
                message=self.mensagem,
                choices=list(self.opcoes.keys()),
            ).execute()

            etapa = self.opcoes[selecionada]
            destino = etapa.executar(personagem)

            if destino is not None:
                return destino


@dataclass
class ExecutorNarrativa:
    cenas: dict[str, EtapaNarrativa]

    def executar(self, cena_inicial: str, personagem: Personagem) -> None:
        destino: str | None = cena_inicial

        while destino is not None:
            if destino not in self.cenas:
                raise ValueError(f"Cena '{destino}' não encontrada na narrativa.")

            cena = self.cenas[destino]
            destino = cena.executar(personagem)
