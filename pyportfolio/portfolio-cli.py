import locale
import logging
from portfolio import Portfolio
import cutie
from utils import logger
import click
from clihelper import ltcg_tax_harvesting_summary

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.command(name="portfolio-cli", context_settings=CONTEXT_SETTINGS)
@click.option(
    "-f",
    "--caspdf",
    type=click.Path(exists=True),
    metavar="CAS_PDF_FILE",
    prompt="CAS PDF File Path",
)
def main(caspdf):
    logger.setLevel(logging.INFO)
    locale.setlocale(locale.LC_MONETARY, 'en_IN')

    password = cutie.secure_input("Please enter the pdf password:")
    
    portfolio = Portfolio(
        caspdf,
        password,
    )

    # Options
    LTCG_TAX_HARVEST = 'LTGC Tax Harvesting'
    VALUATION = ' Portfolio Valuation'
    EXIT = 'Exit'

    options = [
        LTCG_TAX_HARVEST,
        VALUATION,
        EXIT,
    ]

    while True:
        option = options[
            cutie.select(options, selected_index=0)
        ]

        if option == LTCG_TAX_HARVEST:
            ltcg_tax_harvesting_summary(portfolio)
        elif option == VALUATION:
            break
        elif option == EXIT:
            break

if __name__ == "__main__":
    main(prog_name="portfolio-cli")