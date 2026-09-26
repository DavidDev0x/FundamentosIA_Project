class Agente:
    """
    Classe que representa a identidade e a regra social de um agente no ambiente.
    """
    def __init__(self, nome, raio_social, peso_penalidade, cor_linha):
        self.nome = nome
        self.raio_social = raio_social
        self.peso_penalidade = peso_penalidade
        self.cor_linha = cor_linha
