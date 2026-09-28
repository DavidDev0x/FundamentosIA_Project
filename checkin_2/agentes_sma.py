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
    """Recebe mensagens locais e decide onde há maior pressão de tráfego."""

    def __init__(self):
        self.mensagens = []

    def receber(self, mensagem):
        self.mensagens.append(mensagem)

    def priorizar_cruzamento(self):
        if not self.mensagens:
            return None
        return max(
            self.mensagens,
            key=lambda msg: (msg.volume_veiculos, msg.veiculos_risco),
        ).cruzamento
