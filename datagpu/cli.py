"""Command-line interface for DataGPU."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from datagpu import __version__
from datagpu.compiler import DataCompiler
from datagpu.types import CompilationConfig, RankMethod
from datagpu.cache import CacheManager

app = typer.Typer(
    name="datagpu",
    help="Open-source data compiler for AI training datasets",
    add_completion=False
)
console = Console()


@app.command()
def compile(
    source: Path = typer.Argument(
        ...,
        help="Path to source dataset (CSV, Parquet, JSON, JSONL)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True
    ),
    out: Path = typer.Option(
        Path("compiled"),
        "--out", "-o",
        help="Output directory for compiled dataset"
    ),
    rank: bool = typer.Option(
        True,
        "--rank/--no-rank",
        help="Enable quality ranking"
    ),
    rank_method: RankMethod = typer.Option(
        RankMethod.RELEVANCE,
        "--rank-method",
        help="Ranking method to use"
    ),
    rank_target: Optional[str] = typer.Option(
        None,
        "--rank-target",
        help="Target query for relevance ranking"
    ),
    dedupe: bool = typer.Option(
        True,
        "--dedupe/--no-dedupe",
        help="Enable deduplication"
    ),
    cache: bool = typer.Option(
        True,
        "--cache/--no-cache",
        help="Enable caching"
    ),
    compression: str = typer.Option(
        "zstd",
        "--compression",
        help="Compression algorithm (zstd, snappy, gzip)"
    ),
    verbose: bool = typer.Option(
        True,
        "--verbose/--quiet",
        help="Verbose output"
    )
):
    """
    Compile a dataset: clean, deduplicate, rank, and optimize.
    
    Example:
        datagpu compile data/train.csv --rank --dedupe --cache
    """
    console.print(f"[bold cyan]DataGPU v{__version__}[/bold cyan]")
    console.print(f"Compiling: [yellow]{source}[/yellow]\n")
    
    # Create compilation config
    config = CompilationConfig(
        source_path=source,
        output_path=out,
        dedupe=dedupe,
        rank=rank,
        rank_method=rank_method,
        rank_target=rank_target,
        cache=cache,
        compression=compression,
        verbose=verbose
    )
    
    # Run compilation
    try:
        compiler = DataCompiler(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Compiling dataset...", total=None)
            output_path, manifest, stats = compiler.compile()
        
        # Display results
        console.print("\n[bold green]Compilation complete![/bold green]\n")
        
        # Stats table
        table = Table(show_header=False, box=None)
        table.add_row("[cyan]Rows processed[/cyan]", f"{stats.total_rows:,}")
        table.add_row("[cyan]Valid rows[/cyan]", f"{stats.valid_rows:,} ({stats.valid_ratio:.1%})")
        table.add_row("[cyan]Duplicates removed[/cyan]", f"{stats.duplicates_removed:,} ({stats.dedup_ratio:.1%})")
        table.add_row("[cyan]Ranked samples[/cyan]", f"{stats.ranked_samples:,}")
        table.add_row("[cyan]Processing time[/cyan]", f"{stats.processing_time:.1f}s")
        table.add_row("[cyan]Output[/cyan]", f"{output_path}")
        table.add_row("[cyan]Manifest[/cyan]", f"{out / 'manifest.yaml'}")
        
        console.print(table)
        console.print(f"\n[dim]Dataset version: {manifest.version}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def info(
    manifest: Path = typer.Argument(
        ...,
        help="Path to manifest.yaml",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True
    )
):
    """
    Display information about a compiled dataset.
    
    Example:
        datagpu info compiled/manifest.yaml
    """
    from datagpu.utils import load_yaml
    
    try:
        data = load_yaml(manifest)
        
        console.print(f"\n[bold cyan]Dataset: {data['dataset_name']}[/bold cyan]")
        console.print(f"[dim]Version: {data['version']}[/dim]\n")
        
        table = Table(show_header=False, box=None)
        table.add_row("[cyan]Rows[/cyan]", f"{data['rows']:,}")
        table.add_row("[cyan]Columns[/cyan]", f"{data['columns']}")
        table.add_row("[cyan]Dedup ratio[/cyan]", f"{data['dedup_ratio']:.1%}")
        table.add_row("[cyan]Rank method[/cyan]", data['rank_method'])
        table.add_row("[cyan]Created[/cyan]", data['created_at'])
        table.add_row("[cyan]Hash[/cyan]", data['hash'][:16] + "...")
        table.add_row("[cyan]Source[/cyan]", data['source_path'])
        table.add_row("[cyan]Compiled[/cyan]", data['compiled_path'])
        
        console.print(table)
        
        if data.get('schema'):
            console.print("\n[bold]Schema:[/bold]")
            schema_table = Table(show_header=True)
            schema_table.add_column("Column", style="cyan")
            schema_table.add_column("Type", style="yellow")
            
            for col, dtype in data['schema'].items():
                schema_table.add_row(col, dtype)
            
            console.print(schema_table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def cache_list(
    dataset: Optional[str] = typer.Option(
        None,
        "--dataset", "-d",
        help="Filter by dataset name"
    )
):
    """
    List cached datasets.
    
    Example:
        datagpu cache-list
        datagpu cache-list --dataset train
    """
    cache_mgr = CacheManager()
    entries = cache_mgr.list_entries(dataset)
    
    if not entries:
        console.print("[yellow]No cached datasets found[/yellow]")
        return
    
    table = Table(show_header=True)
    table.add_column("Dataset", style="cyan")
    table.add_column("Version", style="yellow")
    table.add_column("Hash", style="dim")
    table.add_column("Created", style="green")
    
    for entry in entries:
        table.add_row(
            entry["dataset_name"],
            entry["version"],
            entry["source_hash"][:12] + "...",
            entry["created_at"]
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(entries)} entries[/dim]")


@app.command()
def cache_clear(
    dataset: Optional[str] = typer.Option(
        None,
        "--dataset", "-d",
        help="Clear specific dataset cache"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation"
    )
):
    """
    Clear cache entries.
    
    Example:
        datagpu cache-clear --force
        datagpu cache-clear --dataset train
    """
    if not force:
        confirm = typer.confirm(
            f"Clear cache for {'dataset: ' + dataset if dataset else 'all datasets'}?"
        )
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            return
    
    cache_mgr = CacheManager()
    deleted = cache_mgr.clear_cache(dataset)
    
    console.print(f"[green]Cleared {deleted} cache entries[/green]")


@app.command()
def version():
    """Display DataGPU version."""
    console.print(f"DataGPU version {__version__}")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
