class Via:
    """
    Camada de Domínio: Entidade que representa o espaço físico da rua.
    Contém regras de negócio sobre capacidade física, mas não sabe como salvar no banco
    nem como desenhar um gráfico.
    """
    def __init__(self, nome, capacidade_metros):
        self.nome = nome
        self.capacidade_metros = capacidade_metros
        self.fila_metros = 0
        self.demanda_futura_metros = 0 
