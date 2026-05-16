"""CLI interface for the Second Brain."""

import os
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint

from .knowledge_base import (
    build_knowledge_base,
    save_knowledge_base,
    load_knowledge_base,
    get_categories_summary,
)
from .search import search, filter_by_category
from .models import ConversationHistory, ChatMessage

console = Console()


def _header():
    console.print(Panel.fit(
        "[bold cyan]🧠 Second Brain[/bold cyan]\n"
        "[dim]Powered by Google Drive + Claude[/dim]",
        border_style="cyan",
    ))


@click.group()
def cli():
    """Second Brain - sua base de conhecimento pessoal."""
    pass


@cli.command()
def build():
    """Constrói a base de conhecimento a partir dos arquivos do Google Drive."""
    _header()
    console.print("[bold]Construindo base de conhecimento...[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Carregando índice do Drive...", total=None)
        kb = build_knowledge_base()
        progress.update(task, description=f"Processando {kb.total_files} arquivos...")
        save_knowledge_base(kb)
        progress.update(task, description="Base de conhecimento salva!", completed=True)

    cats = get_categories_summary(kb)
    table = Table(title="Categorias da Base de Conhecimento", border_style="cyan")
    table.add_column("Categoria", style="bold")
    table.add_column("Arquivos", justify="right", style="green")

    for cat, count in cats.items():
        table.add_row(cat, str(count))

    console.print(table)
    console.print(f"\n[green]✓ {kb.total_files} arquivos indexados com sucesso![/green]")


@cli.command()
@click.argument("query")
@click.option("--top", "-k", default=5, help="Número de resultados")
@click.option("--category", "-c", default=None, help="Filtrar por categoria")
def search_cmd(query: str, top: int, category: str | None):
    """Busca na base de conhecimento."""
    kb = load_knowledge_base()

    if category:
        files = filter_by_category(kb, category)
        from .models import KnowledgeBase
        kb_filtered = KnowledgeBase(
            last_synced=kb.last_synced,
            total_files=len(files),
            files=files,
        )
        results = search(kb_filtered, query, top_k=top)
    else:
        results = search(kb, query, top_k=top)

    if not results:
        console.print(f"[yellow]Nenhum resultado para '{query}'[/yellow]")
        return

    console.print(f"\n[bold]Resultados para: [cyan]{query}[/cyan][/bold]\n")

    for i, result in enumerate(results, 1):
        f = result.file
        console.print(Panel(
            f"[bold]{f.title}[/bold]\n"
            f"[dim]Categoria:[/dim] [cyan]{f.category}[/cyan]  "
            f"[dim]Relevância:[/dim] [green]{result.relevance_score:.1f}[/green]\n"
            + (f"\n[italic]{result.matched_snippet}[/italic]" if result.matched_snippet else ""),
            title=f"#{i}",
            border_style="blue",
        ))

    if results and results[0].file.view_url:
        console.print(f"\n[dim]Abrir no Drive: {results[0].file.view_url}[/dim]")


@cli.command()
def categories():
    """Lista todas as categorias e arquivos."""
    kb = load_knowledge_base()
    cats = get_categories_summary(kb)

    table = Table(title="Categorias", border_style="cyan")
    table.add_column("Categoria", style="bold cyan")
    table.add_column("Arquivos", justify="right", style="green")

    for cat, count in cats.items():
        table.add_row(cat, str(count))

    console.print(table)


@cli.command()
@click.argument("category")
def list_files(category: str):
    """Lista arquivos de uma categoria específica."""
    kb = load_knowledge_base()
    files = filter_by_category(kb, category)

    if not files:
        console.print(f"[yellow]Categoria '{category}' não encontrada.[/yellow]")
        cats = get_categories_summary(kb)
        console.print("Categorias disponíveis: " + ", ".join(cats.keys()))
        return

    table = Table(title=f"Arquivos: {category}", border_style="cyan")
    table.add_column("Título", style="bold")
    table.add_column("Tipo", style="dim")
    table.add_column("Modificado", style="dim")

    for f in files:
        mime_short = f.mime_type.split("/")[-1].split(".")[-1][:15]
        modified = (f.modified_time or "")[:10]
        table.add_row(f.title[:60], mime_short, modified)

    console.print(table)


@cli.command()
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Chave da API Anthropic")
def chat(api_key: str | None):
    """Conversa com seu Second Brain usando IA."""
    _header()

    if not api_key:
        console.print("[red]Configure ANTHROPIC_API_KEY para usar o chat.[/red]")
        console.print("Exemplo: export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    kb = load_knowledge_base()
    history = ConversationHistory()

    cats = get_categories_summary(kb)
    console.print(f"[green]Base de conhecimento carregada:[/green] {kb.total_files} arquivos")
    console.print("[dim]Categorias: " + ", ".join(cats.keys()) + "[/dim]")
    console.print("\n[bold cyan]Faça uma pergunta sobre seus documentos.[/bold cyan]")
    console.print("[dim]Digite 'sair' para encerrar, 'limpar' para nova conversa.[/dim]\n")

    from .chat import ask

    while True:
        try:
            query = Prompt.ask("[bold green]Você[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Encerrando...[/dim]")
            break

        if query.lower() in ("sair", "exit", "quit"):
            break
        if query.lower() in ("limpar", "clear"):
            history = ConversationHistory()
            console.print("[dim]Conversa reiniciada.[/dim]")
            continue
        if not query.strip():
            continue

        with console.status("[dim]Pensando...[/dim]"):
            try:
                response = ask(kb, query, history, api_key=api_key)
            except Exception as e:
                console.print(f"[red]Erro: {e}[/red]")
                continue

        history.messages.append(ChatMessage(role="user", content=query))
        history.messages.append(ChatMessage(role="assistant", content=response))

        console.print()
        console.print(Panel(
            Markdown(response),
            title="[bold cyan]Second Brain[/bold cyan]",
            border_style="cyan",
        ))
        console.print()


@cli.command()
def stats():
    """Mostra estatísticas da base de conhecimento."""
    kb = load_knowledge_base()
    cats = get_categories_summary(kb)

    from .indexer import get_indexed_count
    from .search import get_readable_files
    readable = get_readable_files(kb)
    indexed = get_indexed_count(kb)

    console.print(Panel(
        f"[bold]Total de arquivos:[/bold] [cyan]{kb.total_files}[/cyan]\n"
        f"[bold]Arquivos legíveis:[/bold] [cyan]{len(readable)}[/cyan]\n"
        f"[bold]Conteúdo indexado:[/bold] [green]{indexed}[/green]\n"
        f"[bold]Última sincronização:[/bold] [dim]{kb.last_synced or 'Nunca'}[/dim]",
        title="[bold]Estatísticas[/bold]",
        border_style="cyan",
    ))

    table = Table(border_style="dim")
    table.add_column("Categoria", style="bold")
    table.add_column("Arquivos", justify="right")

    for cat, count in cats.items():
        table.add_row(cat, str(count))

    console.print(table)
