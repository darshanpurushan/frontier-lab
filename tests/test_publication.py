import json

import pandas as pd
import pytest

from publish_results import load_study, main


def sample_study(tmp_path, mode="HISTORICAL"):
    folder = tmp_path / "study"
    (folder / "figures").mkdir(parents=True)
    dates = pd.bdate_range("2021-01-01", periods=50)
    names = ["Equal weight", "Min variance: sample", "Min variance: shrinkage",
             "Min variance: factors", "Max Sharpe: shrinkage",
             "Min variance: turnover-aware", "SPY buy & hold"]
    returns = pd.DataFrame(.001, index=dates, columns=names)
    returns.to_csv(folder / "net.csv")
    cagr = (1.001 ** 252) - 1
    pd.DataFrame({"CAGR": cagr, "Sharpe": 1.0, "Max drawdown": -.1},
                 index=names).to_csv(folder / "performance.csv")
    (folder / "figures/wealth_drawdown.png").write_bytes(b"fixture")
    (folder / "manifest.json").write_text(json.dumps({
        "mode": mode,
        "config": {"benchmark": "SPY", "cost_bps": 10},
        "source": {"source": "Yahoo Finance adjusted close; Kenneth French daily factors",
                   "prices_sha256": "abc", "downloaded_utc": "2021-12-31T00:00:00Z"},
        "code_sha256": "123"}))
    return folder


def test_published_summary_requires_observed_returns(tmp_path):
    folder = sample_study(tmp_path)
    destination = tmp_path / "docs"
    main(["--stocks", str(folder), "--etfs", str(tmp_path / "missing"),
          "--docs", str(destination)])
    document = (destination / "HISTORICAL_RESULTS.md").read_text()
    assert "Stock portfolio" in document
    assert "Yahoo Finance" in document
    assert "SPY buy & hold" in document
    assert (destination / "assets/stocks_wealth_drawdown.png").exists()


def test_demo_cannot_be_published(tmp_path):
    folder = sample_study(tmp_path, mode="SYNTHETIC")
    with pytest.raises(ValueError, match="only observed"):
        load_study(folder)


def test_inconsistent_daily_returns_cannot_be_published(tmp_path):
    folder = sample_study(tmp_path)
    table = pd.read_csv(folder / "performance.csv", index_col=0)
    table.loc["Equal weight", "CAGR"] += .1
    table.to_csv(folder / "performance.csv")
    with pytest.raises(ValueError, match="CAGR differs"):
        load_study(folder)
