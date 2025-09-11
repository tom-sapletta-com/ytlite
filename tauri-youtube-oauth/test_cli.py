import click
import youtube_uploader as yu

@click.command()
def test_cli():
    click.echo("CLI is working")

yu.cli.add_command(test_cli)

if __name__ == "__main__":
    yu.cli()
