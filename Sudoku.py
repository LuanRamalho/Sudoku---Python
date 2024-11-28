import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo de Sudoku")
        
        # Variáveis do jogo
        self.difficulty = "fácil"
        self.board = []
        self.solution = []
        self.errors = 0
        self.start_time = 0
        self.game_over = False

        # Caminho do arquivo de recordes
        self.score_file = "sudoku_scores.json"
        self.scores = self.load_scores()

        # Criação da tela inicial
        self.create_difficulty_screen()

    def create_difficulty_screen(self):
        """Cria a tela inicial com os botões de dificuldade"""
        self.difficulty_screen = tk.Frame(self.root)
        self.difficulty_screen.pack(padx=20, pady=20)

        tk.Label(self.difficulty_screen, text="Escolha a Dificuldade", font=("Arial", 16)).pack(pady=10)
        
        difficulties = ["Muito Fácil", "Fácil", "Médio", "Difícil", "Muito Difícil"]
        for level in difficulties:
            tk.Button(self.difficulty_screen, text=level, font=("Arial", 14), 
                      command=lambda l=level: self.start_game(l)).pack(pady=5)

        # Botão do ScoreBoard
        tk.Button(self.difficulty_screen, text="ScoreBoard", font=("Arial", 14),
                  command=self.show_scoreboard).pack(pady=5)

    def start_game(self, level):
        """Inicia o jogo com o nível selecionado"""
        self.difficulty = level.lower()
        self.difficulty_screen.destroy()  # Destrói a tela de seleção de dificuldade
        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        """Cria os widgets do jogo de Sudoku"""
        # Botões e rótulos de controle
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.timer_label = tk.Label(control_frame, text="Tempo: 0s", font=("Arial", 14))
        self.timer_label.pack(side=tk.LEFT, padx=5)
        
        self.error_label = tk.Label(control_frame, text="Erros: 0", font=("Arial", 14))
        self.error_label.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Dica", command=self.give_hint).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Terminar", command=self.finish_game).pack(side=tk.LEFT, padx=5)

        # Grade de Sudoku
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        grid_frame = tk.Frame(self.root)
        grid_frame.pack()
        
        for box_row in range(3):
            for box_col in range(3):
                subgrid = tk.Frame(grid_frame, bd=2, relief="solid")
                subgrid.grid(row=box_row, column=box_col, padx=3, pady=3)
                for i in range(3):
                    for j in range(3):
                        entry = tk.Entry(subgrid, width=2, font=("Arial", 18), justify="center")
                        entry.grid(row=i, column=j, padx=1, pady=1)
                        self.cells[box_row * 3 + i][box_col * 3 + j] = entry
                        entry.bind("<FocusOut>", 
                                   lambda e, x=box_row * 3 + i, y=box_col * 3 + j: self.check_entry(x, y))

    def load_scores(self):
        """Carrega os recordes do arquivo JSON"""
        if os.path.exists(self.score_file):
            with open(self.score_file, "r") as file:
                return json.load(file)
        return {level: None for level in ["muito fácil", "fácil", "médio", "difícil", "muito difícil"]}

    def save_scores(self):
        """Salva os recordes no arquivo JSON"""
        with open(self.score_file, "w") as file:
            json.dump(self.scores, file, indent=4)

    def show_scoreboard(self):
        """Exibe o placar com os recordes"""
        scoreboard_window = tk.Toplevel(self.root)
        scoreboard_window.title("ScoreBoard")
        
        tk.Label(scoreboard_window, text="ScoreBoard", font=("Arial", 16)).pack(pady=10)
        
        for level, time in self.scores.items():
            formatted_time = "Nenhum recorde" if time is None else self.format_time(time)
            record = f"{level.capitalize()}: {formatted_time}"
            tk.Label(scoreboard_window, text=record, font=("Arial", 14)).pack()


    def generate_board(self):
        """Gera um tabuleiro válido de Sudoku"""
        def is_valid_in_solution(board, row, col, num):
            """Verifica se um número é válido na solução"""
            if num in board[row]:
                return False
            if num in [board[i][col] for i in range(9)]:
                return False
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(start_row, start_row + 3):
                for j in range(start_col, start_col + 3):
                    if board[i][j] == num:
                        return False
            return True

        def fill_board(board):
            """Preenche o tabuleiro recursivamente com números válidos"""
            for row in range(9):
                for col in range(9):
                    if board[row][col] == 0:
                        random_nums = list(range(1, 10))
                        random.shuffle(random_nums)
                        for num in random_nums:
                            if is_valid_in_solution(board, row, col, num):
                                board[row][col] = num
                                if fill_board(board):
                                    return True
                                board[row][col] = 0
                        return False
            return True

        base_board = [[0 for _ in range(9)] for _ in range(9)]
        fill_board(base_board)

        # Remover células para criar o quebra-cabeça com base na dificuldade
        difficulty_levels = {
            "muito fácil": 15,
            "fácil": 25,
            "médio": 40,
            "difícil": 60,
            "muito difícil": 75,
        }

        cells_to_remove = difficulty_levels[self.difficulty]
        puzzle = [row[:] for row in base_board]

        for _ in range(cells_to_remove):
            x, y = random.randint(0, 8), random.randint(0, 8)
            while puzzle[x][y] == 0:
                x, y = random.randint(0, 8), random.randint(0, 8)
            puzzle[x][y] = 0

        return puzzle, base_board

    def new_game(self):
        """Inicia um novo jogo com o tabuleiro gerado"""
        self.errors = 0
        self.error_label.config(text="Erros: 0")
        self.start_time = time.time()
        self.game_over = False
        self.board, self.solution = self.generate_board()
        self.update_board()
        self.update_timer()

    def update_board(self):
        """Atualiza o tabuleiro visualmente"""
        for i in range(9):
            for j in range(9):
                value = self.board[i][j]
                self.cells[i][j].delete(0, tk.END)
                if value != 0:
                    self.cells[i][j].insert(0, value)
                    self.cells[i][j].config(state="disabled", fg="black")
                else:
                    self.cells[i][j].config(state="normal", fg="blue")

    def check_entry(self, x, y):
        """Verifica a entrada do jogador em um quadrado"""
        if self.game_over:
            return
        entry = self.cells[x][y]
        value = entry.get()

        if not value.isdigit():
            entry.delete(0, tk.END)
            return

        value = int(value)

        if not self.is_valid_move(x, y, value):
            entry.config(fg="red")
            self.errors += 1
            self.error_label.config(text=f"Erros: {self.errors}")
            if self.errors >= 3:
                self.end_game("GAME OVER")
        else:
            entry.config(fg="green")
            self.board[x][y] = value

    def is_valid_move(self, x, y, value):
        """Verifica se o movimento do jogador é válido"""
        if value in [self.board[x][j] for j in range(9) if j != y]:
            return False
        if value in [self.board[i][y] for i in range(9) if i != x]:
            return False
        start_row, start_col = 3 * (x // 3), 3 * (y // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if (i != x or j != y) and self.board[i][j] == value:
                    return False
        return True

    def format_time(self, seconds):
        """Formata o tempo em segundos para o formato hh:mm:ss"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"


    def update_timer(self):
        """Atualiza o temporizador do jogo no formato hh:mm:ss"""
        if not self.game_over:
            elapsed = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"Tempo: {hours:02}:{minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)


    def give_hint(self):
        """Fornece uma dica ao jogador"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    self.cells[i][j].delete(0, tk.END)
                    self.cells[i][j].insert(0, self.solution[i][j])
                    self.cells[i][j].config(fg="green")
                    self.board[i][j] = self.solution[i][j]
                    return

    def finish_game(self):
        """Verifica se o jogador completou o jogo corretamente"""
        if all(self.board[i][j] == self.solution[i][j] for i in range(9) for j in range(9)):
            elapsed = int(time.time() - self.start_time)
            self.update_score(elapsed)
            self.end_game(f"Parabéns, você completou o jogo em {elapsed}s!")
        else:
            messagebox.showinfo("Jogo Incompleto", "O jogo não foi completado corretamente.")

    def update_score(self, elapsed):
        """Atualiza o placar se o jogador tiver um novo recorde"""
        formatted_time = self.format_time(elapsed)
        current_best = self.scores[self.difficulty]
        if current_best is None or elapsed < current_best:
            self.scores[self.difficulty] = elapsed  # Salvar tempo em segundos
            self.save_scores()


    def end_game(self, message):
        """Finaliza o jogo e exibe uma mensagem"""
        self.game_over = True
        elapsed = int(time.time() - self.start_time)
        formatted_time = self.format_time(elapsed)
        messagebox.showinfo("Fim de Jogo", f"{message}\nTempo: {formatted_time}")
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()
