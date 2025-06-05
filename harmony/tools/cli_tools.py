from rich.console import Console

console = Console()


def display_submenu(title: str, menu_options: list, color: str) -> int:
    """
    Display a submenu and return selection

    Args:
        title: The title of the menu.
        menu_options: A list of menu option strings.
        color: The color to use for the menu.

    Returns:
        int: The index of the selected option, or None if invalid.
    """
    while True:
        console.print(f"\n[{color}]{title}[/{color}]")

        # Display menu items
        for idx, option in enumerate(menu_options, start=1):
            console.print(f"[{color}]{idx}.[/{color}] {option}")

        try:
            choice = int(console.input("Enter your choice: "))
            if 1 <= choice <= len(menu_options):
                return choice - 1
            else:
                console.print(
                    "[bold red]Invalid choice. Please select a valid option.[/bold red]"
                )
        except ValueError:
            console.print("[bold red]Please enter a valid number.[/bold red]")


def display_menu(title, menu_options, color, ascii_art: str = None):
    """
    Display a menu with options and process user input.

    Args:
        title: The title of the menu.
        menu_options: A list of tuples, each containing a label and an action function.
        color: The color to use for the menu.
        ascii_art: ASCII art to display at the top of the menu.
    """
    menu_options += (
        ("[magenta]Return to Main Menu[/magenta]", lambda: "return"),
        ("[red]Exit[/red]", lambda: "exit"),
    )

    while True:
        if ascii_art:
            console.print(f"\n\n[{color}]" + ascii_art + f"[/{color}]")
        console.print(f"\n\n[{color}]{title}:[/{color}]")

        # Display menu items
        for idx, (option, _) in enumerate(menu_options, start=1):
            console.print(f"[{color}]{idx}.[/{color}] {option}")

        try:
            choice = int(console.input("Enter your choice: "))
            if 1 <= choice <= len(menu_options):
                _, action = menu_options[choice - 1]
                result = action()
                if result == "return":
                    console.print(
                        "[bold magenta]Returning to the main menu...[/bold magenta]"
                    )
                    return
                elif result == "exit":
                    console.print("[bold magenta]Goodbye![/bold magenta]")
                    exit(0)
            else:
                console.print(
                    "[bold red]Invalid choice. Please select a valid option.[/bold red]"
                )
        except ValueError:
            console.print("[bold red]Please enter a valid number.[/bold red]")
