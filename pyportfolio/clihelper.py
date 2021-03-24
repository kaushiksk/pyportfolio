from portfolio import Portfolio
import click 
import tabulate
import cutie 
import locale

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