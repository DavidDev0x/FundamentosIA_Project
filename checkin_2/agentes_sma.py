from dataclasses import dataclass


@dataclass
class MensagemFiscal:
    cruzamento: str
    minuto: str
    volume_veiculos: int
    velocidade_media: float
    veiculos_risco: int


class AgenteFiscal:
    """Representa um ponto local de fiscalização/monitoramento."""

    def __init__(self, cruzamento):
        self.cruzamento = cruzamento

    def criar_mensagem(self, linha):
        return MensagemFiscal(
            cruzamento=self.cruzamento,
            minuto=str(linha["minuto"]),
            volume_veiculos=int(linha["volume_veiculos"]),
            velocidade_media=float(linha["velocidade_media"]),
            veiculos_risco=int(linha.get("veiculos_risco", 0)),
        )


class AgenteCoordenador:
    """Recebe mensagens dos fiscais e prioriza o ponto com maior pressão."""

    def __init__(self, peso_volume=1.0, peso_risco=2.0):
        self.mensagens = []
        self.peso_volume = peso_volume
        self.peso_risco = peso_risco

    def receber(self, mensagem):
        self.mensagens.append(mensagem)

    def calcular_pressao(self, mensagem):
        """
        Heurística simples de prioridade.
        O risco recebe peso maior para que a decisão não dependa apenas do fluxo.
        """
        return (
            mensagem.volume_veiculos * self.peso_volume
            + mensagem.veiculos_risco * self.peso_risco
        )

    def ranking_prioridade(self):
        return sorted(
            self.mensagens,
            key=lambda msg: (
                self.calcular_pressao(msg),
                msg.volume_veiculos,
                msg.veiculos_risco,
            ),
            reverse=True,
        )

    def priorizar_cruzamento(self):
        ranking = self.ranking_prioridade()
        return ranking[0].cruzamento if ranking else None
