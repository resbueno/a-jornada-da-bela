"""Base dos estados do jogo."""


class State:
    # True: o estado abaixo na pilha continua sendo desenhado (pausa, dialogo, inventario)
    overlay = False

    def __init__(self):
        self.manager = None  # preenchido pelo StateManager

    def enter(self):
        """Chamado quando o estado entra na pilha."""

    def exit(self):
        """Chamado quando o estado sai da pilha."""

    def update(self, dt, inp):
        """Um passo de logica (dt fixo). So o estado do topo recebe update."""

    def draw(self, canvas):
        """Desenha no canvas logico 320x180."""
