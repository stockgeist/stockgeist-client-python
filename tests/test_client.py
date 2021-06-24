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
    # get actual result
    query_args = {}
    symbols = api_connection._fetch_data_snapshot('snapshot/symbols', query_args)[0]['body']['symbols']['stocks']

    assert len(symbols) > 2000 and isinstance(symbols, list) and isinstance(symbols[0], str)


def test_client_fetch_data_fundamentals(api_connection):
    # fundamental metrics to be found
    metrics = (
        'book_to_sh', 'rsi_14', 'eps_next_y', '52w_range', 'eps_ttm', 'roa', 'dividend_perc', 'beta', 'oper_margin',
        'p_to_fcf', 'eps_this_y', 'inst_trans', 'p_to_b', 'rel_volume', 'perf_quarter', 'sales', 'roi', 'inst_own',
        'index', 'perf_ytd', 'eps_next_q', 'avg_volume', 'dividend', 'p_to_c', 'insider_trans', 'short_float',
        'country', 'income', 'perf_year', 'perf_half_y', 'atr', 'sales_past_5_y', '52w_high_diff', 'gross_margin',
        'peg', 'perf_month', 'volatility', 'cash_to_sh', 'short_ratio', 'eps_past_5_y', 'debt_to_eq', 'sector',
        'industry', 'eps_q_to_q', 'p_to_e', 'prev_close', 'volume', 'sma_20_diff', 'p_to_s', 'price', 'current_ratio',
        'forward_p_to_e', 'sma_50_diff', 'employees', 'profit_margin', 'sma_200_diff', 'sales_q_to_q', 'earnings',
        'perf_week', 'quick_ratio', 'payout', 'eps_next_5_y', 'recom', 'roe', 'shs_outstand', 'description',
        '52w_low_diff', 'company_name', 'target_price', 'market_cap', 'optionable', 'shortable', 'insider_own',
        'shs_float', 'lt_debt_to_eq', 'timestamp', 'symbol'
    )

    # get actual result
    query_args = {
        'symbol': 'AAPL',
        'filter': metrics
    }
    fundamentals = api_connection._fetch_data_snapshot('snapshot/fundamentals', query_args)[0]['body'].keys()

    assert set(metrics) == set(fundamentals)

