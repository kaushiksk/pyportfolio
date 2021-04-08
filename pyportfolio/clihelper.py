from decimal import Decimal
import locale
from collections import defaultdict

import click
import cutie
import tabulate

from .portfolio import Portfolio


def ltcg_tax_harvesting_summary(portfolio: Portfolio):
    summary = portfolio.ltcg_tax_harvesting_summary()

    print(
        click.style("\nTotal LTCG Tax that can be harvested this FY: ", bold=True)
        + click.style(locale.currency(summary["total_ltcg"], grouping=True), bold=True, fg="green")
    )
    print(
        click.style("Total value of units to be sold and bought: ", bold=True)
        + click.style(
            locale.currency(summary["total_amount"], grouping=True),
            bold=True,
            fg="green",
        )
    )
    print(
        click.style(
            """Note: Buy and sell the following units on the same day to avoid losses due to NAV
            fluctuations""",
            bold=True,
            fg="yellow",
        )
    )

    schemes_breakup = summary["schemes"]
    schemes_breakup = [
        {k: v for k, v in scheme.items() if k != "transactions"} for scheme in schemes_breakup
    ]
    rows = [x.values() for x in schemes_breakup]
    header = schemes_breakup[0].keys()
    print(tabulate.tabulate(rows, header, tablefmt="fancy_grid"))

    if cutie.prompt_yes_or_no("Show scheme wise break-up of eligible transactions?"):
        schemes_breakup = summary["schemes"]
        for scheme in schemes_breakup:
            eligible_purchase_transactions = scheme["transactions"]
            print(click.style(scheme["scheme"], bold=True))
            print(
                "Total units available for LTCG tax harvesting: "
                + click.style(str(scheme["units"]), bold=True)
            )
            print(
                f"Approx value at NAV {scheme['nav']}: "
                + click.style(
                    locale.currency(scheme["amount"], grouping=True),
                    bold=True,
                    fg="green",
                )
            )
            print(
                "Approx LTCG: "
                + click.style(
                    locale.currency(scheme["ltcg"], grouping=True),
                    bold=True,
                    fg="green",
                )
            )

            print("\nBreak-down: ")
            rows = [x.values() for x in eligible_purchase_transactions]
            header = eligible_purchase_transactions[0].keys()
            print(tabulate.tabulate(rows, header, tablefmt="grid"))
            print("\n")


def valuation_summary(portfolio: Portfolio):
    summary = portfolio.get_valuation_summary()
    debt_summary = summary["debt_valuation"]
    equity_summary = summary["equity_valuation"]

    total_valuation = summary["valuation"]
    debt_percentage = (debt_summary["valuation"] * 100) / total_valuation
    equity_percentage = (equity_summary["valuation"] * 100) / total_valuation

    print(
        click.style("\nValuation: ", bold=True)
        + click.style(locale.currency(total_valuation, grouping=True), bold=True, fg="green")
    )
    print(click.style("Debt  : " + " {0:.2f}%".format(debt_percentage), bold=True))
    print(click.style("Equity: " + " {0:.2f}%".format(equity_percentage), bold=True))

    if cutie.prompt_yes_or_no("Show subtype breakup for debt and equity?"):
        print()

        def print_subtypes_summary(summary, title):
            subtypes = defaultdict(Decimal)
            subtype_counts = defaultdict(int)
            for scheme in summary["schemes"]:
                subtypes[scheme["subtype"]] += scheme["valuation"]
                subtype_counts[scheme["subtype"]] += 1

            subtypes = sorted(subtypes.items(), key=lambda x: x[1], reverse=True)

            valuation = summary["valuation"]
            valuation_percentage = (valuation * 100) / total_valuation

            print(
                click.style(
                    "{0:<6} - ".format(title)
                    + click.style(locale.currency(valuation, grouping=True), fg="green")
                    + " ({0:.2f}%)".format(valuation_percentage),
                    bold=True,
                )
            )
            for subtype, subtype_valuation in subtypes:
                print(
                    click.style(
                        " {0:<25} - {1} ({2:.2f}%)".format(
                            subtype + " ({})".format(subtype_counts[subtype]),
                            click.style(
                                locale.currency(subtype_valuation, grouping=True),
                                fg="green",
                            ),
                            (subtype_valuation * 100) / valuation,
                        ),
                        bold=True,
                    )
                )

            print()

        print_subtypes_summary(debt_summary, "Debt")
        print_subtypes_summary(equity_summary, "Equity")
