import os

from stockgeist import StockGeistClient
from dotenv import load_dotenv
import pytest
import pickle

load_dotenv()


@pytest.fixture(scope="session")
def api_token():
    return os.getenv('STOCKGEIST_API_TOKEN')


@pytest.fixture(scope="session")
def api_connection(api_token):
    return StockGeistClient(api_token)


def test_client_created_successfully():
    client = StockGeistClient('test-token')
    assert isinstance(client, StockGeistClient)


def test_client_construct_query(api_token, api_connection):
    # expected result
    query_test_case = f'https://api.stockgeist.ai/time-series/message-metrics?token={api_token}&' \
                      f'symbol=AAPL&' \
                      f'timeframe=1h&' \
                      f'filter=total_count,ma_diff&' \
                      f'start=2021-06-20T00:05:00&' \
                      f'end=2021-06-21T01:05:00'

    # actual result from tested function
    query_result = api_connection._construct_query(
        endpoint_name='time-series/message-metrics',
        query_args={
            'symbol': 'AAPL',
            'timeframe': '1h',
            'filter': ('total_count', 'ma_diff'),
            'start': '2021-06-20T00:05:00',
            'end': '2021-06-21T01:05:00'
        }
    )

    assert query_test_case == query_result


@pytest.mark.parametrize('timeframe, start, end',
                         [('5m', '2021-06-20T00:05:00', '2021-06-20T15:40:00'),
                          ('1h', '2021-06-18T00:00:00', '2021-06-20T03:00:00'),
                          ('1d', '2021-06-18T00:00:00', '2021-06-22T00:00:00')])
def test_client_fetch_data_message_metrics(api_connection, timeframe, start, end):
    # load expected result
    test_case = pickle.load(open(f'tests/data/message-metrics/TSLA-{timeframe}-all-metrics.pkl', 'rb'))
    test_case = [entry['body'] for entry in test_case]

    # get actual result
    query_args = {'symbol': 'TSLA',
                  'timeframe': timeframe,
                  'filter': ('inf_positive_count', 'inf_neutral_count', 'inf_negative_count', 'inf_total_count',
                             'em_positive_count', 'em_neutral_count', 'em_negative_count', 'em_total_count',
                             'total_count', 'pos_index', 'msg_ratio', 'ma', 'ma_diff', 'std_dev', 'ma_count_change'),
                  'start': start,
                  'end': end}
    actual_result = api_connection._fetch_data_time_series('time-series/message-metrics', query_args)
    actual_result = [entry['body'] for entry in actual_result]

    assert test_case == actual_result


@pytest.mark.parametrize('timeframe, start, end',
                         [('5m', '2021-05-20T00:05:00', '2021-05-20T15:40:00'),
                          ('1h', '2021-05-18T00:00:00', '2021-05-20T03:00:00'),
                          ('1d', '2021-05-18T00:00:00', '2021-05-22T00:00:00')])
def test_client_fetch_data_article_metrics(api_connection, timeframe, start, end):
    # load expected result
    test_case = pickle.load(open(f'tests/data/article-metrics/NVDA-{timeframe}-all-metrics.pkl', 'rb'))
    test_case = [entry['body'] for entry in test_case]

    # get actual result
    query_args = {'symbol': 'NVDA',
                  'timeframe': timeframe,
                  'filter': ('titles', 'title_sentiments', 'mentions', 'summaries', 'sentiment_spans', 'urls'),
                  'start': start,
                  'end': end}
    actual_result = api_connection._fetch_data_time_series('time-series/article-metrics', query_args)
    actual_result = [entry['body'] for entry in actual_result]

    assert test_case == actual_result


@pytest.mark.parametrize('timeframe, start, end',
                         [('5m', '2021-04-19T00:05:00', '2021-04-20T15:40:00'),
                          ('1h', '2021-05-18T00:00:00', '2021-05-20T03:00:00'),
                          ('1d', '2021-06-18T00:00:00', '2021-06-22T00:00:00')])
def test_client_fetch_data_price_metrics(api_connection, timeframe, start, end):
    # load expected result
    test_case = pickle.load(open(f'tests/data/price-metrics/GILD-{timeframe}-all-metrics.pkl', 'rb'))
    test_case = [entry['body'] for entry in test_case]

    # get actual result
    query_args = {'symbol': 'GILD',
                  'timeframe': timeframe,
                  'filter': ('open', 'high', 'low', 'close', 'volume'),
                  'start': start,
                  'end': end}
    actual_result = api_connection._fetch_data_time_series('time-series/price-metrics', query_args)
    actual_result = [entry['body'] for entry in actual_result]

    assert test_case == actual_result


@pytest.mark.parametrize('timeframe, start, end',
                         [('5m', '2021-04-13T00:05:00', '2021-04-13T15:40:00'),
                          ('1h', '2021-05-10T00:00:00', '2021-05-12T03:00:00'),
                          ('1d', '2021-06-15T00:00:00', '2021-06-19T00:00:00')])
def test_client_fetch_data_topic_metrics(api_connection, timeframe, start, end):
    # load expected result
    test_case = pickle.load(open(f'tests/data/topic-metrics/AAPL-{timeframe}-all-metrics.pkl', 'rb'))
    test_case = [entry['body'] for entry in test_case]

    # get actual result
    query_args = {'symbol': 'AAPL',
                  'timeframe': timeframe,
                  'filter': ('words', 'scores'),
                  'start': start,
                  'end': end}
    actual_result = api_connection._fetch_data_time_series('time-series/topic-metrics', query_args)
    actual_result = [entry['body'] for entry in actual_result]

    assert test_case == actual_result


@pytest.mark.parametrize('symbol, timeframe, start, end',
                         [(None, '5m', '2021-03-13T00:05:00', '2021-03-13T15:40:00'),
                          (None, '1h', '2021-05-02T00:00:00', '2021-05-04T03:00:00'),
                          (None, '1d', '2021-06-01T00:00:00', '2021-06-05T00:00:00'),
                          ('A', '5m', '2021-03-13T00:05:00', '2021-03-13T15:40:00'),
                          ('A', '1h', '2021-05-02T00:00:00', '2021-05-04T03:00:00'),
                          ('A', '1d', '2021-06-01T00:00:00', '2021-06-05T00:00:00')
                          ])
def test_client_fetch_data_ranking_metrics(api_connection, symbol, timeframe, start, end):
    # load expected result
    test_case = pickle.load(open(f'tests/data/ranking-metrics/{symbol}-{timeframe}-all-metrics.pkl', 'rb'))
    test_case = [entry['body'] for entry in test_case]

    # get actual result
    query_args = {'symbol': symbol,
                  'timeframe': timeframe,
                  'filter': ('symbols', 'scores', 'score_changes', 'values'),
                  'start': start,
                  'end': end}
    actual_result = api_connection._fetch_data_time_series('time-series/ranking-metrics', query_args)
    actual_result = [entry['body'] for entry in actual_result]

    assert test_case == actual_result


def test_client_fetch_data_symbols(api_connection):
    pass


def test_client_fetch_data_fundamentals(api_connection):
    pass