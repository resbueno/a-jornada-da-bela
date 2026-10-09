"""Pilha de estados. Transicoes sao aplicadas ao fim do update, nunca no meio dele."""


class StateManager:
    def __init__(self, initial):
        self._stack = []
        self._pending = []
        self.change(initial)
        self._apply_pending()

    @property
    def current(self):
        return self._stack[-1] if self._stack else None

    # --- transicoes (adiadas para o fim do tick) -----------------------
    def change(self, state):
        """Substitui toda a pilha por `state` (ex.: Titulo -> Jogando)."""
        self._pending.append(("change", state))

    def push(self, state):
        """Empilha `state` sobre o atual (ex.: Jogando -> Pausa)."""
        self._pending.append(("push", state))

    def pop(self):
        """Remove o estado do topo, voltando ao de baixo (ex.: Pausa -> Jogando)."""
        self._pending.append(("pop", None))

    def _apply_pending(self):
        for op, state in self._pending:
            if op == "change":
                while self._stack:
                    self._stack.pop().exit()
                self._enter(state)
            elif op == "push":
                self._enter(state)
            elif op == "pop" and self._stack:
                self._stack.pop().exit()
        self._pending.clear()

    def _enter(self, state):
        state.manager = self
        self._stack.append(state)
        state.enter()

    # --- loop -----------------------------------------------------------
    def update(self, dt, inp):
        if self.current:
            self.current.update(dt, inp)
        self._apply_pending()

    def draw(self, canvas):
        start = len(self._stack) - 1
        while start > 0 and self._stack[start].overlay:
            start -= 1
        for state in self._stack[max(start, 0):]:
            state.draw(canvas)
