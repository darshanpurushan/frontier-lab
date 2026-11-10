import pandas as pd
import pytest

from publish_results import load_study, main
from test_publication import sample_study


def set_losses(folder, losses):
    net = pd.read_csv(folder / "net.csv", index_col=0)
    net.iloc[:len(losses), 0] = losses
    net.to_csv(folder / "net.csv")
    performance = pd.read_csv(folder / "performance.csv", index_col=0)
    performance.loc["Equal weight", "CAGR"] = (1 + net["Equal weight"]).prod() ** (252 / len(net)) - 1
    performance.to_csv(folder / "performance.csv")


@pytest.mark.parametrize("loss", [-1.01, -2.0])
def test_returns_below_total_loss_cannot_be_published(tmp_path, loss):
    folder = sample_study(tmp_path)
    # Two impossible losses yield positive compounded wealth, bypassing
    # checks based only on the endpoint growth rate.
    set_losses(folder, [loss, loss])
    docs = tmp_path / "docs"
    docs.mkdir()
    report = docs / "HISTORICAL_RESULTS.md"
    report.write_text("existing report")
    with pytest.raises(ValueError, match="below -100%"):
        main(["--stocks", str(folder), "--etfs", str(tmp_path / "missing"),
              "--docs", str(docs)])
    assert report.read_text() == "existing report"
    assert not (docs / "assets").exists()


def test_exact_total_loss_remains_a_valid_return(tmp_path):
    folder = sample_study(tmp_path)
    set_losses(folder, [-1.0])
    _, performance, _, _ = load_study(folder)
    assert performance.loc["Equal weight", "CAGR"] == -1.0
