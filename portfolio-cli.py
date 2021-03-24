import locale
import logging
from portfolio import Portfolio
import tabulate
import cutie
from utils import logger
import click

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


def ltcg_tax_harvesting_summary(portfolio: Portfolio):
    summary = portfolio.ltcg_tax_harvesting_summary()

    print(click.style("\nTotal LTCG Tax that can be harvested this FY: ", bold=True) + click.style(locale.currency(summary["total_ltcg"], grouping=True), bold=True, fg="green"))
    print(click.style("Total value of units to be sold and bought: ", bold=True) + click.style(locale.currency(summary["total_amount"], grouping=True), bold=True, fg="green"))
    print(click.style("Note: Buy and sell the following units on the same day to avoid losses due to NAV fluctuations", bold=True, fg="yellow"))

    schemes_breakup = summary["schemes"]
    schemes_breakup = [{k: v for k, v in scheme.items() if k != "transactions"} for scheme in schemes_breakup]
    rows = [x.values() for x in schemes_breakup]
    header = schemes_breakup[0].keys()
    print(tabulate.tabulate(rows, header, tablefmt="fancy_grid"))

    if cutie.prompt_yes_or_no('Show scheme wise break-up of eligible transactions?'):
        schemes_breakup = summary["schemes"]
        for scheme in schemes_breakup:
            eligible_purchase_transactions = scheme["transactions"]
            print(click.style(scheme['scheme'], bold=True))
            print("Total units available for LTCG tax harvesting: " + click.style(str(scheme['units']), bold=True))
            print(
                f"Approx value at NAV {scheme['nav']}: "
                + click.style(locale.currency(scheme["amount"], grouping=True), bold=True, fg="green")
            )
            print(f"Approx LTCG: " + click.style(locale.currency(scheme["ltcg"], grouping=True), bold=True, fg="green"))
            
            print("\nBreak-down: ")
            rows = [x.values() for x in eligible_purchase_transactions]
            header = eligible_purchase_transactions[0].keys()
            print(tabulate.tabulate(rows, header, tablefmt="grid"))
            print("\n")

if __name__ == "__main__":
    main(prog_name="portfolio-cli")