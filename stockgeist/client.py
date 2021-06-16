from typing import Tuple as _Tuple
from typing import Dict as _Dict

import pandas as pd
import requests as _requests
import pandas_market_calendars as mcal
from tqdm import tqdm

from stockgeist.responses import ArticleMetricsResponse as _ArticleMetricsResponse
from stockgeist.responses import MessageMetricsResponse as _MessageMetricsResponse
from stockgeist.responses import PriceMetricsResponse as _PriceMetricsResponse
from stockgeist.responses import RankingMetricsResponse as _RankingMetricsResponse
from stockgeist.responses import TopicMetricsResponse as _TopicMetricsResponse


# from stockgeist.responses import MessageMetricsResponse as _MessageMetricsResponse
# from stockgeist.responses import MessageMetricsResponse as _MessageMetricsResponse


class StockGeistClient:
    """
    A Client class responsible for communication with StockGeist's API.
    """

    def __init__(self, token):
        self.token = token
        self.session = _requests.Session()
        self.base_url = 'https://api.stockgeist.ai/'
        self.mkt_calendar = mcal.get_calendar('NYSE').schedule(start_date='2020-01-01', end_date='2025-01-01')

    def _gen(self):
        while True:
            yield

    def _construct_query(self, endpoint_name: str, query_args: _Dict[str, object]) -> str:
        """
        Helper function for constructing API query.
        :param endpoint_name: Name of the StockGeist's REST API endpoint.
        :param query_args: Dict containing all arguments passed to REST API.
        :rtype: str
        """
        # construct query
        query = f'{self.base_url}{endpoint_name}?token={self.token}&'
        for name, value in query_args.items():
            if value is not None:
                if isinstance(value, tuple):
                    query += f'{name}={",".join(value)}&'
                else:
                    query += f'{name}={value}&'

        return query

    def get_message_metrics(self,
                            symbol: str,
                            timeframe: str = '5m',
                            filter: _Tuple[str, ...] = ('total_count', ),
                            start: str = None,
                            end: str = None) -> _MessageMetricsResponse:
        """
        Queries StockGeist's API and gets message metrics data.
        Returns :class:`MessageMetricsResponse <MessageMetricsResponse>` object.

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
        :rtype: MessageMetricsResponse
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        res = []
        for _ in tqdm(self._gen()):
            # construct query
            query = self._construct_query('time-series/message-metrics', query_args)

            # query endpoint
            res_batch = self.session.get(query).json()
            res.append(res_batch)
            first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

            if start is not None:
                # check whether all data range is fetched
                if first_timestamp == query_args['start']:
                    break
                else:
                    query_args['end'] = first_timestamp

        return _MessageMetricsResponse(res, query_args)

    def get_article_metrics(self,
                            symbol: str,
                            timeframe: str = '5m',
                            filter: _Tuple[str, ...] = ('titles',),
                            start: str = None,
                            end: str = None) -> _ArticleMetricsResponse:
        """
        Queries StockGeist's API and gets article metrics data.
        Returns :class:`ArticleMetricsResponse <ArticleMetricsResponse>` object.

        :param symbol: Stock ticker for which to retrieve data.
        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.
        :param filter: What metrics to return with the response. Possible values are: titles, title_sentiments,
            mentions, summaries, sentiment_spans, urls. For more information check https://docs.stockgeist.ai.
        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.
        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.
        :rtype: ArticleMetricsResponse
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        res = []
        for _ in tqdm(self._gen()):
            # construct query
            query = self._construct_query('time-series/article-metrics', query_args)

            # query endpoint
            res_batch = self.session.get(query).json()
            res.append(res_batch)
            first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

            if start is not None:
                # check whether all data range is fetched
                if first_timestamp == query_args['start']:
                    break
                else:
                    query_args['end'] = first_timestamp

        return _ArticleMetricsResponse(res, query_args)

    def get_price_metrics(self,
                          symbol: str,
                          timeframe: str = '5m',
                          filter: _Tuple[str, ...] = ('close',),
                          start: str = None,
                          end: str = None) -> _PriceMetricsResponse:
        """
        Queries StockGeist's API and gets price metrics data.
        Returns :class:`PriceMetricsResponse <PriceMetricsResponse>` object.

        :param symbol: Stock ticker for which to retrieve data.
        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.
        :param filter: What metrics to return with the response. Possible values are: open, high, low, close, volume.
            For more information check https://docs.stockgeist.ai.
        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.
        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.
        :rtype: PriceMetricsResponse
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        res = []
        for _ in tqdm(self._gen()):
            # construct query
            query = self._construct_query('time-series/price-metrics', query_args)

            # query endpoint
            res_batch = self.session.get(query).json()
            res.append(res_batch)

            try:
                # some data returned
                first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp'])
            except IndexError:
                # data not returned - might have encountered market holiday, weekend or non-market hours
                first_timestamp = pd.Timestamp(query_args['end']).replace(hour=23, minute=0, second=0) - pd.Timedelta(
                    days=1)

            if start is not None:
                # check whether all data range is fetched
                if first_timestamp.strftime('%Y-%m-%dT%H:%M:%S') <= query_args['start']:
                    break
                else:
                    query_args['end'] = first_timestamp.strftime('%Y-%m-%dT%H:%M:%S')

        return _PriceMetricsResponse(res, query_args)

    def get_topic_metrics(self,
                          symbol: str,
                          timeframe: str = '5m',
                          filter: _Tuple[str, ...] = ('words',),
                          start: str = None,
                          end: str = None) -> _TopicMetricsResponse:
        """
        Queries StockGeist's API and gets topic metrics data.
        Returns :class:`TopicMetricsResponse <TopicMetricsResponse>` object.

        :param symbol: Stock ticker for which to retrieve data.
        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.
        :param filter: What metrics to return with the response. Possible values are: words, scores. For more
            information check https://docs.stockgeist.ai.
        :param start: Timestamp of the earliest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.
        :param end: Timestamp of the latest data point in returned time series. Time is assumed to be in
            UTC time zone. Valid format: YYYY-mm-ddTHH:MM:SS.
        :rtype: TopicMetricsResponse
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        res = []
        for _ in tqdm(self._gen()):
            # construct query
            query = self._construct_query('time-series/topic-metrics', query_args)

            # query endpoint
            res_batch = self.session.get(query).json()
            res.append(res_batch)
            first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

            if start is not None:
                # check whether all data range is fetched
                if first_timestamp == query_args['start']:
                    break
                else:
                    query_args['end'] = first_timestamp

        return _TopicMetricsResponse(res, query_args)

    def get_ranking_metrics(self,
                            symbol: str = None,
                            timeframe: str = '5m',
                            filter: _Tuple[str, ...] = ('symbols',),
                            start: str = None,
                            end: str = None,
                            by: str = 'total_count',
                            direction: str = 'descending',
                            top: int = 5) -> _RankingMetricsResponse:
        """
        Queries StockGeist's API and gets ranking metrics data.
        Returns :class:`RankingMetricsResponse <RankingMetricsResponse>` object.

        :param symbol: Stock ticker for which to retrieve data.
        :param timeframe: Time resolution of returned data. Possible values are 5m, 1h, 1d.
        :param filter: What metrics to return with the response. Possible values are: words, scores. For more
            information check https://docs.stockgeist.ai.
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
        :rtype: RankingMetricsResponse
        """

        # get query arguments
        query_args = locals()
        query_args.pop('self')

        res = []
        for _ in tqdm(self._gen()):
            # construct query
            query = self._construct_query('time-series/ranking-metrics', query_args)

            # query endpoint
            res_batch = self.session.get(query).json()
            res.append(res_batch)
            first_timestamp = pd.Timestamp(res_batch['body'][0]['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')

            if start is not None:
                # check whether all data range is fetched
                if first_timestamp == query_args['start']:
                    break
                else:
                    query_args['end'] = first_timestamp

        return _RankingMetricsResponse(res, query_args)
