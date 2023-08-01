

def sort_players(players_pos, dealer_pos, nr_of_players):
    # In players_sorted,
    #   starter is index 0,
    #   I am index (0 + jump % nr_of_players),
    #   big-ante is index -1
    #   small-ante is index -2
    #   dealer is index -3

    # Sort players
    # Get point in middle of screen
    navigate_pnt = (960, 540)
    # I am close to the middle and furthest down
    me_ind = min(
        range(len(players_pos)),
        key=lambda ind: (abs(players_pos[ind][0] - navigate_pnt[0]) - (players_pos[ind][1] - navigate_pnt[1]))
    )

    # Player after me is to the left of and below middle
    second_ind = min(
        range(len(players_pos)),
        key=lambda ind: ((players_pos[ind][0] - navigate_pnt[0]) - (players_pos[ind][1] - navigate_pnt[1]))
    )

    # Third player is to the left of and above middle
    third_ind = min(
        range(len(players_pos)),
        key=lambda ind: ((players_pos[ind][0] - navigate_pnt[0]) + (players_pos[ind][1] - navigate_pnt[1]))
    )

    fourth_ind = min(
        range(len(players_pos)),
        key=lambda ind: (abs(players_pos[ind][0] - navigate_pnt[0]) + (players_pos[ind][1] - navigate_pnt[1]))
    )

    fifth_ind = min(
        range(len(players_pos)),
        key=lambda ind: (-(players_pos[ind][0] - navigate_pnt[0]) + (players_pos[ind][1] - navigate_pnt[1]))
    )

    # Player after me is to the left of and below middle
    sixth_ind = min(
        range(len(players_pos)),
        key=lambda ind: (-(players_pos[ind][0] - navigate_pnt[0]) - (players_pos[ind][1] - navigate_pnt[1]))
    )

    if not me_ind != second_ind != third_ind != fourth_ind != fifth_ind != sixth_ind:
        raise Exception("Non-unique indexes for players. Faulty match")

    # Sort players so that they are in play-order. (So that I can get who starts)
                                                                                                    # Hard-code 6 players!!!
    players_sorted = [players_pos[me_ind], players_pos[second_ind], players_pos[third_ind], players_pos[fourth_ind],
                      players_pos[fifth_ind], players_pos[sixth_ind]]

    dealer_ind = min(
        range(len(players_sorted)),
        key=lambda ind: ((dealer_pos[:2] - players_sorted[ind][:2])[0] ** 2 +
                         (dealer_pos[:2] - players_sorted[ind][:2])[1] ** 2) ** 0.5
    )

    starter_ind = (dealer_ind + 3) % nr_of_players

    # Sort players so that starter is always 0
    jump = nr_of_players - starter_ind
    players_sorted = [players_sorted[(0 + jump) % nr_of_players],
                      players_sorted[(1 + jump) % nr_of_players],
                      players_sorted[(2 + jump) % nr_of_players],
                      players_sorted[(3 + jump) % nr_of_players],
                      players_sorted[(4 + jump) % nr_of_players],
                      players_sorted[(5 + jump) % nr_of_players]]

    return players_sorted, (jump % nr_of_players)
