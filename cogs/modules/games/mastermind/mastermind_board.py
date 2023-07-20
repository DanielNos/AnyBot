from nextcord import Embed


def create_board(combinations = None, turn = 0, correct = None):
    embed: Embed = Embed(title="Mastermind")
    
    offset = 0
    if combinations and correct and turn > 0 and combinations[turn-1] == correct:
      offset = -1

    text = "```"
    for i in range(0, 10):
        # Create index
        index = str(i+1)
        if i+1 < 10:
            index = " " + index
        index = "  " + index

        # Create combination
        combination = ""
        if not combinations:
            # Empty combination
            combination = "🔳 🔳 🔳 🔳 "
        else:
            # Get combination
            for j in range(4):
                if j < len(combinations[i]):
                    combination += combinations[i][j] + " "
                else:
                    combination += "🔳 "
            combination = combination[:-1]

        # Create hints
        color = 0
        col_pos = 0

        if i < turn and correct is not None:
            for j in range(4):
                if combinations[i][j] == correct[j]:
                    col_pos +=1
                elif combinations[i][j] in correct:
                    color += 1

        # Assemble row
        if i == turn + offset:
            text += f"▶️ {index[2:]} {combination} {color} | {col_pos} ◀️\n"
        else:
            text += f"{index} {combination} {color} | {col_pos}\n"

    if turn >= 9:
        turn = 9
        
    if not combinations or not correct or turn > 0 and turn < 9 and combinations[turn-1] != correct:
        embed.set_footer(text="Figure out the correct combination!\nLeft number = correct color, wrong position.\nRight number = correct color, correct position.")

    embed.add_field(name=f"Turn: {turn + 1}/10", value=text + "```")
    return embed