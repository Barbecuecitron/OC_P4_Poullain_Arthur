from view.chest_management_view import show_menu_view, build_menu


def main():
    running = True
    while running:
        choix = show_menu_view(build_menu())
        if choix is None:
            continue
        elif choix is False:
            running = False
        else:
            choix()


if __name__ == '__main__':
    main()
