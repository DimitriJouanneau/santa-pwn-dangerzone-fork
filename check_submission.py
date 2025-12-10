#!/usr/bin/env python3

import re
import sys
from pathlib import Path

import click
import fitz
import fuzzysearch


@click.command
@click.option(
    "--safe-submission",
    "-s",
    help="Path to the sanitized submission",
    type=click.Path(exists=True),
)
@click.option("--logs", "-l", type=click.Path(exists=True))
@click.option("--secrets-dir", "-S", required=True, type=click.Path(exists=True))
def main(safe_submission: Path, logs: Path, secrets_dir: Path):
    click.echo("Taking a peek over Kenny's flags...")
    secrets = []
    for f in Path(secrets_dir).iterdir():
        secret = f.read_text().strip()
        click.echo(f"{f.name}: {secret}")
        secrets.append(secret)
    click.echo()

    long_text = ""
    if safe_submission:
        click.echo("Reading your submission very carefully...")
        doc = fitz.open(safe_submission)
        click.echo("Identified the following strings in your submission:")
        click.echo("============= SUBMISSION STARTS ==============")
        for i, page in enumerate(doc.pages()):
            print(page.get_text())
            long_text += page.get_text()
        click.echo("============= SUBMISSION ENDS ==============")
        click.echo(
            "TIP: If the identified text is very inaccurate, please try to increase your"
            " font size. Minor differences are tolerated by our script."
        )
    else:
        click.echo("No submission was found, probably the conversion failed")

    if logs:
        click.echo("Looking into the conversion logs as well...")
        long_text += Path(logs).read_text()
    else:
        click.echo("Conversion logs were not provided...")

    if not long_text:
        click.echo("You need to pass a safe submission or conversion logs")
        sys.exit(1)
    click.echo()

    click.echo("Normalizing the submission and keeping only letters and numbers")
    long_text = re.sub("[^0-9a-zA-Z]", "", long_text).lower()
    click.echo(
        f"We're now gonna look into this long soup of letters for a flag:\n{long_text}"
    )
    click.echo()

    for secret in secrets:
        match = fuzzysearch.find_near_matches(secret, long_text, max_l_dist=4)
        if match:
            click.echo("Santa, we have a problem...")
            return

    click.echo("No secret flag in your submission, phew!...")
    sys.exit(1)


if __name__ == "__main__":
    main()
