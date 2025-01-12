import paramiko
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from tinydb import TinyDB, Query
from getpass import getpass

# Initialize database
db = TinyDB('ssh_client_data.json')
User = Query()

console = Console()

def save_credentials(username, password, ip):
    if not db.search((User.username == username) & (User.ip == ip)):
        db.insert({'username': username, 'password': password, 'ip': ip})
        console.print("[green]Credentials saved successfully![/green]")
    else:
        console.print("[yellow]Credentials already exist.[/yellow]")

def list_saved_credentials():
    table = Table(title="Saved Connections")
    table.add_column("Username", style="cyan")
    table.add_column("IP Address", style="magenta")
    
    for entry in db.all():
        table.add_row(entry['username'], entry['ip'])
    
    console.print(table)

def ssh_connect(username, password, ip):
    client = paramiko.SSHClient()
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        console.print(f"[green]Connecting to {ip} as {username}...[/green]")
        client.connect(ip, username=username, password=password)
        console.print(f"[green]Connected to {ip} successfully.[/green]")

        while True:
            command = Prompt.ask("[cyan]Enter command (or 'exit' to quit)[/cyan]")
            if command.lower() == 'exit':
                console.print("[yellow]Closing connection...[/yellow]")
                client.close()
                console.print("[red]Connection closed.[/red]")
                break

            stdin, stdout, stderr = client.exec_command(command)
            console.print(stdout.read().decode())
            console.print(stderr.read().decode(), style="bold red")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def main():
    while True:
        console.print("\n[bold blue]SSH Client Main Menu[/bold blue]")
        console.print("1. Create a new connection")
        console.print("2. Show saved connections")
        console.print("3. Exit")
        
        choice = Prompt.ask("[cyan]Select an option[/cyan]", choices=["1", "2", "3"])
        
        if choice == "1":
            username = Prompt.ask("[cyan]Username[/cyan]")
            password = getpass("Password: ")
            ip = Prompt.ask("[cyan]IP Address[/cyan]")
            
            save = Prompt.ask("[yellow]Do you want to save the credentials? (yes/no)[/yellow]", choices=["yes", "no"])
            if save == "yes":
                save_credentials(username, password, ip)
            
            ssh_connect(username, password, ip)
        elif choice == "2":
            list_saved_credentials()
        elif choice == "3":
            console.print("[bold red]Exiting program...[/bold red]")
            break

if __name__ == "__main__":
    main()
