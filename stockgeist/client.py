from typing import Tuple, Dict, List

import pandas as pd
import requests
from tqdm import tqdm

from stockgeist.responses import ArticleMetricsResponse, MessageMetricsResponse, PriceMetricsResponse, \
    RankingMetricsResponse, TopicMetricsResponse, SymbolsResponse, FundamentalsResponse


class StockGeistClient:
    """
    A Client class responsible for communication with StockGeist's API.
    """

    def __init__(self, token):
        self._token = token
        self._session = requests.Session()
        self._base_url = 'https://api.stockgeist.ai/'

    def _gen(self):
        while True:
            yield

    def _construct_query(self, endpoint_name: str, query_args: Dict[str, object]) -> str:
        """
        Helper function for constructing API query.

        :param endpoint_name: Name of the StockGeist's REST API endpoint.

        :param query_args: Dict containing all arguments passed to REST API.

        :return: REST API query string.
        """

        # construct query
        query = f'{self._base_url}{endpoint_name}?token={self._token}&'
        for name, value in query_args.items():
            if value is not None:
                if isinstance(value, tuple):
                    query += f'{name}={",".join(value)}&'
                else:
                    query += f'{name}={value}&'
        query = query.strip('&')

        return query

    def _fetch_data_time_series(self, endpoint_name: str, query_args: Dict) -> List[Dict]:
        """
        Fetch data from time series endpoints of REST API.

        :param endpoint_name: Name of the StockGeist's REST API endpoint.

        :param query_args: Dict containing all arguments passed to REST API.

        :return: list of batches of data returned by REST API.
        """

        res = []
        for _ in tqdm(self._gen()):
            # construct query
            query = self._construct_query(endpoint_name, query_args)

            # query endpoint
            res_batch = self._session.get(query).json()
            res.append(res_batch)

            # check response
            if res_batch['metadata']['status_code'] != 200:
                return res

            if endpoint_name == 'time-series/price-metrics':
                try:
                    # some data returned
                    first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp'])
                except IndexError:
                    # data not returned - might have encountered market holiday, weekend or non-market hours
                    first_timestamp = pd.Timestamp(query_args['end']).replace(hour=23, minute=0,
                                                                              second=0) - pd.Timedelta(
                        days=1)

                if query_args['start'] is not None:
                    # check whether all data range is fetched
                    if first_timestamp.strftime('%Y-%m-%dT%H:%M:%S') <= query_args['start']:
                        break
                    else:
                        query_args['end'] = first_timestamp.strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    break
            else:
                first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

                if query_args['start'] is not None:
                    # check whether all data range is fetched
                    if first_timestamp == query_args['start']:
                        break
                    else:
                        query_args['end'] = first_timestamp
                else:
                    break

        return res

    def _fetch_data_snapshot(self, endpoint_name: str, query_args: Dict) -> List[Dict]:
        """
        Fetch data from snapshot endpoints of REST API.

        :param endpoint_name: Name of the StockGeist's REST API endpoint.

        :param query_args: Dict containing all arguments passed to REST API.

        :return: list of batches of data returned by REST API.
        """

        # construct query
        query = self._construct_query(endpoint_name, query_args)

        # query endpoint
        res = self._session.get(query).json()

        return [res]

    def get_credits(self):
        """
        Queries StockGeist's API and gets the number of credits available for given token.
        """

        # get data
        res = self._fetch_data_snapshot('snapshot/credits', {})[0]
        credits = res['metadata']['credits']

        return credits

    def get_message_metrics(self,
                            symbol: str,
                            timeframe: str = '5m',
                            filter: Tuple[str, ...] = ('total_count', ),
                            start: str = None,
                            end: str = None) -> MessageMetricsResponse:
        """
        Queries StockGeist's API and gets message metrics data.

        :param symbol: Stock ticker for which to retrieve data.

        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.

        :param filter: What metrics to return with the response. Possible values are: inf_positive_count,
            inf_neutral_count, inf_negative_count, inf_total_count, em_positive_count, em_neutral_count,
            em_negative_count, em_total_count, total_count, pos_index, msg_ratio, ma, ma_diff, std_dev,
            ma_count_change. For more information check https://docs.stockgeist.ai.

        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :return: MessageMetricsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_time_series('time-series/message-metrics', query_args)

        return MessageMetricsResponse(res, query_args)

    def get_article_metrics(self,
                            symbol: str,
                            timeframe: str = '5m',
                            filter: Tuple[str, ...] = ('titles',),
                            start: str = None,
                            end: str = None) -> ArticleMetricsResponse:
        """
        Queries StockGeist's API and gets article metrics data.

        :param symbol: Stock ticker for which to retrieve data.

        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.

        :param filter: What metrics to return with the response. Possible values are: titles, title_sentiments,
            mentions, summaries, sentiment_spans, urls. For more information check https://docs.stockgeist.ai.

        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :return: ArticleMetricsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_time_series('time-series/article-metrics', query_args)

        return ArticleMetricsResponse(res, query_args)

    def get_price_metrics(self,
                          symbol: str,
                          timeframe: str = '5m',
                          filter: Tuple[str, ...] = ('close',),
                          start: str = None,
                          end: str = None) -> PriceMetricsResponse:
        """
        Queries StockGeist's API and gets price metrics data.

        :param symbol: Stock ticker for which to retrieve data.

        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.

        :param filter: What metrics to return with the response. Possible values are: open, high, low, close, volume.
            For more information check https://docs.stockgeist.ai.

        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :return: PriceMetricsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_time_series('time-series/price-metrics', query_args)

        return PriceMetricsResponse(res, query_args)

    def get_topic_metrics(self,
                          symbol: str,
                          timeframe: str = '5m',
                          filter: Tuple[str, ...] = ('words',),
                          start: str = None,
                          end: str = None) -> TopicMetricsResponse:
        """
        Queries StockGeist's API and gets topic metrics data.

        :param symbol: Stock ticker for which to retrieve data.

        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.

        :param filter: What metrics to return with the response. Possible values are: words, scores. For more
            information check https://docs.stockgeist.ai.

        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :return: TopicMetricsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_time_series('time-series/topic-metrics', query_args)

        return TopicMetricsResponse(res, query_args)

    def get_ranking_metrics(self,
                            symbol: str = None,
                            timeframe: str = '5m',
                            filter: Tuple[str, ...] = ('symbols',),
                            start: str = None,
                            end: str = None,
                            by: str = 'total_count',
                            direction: str = 'descending',
                            top: int = 5) -> RankingMetricsResponse:
        """
        Queries StockGeist's API and gets ranking metrics data.

        :param symbol: Stock ticker for which to retrieve data.

        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.

        :param filter: What metrics to return with the response. Possible values are: symbols, scores, score_changes,
            values. For more information check https://docs.stockgeist.ai.

        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.

        :param by: Select message metric by which stock ranking is produced. Possible values are: inf_positive_count,
            inf_neutral_count, inf_negative_count, inf_total_count, em_positive_count, em_neutral_count,
            em_negative_count, em_total_count, total_count, pos_index, msg_ratio, ma, ma_diff, std_dev,
            ma_count_change.

        :param direction: Ranking direction: descending/ascending leaves stock with largest/smallest metric
            value at the top.

        :param top: Number of top stocks to return.

        :return: RankingMetricsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_time_series('time-series/ranking-metrics', query_args)

        return RankingMetricsResponse(res, query_args)

    def get_symbols(self) -> SymbolsResponse:
        """
        Queries StockGeist's API and gets all available symbols.

        :return: SymbolsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_snapshot('snapshot/symbols', query_args)

        return SymbolsResponse(res, query_args)

    def get_fundamentals(self,
                         symbol: str = None,
                         filter: Tuple[str, ...] = ('market_cap',)) -> FundamentalsResponse:
        """
        Queries StockGeist's API and gets fundamentals data.

        :param symbol: Stock ticker for which to retrieve data.h, 1d.

        :param filter: What metrics to return with the response. Possible values are: ``book_to_sh``, ``rsi_14``,
            ``eps_next_y``,
            52w_range, eps_ttm, roa, dividend_perc, beta, oper_margin, p_to_fcf, eps_this_y, inst_trans, p_to_b,
            rel_volume, perf_quarter, sales, roi, inst_own, index, perf_ytd, eps_next_q, avg_volume, dividend, p_to_c,
            insider_trans, short_float, country, income, perf_year, perf_half_y, atr, sales_past_5_y, 52w_high_diff,
            gross_margin, peg, perf_month, volatility, cash_to_sh, short_ratio, eps_past_5_y, debt_to_eq, sector,
            industry, eps_q_to_q, p_to_e, prev_close, volume, sma_20_diff, p_to_s, price, current_ratio, forward_p_to_e,
            sma_50_diff, employees, profit_margin, sma_200_diff, sales_q_to_q, earnings, perf_week, quick_ratio, payout,
            eps_next_5_y, recom, roe, shs_outstand, description, 52w_low_diff, company_name, target_price, market_cap,
            optionable, shortable, insider_own, shs_float, lt_debt_to_eq. For more information check
            https://docs.stockgeist.ai.

        :return: FundamentalsResponse object.
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        # get data
        res = self._fetch_data_snapshot('snapshot/fundamentals', query_args)

        return FundamentalsResponse(res, query_args)
