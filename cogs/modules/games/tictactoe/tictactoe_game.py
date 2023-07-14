from nextcord import Message, User, Embed
from math import floor


EMPTY_BOARD = "▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n"


class Game:
    def __init__(self, player: User, opponent: User):
        self.message: Message = None
        self.player: User = player
        self.opponent: User = opponent

        self.turn: int = 1
        self.round: int = 1
        self.board = [[0,0,0], [0,0,0], [0,0,0]]
        self.board_render = self.__create_game_embed()
    

    def get_render(self):
        return self.board_render
    

    def __create_game_embed(self) -> Embed:
        embed = Embed(title="Tic-Tac-Toe | " + self.player.name + " vs. " + self.opponent.name, color=0xFBCE9D)
        embed.add_field(name="Round " + str(self.round) + " | Turn: " + ([self.player.name, self.opponent.name][self.turn-1]), value=EMPTY_BOARD)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/tictactoe.png")

        embed.set_footer(text="Play using /tictactoe play [row] [column]")
        return embed
    

    def __render_board(self) -> str:
        empty = "▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️"
        line = "▫️" * 11 + "\n"
        
        # Convert values to characters
        rendered_board = []
        for y in range(3):
            row = []
            for x in range(3):
                if self.board[x][y] == 0:
                    row.append("▪️")
                elif self.board[x][y] == 1:
                    row.append("🅾️")
                else:
                    row.append("❎")
            rendered_board.append(row)
                    
        # Assemble game board
        render = empty + "\n"
        render += "▪️" + rendered_board[0][0] + "▪️▫️▪️" + rendered_board[1][0] + "▪️▫️▪️" + rendered_board[2][0] + "▪️\n"
        render += empty + "\n" + line + empty + "\n"

        render += "▪️" + rendered_board[0][1] + "▪️▫️▪️" + rendered_board[1][1] + "▪️▫️▪️" + rendered_board[2][1] + "▪️\n"
        render += empty + "\n" + line + empty + "\n"

        render += "▪️" + rendered_board[0][2] + "▪️▫️▪️" + rendered_board[1][2] + "▪️▫️▪️" + rendered_board[2][2] + "▪️\n"
        render += empty

        return render

    
    def play(self, x, y):
        self.board[x][y] = self.turn
        
        self.turn += -int(self.turn == 2) + int(self.turn == 1)
        self.round += 1

        name = f"Round {floor(self.round / 2) + 1} | Turn: {[self.player.name, self.opponent.name][self.turn-1]}"
        self.board_render.set_field_at(0, name=name, value=self.__render_board())

    
    def is_empty(self, x, y) -> bool:
        return self.board[x][y] == 0
    

    def turn_id(self) -> int:
        return [self.player.id, self.opponent.id][self.turn-1]

    
    def __get_player(self, index: int) -> User:
        return [self.player, self.opponent][index-1]
    

    def get_winner(self) -> User:
        for p in [1, 2]:
            # Check rows and columns
            for i in range(3):
                if self.board[i][0] == p and self.board[i][1] == p and self.board[i][2] == p:
                    return self.__get_player(p)
                
                if self.board[0][i] == p and self.board[1][i] == p and self.board[2][i] == p:
                    return self.__get_player(p)
            
            # Check diagonals
            if self.board[0][0] == p and self.board[1][1] == p and self.board[2][2] == p:
                return self.__get_player(p)
            
            if self.board[0][2] == p and self.board[1][1] == p and self.board[2][0] == p:
                return self.__get_player(p)
        
        return None
    
    
    def delete(self):
        global games, game_messages

        games.pop(self.player.id)
        if self.difficulty == None:
            games.pop(self.opponent.id)

        game_messages.pop(self.message.id)