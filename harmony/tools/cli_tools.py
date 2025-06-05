from rich.console import Console

console = Console()


def display_submenu(title: str, menu_options: tuple, color: str) -> int:
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
        console.print(f"\n[bold {color}]{title}[/bold {color}]")

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


def display_menu(
    title,
    color,
    menu_options: tuple = None,
    dynamic_options: callable = None,
    ascii_art: str = None,
):
    """
    Display a menu with options and process user input.

    Args:
        title: The title of the menu.
        menu_options: A list of tuples, each containing a label and an action function.
        dynamic_options: Optional function that returns fresh menu options after each action.
        color: The color to use for the menu.
        ascii_art: ASCII art to display at the top of the menu.
    """
    while True:
        # Get fresh menu options if a dynamic options function is provided
        full_options = (
            tuple(dynamic_options()) if dynamic_options else tuple(menu_options)
        )

        # Add standard menu options as new tuples (concatenation creates a new tuple)
        if title != "Main Menu":
            full_options += (
                ("[magenta]Return to Main Menu[/magenta]", lambda: "return"),
            )
        full_options += (("[red]Exit[/red]", lambda: "exit"),)

        if ascii_art:
            console.print(f"\n\n[{color}]" + ascii_art + f"[/{color}]")
        console.print(f"\n\n[bold {color}]{title}:[/bold {color}]")

        # Display menu items
        for idx, (option, _) in enumerate(full_options, start=1):
            console.print(f"[{color}]{idx}.[/{color}] {option}")

        try:
            choice = int(console.input("Enter your choice: "))
            if 1 <= choice <= len(full_options):
                _, action = full_options[choice - 1]
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
