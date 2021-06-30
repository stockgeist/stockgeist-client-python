from stockgeist.responses import _Response, MessageMetricsResponse, ArticleMetricsResponse, PriceMetricsResponse
import pickle
import pandas as pd
import pytest


def test_base_response_created_successfully():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    assert isinstance(base_response, _Response)


def test_base_response_status_codes():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    assert isinstance(base_response.status_codes, list) and base_response.status_codes[0] == 200


def test_base_response_messages():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    assert isinstance(base_response.messages, list) and base_response.messages[0] == 'OK'


def test_base_response_credits():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    assert isinstance(base_response.credits, list) and base_response.credits[0] == 99314258


def test_base_response_server_timestamps():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    assert isinstance(base_response.server_timestamps, list) \
           and base_response.server_timestamps[0] == '2021-06-23 10:20:12.617781+00:00'


def test_base_response_dataframe():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    assert isinstance(base_response.as_dataframe, pd.DataFrame) \
           and str(base_response.as_dataframe.index[0]) == '2021-06-20 00:05:00+00:00'


@pytest.mark.parametrize('to_parse, test_configuration',
                         [('total_count+ma_diff+ma', 1),
                          ('total_count+ma_diff+ma+bad_metric', 2),
                          ('total_count+ma_diff+ma+not_downloaded', 3)])
def test_base_response_validate_metrics(to_parse, test_configuration):
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    base_response = _Response(test_data)

    # get actual result
    available_metrics = ['inf_positive_count', 'inf_neutral_count', 'inf_negative_count', 'inf_total_count',
                         'em_positive_count', 'em_neutral_count', 'em_negative_count', 'em_total_count',
                         'total_count', 'pos_index', 'msg_ratio', 'ma', 'ma_diff', 'std_dev', 'ma_count_change',
                         'not_downloaded']

    if test_configuration == 1:
        res = base_response._validate_metrics(to_parse, available_metrics)
        assert res == ['total_count', 'ma_diff', 'ma']
    elif test_configuration == 2:
        with pytest.raises(Exception, match='bad_metric is not a valid metric'):
            res = base_response._validate_metrics(to_parse, available_metrics)
    elif test_configuration == 3:
        with pytest.raises(Exception, match='not_downloaded metric not downloaded'):
            res = base_response._validate_metrics(to_parse, available_metrics)


def test_base_response_plot_simple():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    test_fig = pickle.load(open(f'tests/data/message-metrics/TSLA-fig.pkl', 'rb'))
    base_response = _Response(test_data)

    # get actual result
    args = {
        'title': f'TSLA Message Metrics',
        'metric_names': ['total_count', 'ma_diff', 'ma', 'pos_index'],
        'right_y_metric_names': ['pos_index', 'msg_ratio', 'ma_count_change']
    }
    res = base_response._plot_simple(**args)

    assert res == test_fig


def test_message_metrics_response_created_successfully():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    query_args = {'symbol': 'TSLA',
                  'timeframe': '5m',
                  'filter': ('inf_positive_count', 'inf_neutral_count', 'inf_negative_count', 'inf_total_count',
                             'em_positive_count', 'em_neutral_count', 'em_negative_count', 'em_total_count',
                             'total_count', 'pos_index', 'msg_ratio', 'ma', 'ma_diff', 'std_dev', 'ma_count_change'),
                  'start': '2021-06-20T00:05:00',
                  'end': '2021-06-20T15:40:00'}
    message_metrics_response = MessageMetricsResponse(test_data, query_args)

    assert isinstance(message_metrics_response, MessageMetricsResponse)


def test_message_metrics_response_visualize():
    # load test data
    test_data = pickle.load(open(f'tests/data/message-metrics/TSLA-5m-all-metrics.pkl', 'rb'))
    test_fig = pickle.load(open(f'tests/data/message-metrics/TSLA-fig.pkl', 'rb'))
    query_args = {'symbol': 'TSLA',
                  'timeframe': '5m',
                  'filter': ('inf_positive_count', 'inf_neutral_count', 'inf_negative_count', 'inf_total_count',
                             'em_positive_count', 'em_neutral_count', 'em_negative_count', 'em_total_count',
                             'total_count', 'pos_index', 'msg_ratio', 'ma', 'ma_diff', 'std_dev', 'ma_count_change'),
                  'start': '2021-06-20T00:05:00',
                  'end': '2021-06-20T15:40:00'}
    message_metrics_response = MessageMetricsResponse(test_data, query_args)

    assert message_metrics_response.visualize('total_count+ma_diff+ma+pos_index', False) == test_fig


def test_article_metrics_response_created_successfully():
    # load test data
    test_data = pickle.load(open(f'tests/data/article-metrics/NVDA-5m-all-metrics.pkl', 'rb'))
    query_args = {'symbol': 'NVDA',
                  'timeframe': '5m',
                  'filter': ('titles', 'title_sentiments', 'mentions', 'summaries', 'sentiment_spans', 'urls'),
                  'start': '2021-05-20T00:05:00',
                  'end': '2021-05-20T15:40:00'}
    article_metrics_response = ArticleMetricsResponse(test_data, query_args)

    assert isinstance(article_metrics_response, ArticleMetricsResponse)


def test_article_metrics_response_visualize():
    # load test data
    test_data = pickle.load(open(f'tests/data/article-metrics/NVDA-5m-all-metrics.pkl', 'rb'))
    test_fig = pickle.load(open(f'tests/data/article-metrics/NVDA-fig.pkl', 'rb'))
    query_args = {'symbol': 'NVDA',
                  'timeframe': '5m',
                  'filter': ('titles', 'title_sentiments', 'mentions', 'summaries', 'sentiment_spans', 'urls'),
                  'start': '2021-05-20T00:05:00',
                  'end': '2021-05-20T15:40:00'}
    article_metrics_response = ArticleMetricsResponse(test_data, query_args)

    assert article_metrics_response.visualize('titles+mentions+title_sentiments', False) == test_fig
