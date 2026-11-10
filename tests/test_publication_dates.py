import pandas as pd
import pytest
from publish_results import load_study
from test_publication import sample_study

@pytest.mark.parametrize('value',['not-a-date',''])
def test_invalid_daily_dates_have_clear_validation_errors(tmp_path,value):
    folder=sample_study(tmp_path)
    frame=pd.read_csv(folder/'net.csv',index_col=0)
    labels=frame.index.tolist();labels[0]=value;frame.index=labels
    frame.to_csv(folder/'net.csv')
    with pytest.raises(ValueError,match='valid daily return dates'):
        load_study(folder)
