from view.chess_management_view import ChessManagementView


def main():
    running = True
    menu_view = ChessManagementView()
    while running:

        choix = menu_view.show_menu_view(menu_view.build_menu())
        if choix is None:
            continue
        elif choix is False:
            running = False
        else:
            choix()


if __name__ == '__main__':
    main()
