import os
import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from bot.validators import OrderInput
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.logging_config import setup_logging

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(
    help="Binance Futures Testnet Trading Bot CLI",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False
)
console = Console()
logger = setup_logging()

@app.callback()
def main():
    """Binance Futures Testnet CLI Order Management Tool."""
    pass

@app.command(name="place-order")
def place_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair (e.g. BTCUSDT)"),
    side: str = typer.Option(..., "--side", "-d", help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="Order type: MARKET or LIMIT"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: float = typer.Option(None, "--price", "-p", help="Price (Required for LIMIT)"),
    api_key: str = typer.Option(None, "--api-key", envvar="BINANCE_API_KEY", help="Binance Testnet API Key"),
    api_secret: str = typer.Option(None, "--api-secret", envvar="BINANCE_API_SECRET", help="Binance Testnet API Secret"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate order validation without calling API"),
):
    """Place a Market or Limit order on Binance Futures Testnet."""
    
    console.print("\n[bold blue]=== Binance Futures Order Execution ===[/bold blue]\n")

    # 1. Validation Layer
    try:
        validated_input = OrderInput(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        validated_input.check_type_specific_requirements()
    except Exception as err:
        console.print(f"[bold red]Validation Error:[/bold red] {err}")
        logger.error(f"CLI Input Validation Failed: {err}")
        raise typer.Exit(code=1)

    # Print Order Request Summary Table
    summary_table = Table(title="Order Request Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Parameter", style="cyan")
    summary_table.add_column("Value", style="green")
    summary_table.add_row("Symbol", validated_input.symbol)
    summary_table.add_row("Side", validated_input.side)
    summary_table.add_row("Type", validated_input.order_type)
    summary_table.add_row("Quantity", str(validated_input.quantity))
    summary_table.add_row("Price", str(validated_input.price) if validated_input.price else "MARKET")
    summary_table.add_row("Mode", "DRY RUN (Simulated)" if dry_run else "LIVE TESTNET")
    console.print(summary_table)

    # Bonus: Dry-Run Exit Point (skips credential check and API call)
    if dry_run:
        console.print(Panel("[bold yellow]DRY RUN SUCCESS: Order validated & constructed successfully (API call skipped).[/bold yellow]"))
        logger.info(f"Dry Run Order Validated for {validated_input.symbol}")
        raise typer.Exit(code=0)

    # 2. Retrieve & Sanitize Credentials
    raw_key = api_key or os.getenv("BINANCE_API_KEY")
    raw_secret = api_secret or os.getenv("BINANCE_API_SECRET")

    if not raw_key or not raw_secret:
        console.print("[bold red]Error:[/bold red] API Key and Secret are required. Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file or pass them via CLI.")
        logger.error("Execution failed: Missing API Credentials")
        raise typer.Exit(code=1)

    # Strip quotes, whitespace, and hidden formatting characters
    clean_key = str(raw_key).strip().strip("'").strip('"')
    clean_secret = str(raw_secret).strip().strip("'").strip('"')

    # Quick sanity check for valid length
    if len(clean_key) < 32:
        console.print(f"[bold red]Error:[/bold red] Provided API Key is too short ({len(clean_key)} chars). Ensure you copied the full key from testnet.binancefuture.com.")
        logger.error(f"Execution failed: Malformed API Key length ({len(clean_key)})")
        raise typer.Exit(code=1)

    # 3. Execution Layer
    try:
        client = BinanceFuturesClient(api_key=clean_key, api_secret=clean_secret)
        manager = OrderManager(client)

        with console.status("[bold yellow]Submitting order to Binance Testnet...[/bold yellow]"):
            response = manager.place_order(
                symbol=validated_input.symbol,
                side=validated_input.side,
                order_type=validated_input.order_type,
                quantity=validated_input.quantity,
                price=validated_input.price
            )

        # Print Response Output Table
        res_table = Table(title="Order Execution Result", show_header=True, header_style="bold yellow")
        res_table.add_column("Field", style="cyan")
        res_table.add_column("Response Value", style="white")

        res_table.add_row("Order ID", str(response.get("orderId")))
        res_table.add_row("Status", str(response.get("status")))
        res_table.add_row("Executed Qty", str(response.get("executedQty")))
        res_table.add_row("Avg Price", str(response.get("avgPrice", "0.0")))
        res_table.add_row("Time in Force", str(response.get("timeInForce", "N/A")))
        
        console.print(res_table)
        console.print(Panel("[bold green]SUCCESS: Order executed successfully![/bold green]"))

    except Exception as e:
        console.print(f"\n[bold red]Execution Failed:[/bold red] {e}")
        logger.error(f"Order Execution Failed: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()