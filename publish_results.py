"""Build a reviewable GitHub research page from an observed Yahoo backtest."""

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
STRATEGIES = [
    "Equal weight", "Min variance: sample", "Min variance: shrinkage",
    "Min variance: factors", "Max Sharpe: shrinkage",
    "Min variance: turnover-aware", "SPY buy & hold",
]


def load_study(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    source = manifest["source"]
    if (manifest.get("mode") != "HISTORICAL" or source.get("synthetic")
            or "Yahoo Finance" not in source.get("source", "")):
        raise ValueError(f"{folder}: only observed Yahoo Finance research can be published")
    performance = pd.read_csv(folder / "performance.csv", index_col=0)
    expected = STRATEGIES[:-1] + [manifest["config"]["benchmark"] + " buy & hold"]
    if performance.empty or not set(expected).issubset(performance.index):
        raise ValueError(f"{folder}: incomplete strategy performance table")
    if not {"CAGR", "Sharpe", "Max drawdown"}.issubset(performance.columns):
        raise ValueError(f"{folder}: missing required metrics")
    net = pd.read_csv(folder / "net.csv", index_col=0, parse_dates=True)
    if net.empty or net.isna().any().any() or not set(expected).issubset(net.columns):
        raise ValueError(f"{folder}: incomplete daily portfolio returns")
    if not net.index.is_monotonic_increasing or net.index.has_duplicates:
        raise ValueError(f"{folder}: dates must be unique and ordered")
    for strategy in expected:
        actual_cagr = (1 + net[strategy]).prod() ** (252 / len(net)) - 1
        if abs(actual_cagr - performance.loc[strategy, "CAGR"]) > 1e-7:
            raise ValueError(f"{folder}: CAGR differs from daily net returns for {strategy}")
    image = folder / "figures" / "wealth_drawdown.png"
    if not image.is_file():
        raise ValueError(f"{folder}: missing historical wealth and drawdown chart")
    return manifest, performance.loc[expected], net, image


def markdown_table(frame):
    lines = ["| Strategy | Net CAGR | Net Sharpe | Max drawdown |",
             "| --- | ---: | ---: | ---: |"]
    for name, row in frame.iterrows():
        lines.append(f"| {name} | {row['CAGR']:.2%} | {row['Sharpe']:.2f} | "
                     f"{row['Max drawdown']:.2%} |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stocks", type=Path, default=ROOT / "outputs/research_v2")
    parser.add_argument("--etfs", type=Path, default=ROOT / "outputs/etf_research_v2")
    parser.add_argument("--docs", type=Path, default=ROOT / "docs")
    args = parser.parse_args(argv)
    studies = [("Stock portfolio", "stocks", args.stocks)]
    if args.etfs.is_dir():
        studies.append(("Sector ETF portfolio", "etfs", args.etfs))
    sections = [
        "# Historical research results",
        "",
        "These are observed Yahoo Finance adjusted-close backtests, with Kenneth French "
        "daily factors. Values below are computed from the net daily portfolio returns. "
        "Results are descriptive and depend on the selected universe, historical sample, "
        "execution assumptions, and transaction-cost model.",
    ]
    images = []
    for title, slug, folder in studies:
        manifest, frame, net, image = load_study(folder)
        source = manifest["source"]
        lines = [
            "", f"## {title}", "",
            f"Daily return sample: {net.index[0].date()} to {net.index[-1].date()} "
            f"({len(net):,} sessions). Data snapshot downloaded: "
            f"{source.get('downloaded_utc', 'date unavailable')}. "
            f"Trading cost: {manifest['config']['cost_bps']:g} basis points per "
            "dollar bought or sold; net returns include initial entry cost.",
            "", markdown_table(frame), "",
            f"![{title} net wealth and drawdown](assets/{slug}_wealth_drawdown.png)",
            "", "The universe was selected with hindsight; estimates, parameters, and "
            "comparisons have been inspected on this historical sample. The table "
            "does not establish prospective alpha.",
            "", f"Data hash (prices): `{source['prices_sha256']}`. "
            f"Code hash: `{manifest['code_sha256']}`.",
        ]
        sections.extend(lines)
        images.append((image, slug))
    sections.extend(["", "## Reproduce", "",
        "Install the package and run `python3 run_research.py`, then "
        "`python3 publish_results.py`. The full report and CSVs remain in "
        "`outputs/research_v2/` (and `outputs/etf_research_v2/`). "
        "See [methodology](../METHODOLOGY.md) for timing, costs, and limitations.", ""])
    assets = args.docs / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for image, slug in images:
        shutil.copy2(image, assets / f"{slug}_wealth_drawdown.png")
    destination = args.docs / "HISTORICAL_RESULTS.md"
    destination.write_text("\n".join(sections), encoding="utf-8")
    print("Published observed research page:", destination.resolve())


if __name__ == "__main__":
    main()
