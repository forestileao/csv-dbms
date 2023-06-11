import curses


# Function to handle user input and navigate the menu
def handle_input(stdscr, options):
    selected_index = 0

    while True:
        stdscr.clear()
        for i, option in enumerate(options):
            if i == selected_index:
                stdscr.addstr("-> " + option + "\n")
            else:
                stdscr.addstr("   " + option + "\n")

        key = stdscr.getch()

        if key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            stdscr.clear()
            stdscr.addstr("Selected option: " + options[selected_index])
            stdscr.refresh()
            break

        if key == curses.KEY_DOWN:  # Down arrow
            selected_index = (selected_index + 1) % len(options)
        elif key == curses.KEY_UP:  # Up arrow
            selected_index = (selected_index - 1) % len(options)

        stdscr.refresh()


# Main menu options
menu_options = ["Option 1", "Option 2", "Option 3", "Exit"]

# Initialize curses
stdscr_ = curses.initscr()
curses.cbreak()
curses.noecho()
stdscr_.keypad(True)

# Call the function to handle the menu
handle_input(stdscr_, menu_options)

# Clean up curses
curses.nocbreak()
stdscr_.keypad(False)
curses.echo()
curses.endwin()
