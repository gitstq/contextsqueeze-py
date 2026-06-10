"""
Command-line interface for ContextSqueeze.
"""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from .compressor import ContextCompressor
from .router import ContentRouter

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="ctxsq")
@click.option("--model", default="gpt-4", help="LLM model for token counting")
@click.pass_context
def main(ctx, model):
    """ContextSqueeze - Lightweight LLM Context Compression & Intelligent Routing"""
    ctx.ensure_object(dict)
    ctx.obj["model"] = model
    ctx.obj["compressor"] = ContextCompressor(model)


@main.command()
@click.argument("text", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="File to compress")
@click.option("--strategy", "-s", help="Compression strategy (auto-detected if not specified)")
@click.option("--ratio", "-r", default=0.5, type=float, help="Target compression ratio (0-1)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def compress(ctx, text, file, strategy, ratio, output):
    """Compress text or file content."""
    compressor = ctx.obj["compressor"]

    if file:
        content = Path(file).read_text(encoding="utf-8")
        filename = Path(file).name
    elif text:
        content = text
        filename = None
    else:
        # Read from stdin
        content = sys.stdin.read()
        filename = None

    if not content.strip():
        console.print("[red]Error: No content to compress[/red]")
        sys.exit(1)

    # Detect content type
    content_type = ContentRouter.detect(content, filename)
    detected_strategy = ContentRouter.get_strategy_name(content_type)

    # Use specified strategy or auto-detected
    use_strategy = strategy or detected_strategy

    with console.status("[bold green]Compressing..."):
        result = compressor.compress(
            content, strategy=use_strategy, target_ratio=ratio, filename=filename
        )

    # Display results
    stats = compressor.get_stats(result)

    table = Table(title="Compression Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Strategy", stats["strategy"])
    table.add_row("Content Type", content_type.name)
    table.add_row("Original Tokens", str(stats["original_tokens"]))
    table.add_row("Compressed Tokens", str(stats["compressed_tokens"]))
    table.add_row("Tokens Saved", str(stats["tokens_saved"]))
    table.add_row("Savings", f"{stats['savings_percent']}%")
    table.add_row("Original Cost", f"${stats['original_cost_usd']:.6f}")
    table.add_row("Compressed Cost", f"${stats['compressed_cost_usd']:.6f}")
    table.add_row("Cost Saved", f"${stats['cost_saved_usd']:.6f}")

    console.print(table)

    # Show preview
    preview = result.compressed_text[:500]
    if len(result.compressed_text) > 500:
        preview += "..."

    console.print(Panel(preview, title="Compressed Preview", border_style="blue"))

    # Save if output specified
    if output:
        Path(output).write_text(result.compressed_text, encoding="utf-8")
        console.print(f"[green]Saved to {output}[/green]")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.pass_context
def detect(ctx, file):
    """Detect content type of a file."""
    content = Path(file).read_text(encoding="utf-8")
    content_type = ContentRouter.detect(content, Path(file).name)
    strategy = ContentRouter.get_strategy_name(content_type)

    tree = Tree(f"[bold]{Path(file).name}[/bold]")
    tree.add(f"Content Type: [cyan]{content_type.name}[/cyan]")
    tree.add(f"Recommended Strategy: [green]{strategy}[/green]")
    tree.add(f"Size: [yellow]{len(content)} chars[/yellow]")

    console.print(tree)


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--strategy", "-s", help="Compression strategy")
@click.option("--ratio", "-r", default=0.5, type=float, help="Target compression ratio")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def batch(ctx, file, strategy, ratio, output):
    """Batch compress a JSONL file with multiple messages."""
    compressor = ctx.obj["compressor"]
    lines = Path(file).read_text(encoding="utf-8").strip().split("\n")

    results = []
    total_original = 0
    total_compressed = 0

    with console.status(f"[bold green]Processing {len(lines)} items..."):
        for line in lines:
            try:
                data = json.loads(line)
                content = data.get("content", "")
                if content:
                    result = compressor.compress(content, strategy=strategy, target_ratio=ratio)
                    data["content"] = result.compressed_text
                    data["_compression"] = {
                        "strategy": result.strategy,
                        "savings_percent": result.savings_percent,
                    }
                    total_original += result.original_tokens
                    total_compressed += result.compressed_tokens
                results.append(data)
            except json.JSONDecodeError:
                results.append({"error": "Invalid JSON", "line": line})

    # Output results
    output_text = "\n".join(json.dumps(r, ensure_ascii=False) for r in results)

    if output:
        Path(output).write_text(output_text, encoding="utf-8")
        console.print(f"[green]Saved {len(results)} items to {output}[/green]")
    else:
        console.print(output_text)

    # Summary
    if total_original > 0:
        savings = (total_original - total_compressed) / total_original * 100
        console.print(f"\n[bold]Total Savings: {savings:.1f}% ({total_original} -> {total_compressed} tokens)[/bold]")


@main.command()
def strategies():
    """List available compression strategies."""
    table = Table(title="Available Compression Strategies")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Best For", style="yellow")

    strategies_info = [
        ("semantic", "Sentence importance scoring with filler removal", "General text, articles"),
        ("code", "Comment removal and whitespace collapse", "Source code files"),
        ("json", "Minification and array truncation", "JSON data, API responses"),
        ("text", "Paragraph-based extractive summarization", "Long documents, logs"),
    ]

    for name, desc, best_for in strategies_info:
        table.add_row(name, desc, best_for)

    console.print(table)


if __name__ == "__main__":
    main()
