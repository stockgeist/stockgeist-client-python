import requests
from typing import Tuple
from responses import MessageMetricsResponse, ArticleMetricsResponse, PriceMetricsResponse, TopicMetricsResponse, \
    RankingMetricsResponse, SymbolsResponse, FundamentalsResponse


class StockGeistClient:
    """
    A Client class responsible for communication with StockGeist's API.
    """

    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.base_url = 'https://api.stockgeist.ai/'

    def get_message_metrics(self,
                            symbol: str,
                            timeframe: str = '5m',
                            filter: Tuple[str, ...] = ('total_count', ),
                            start: str = None,
                            end: str = None) -> MessageMetricsResponse:
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

        # construct query
        query = f'{self.base_url}time-series/message-metrics?token={self.token}&'
        if symbol is not None:
            query += f'symbol={symbol}&'
        if timeframe is not None:
            query += f'timeframe={timeframe}&'
        if filter is not None:
            query += f'filter={",".join(filter)}&'
        if start is not None:
            query += f'start={start}&'
        if end is not None:
            query += f'end={end}'

        # query endpoint
        res = self.session.get(query).json()

        return MessageMetricsResponse(res, query_args)

    def get_article_metrics(self,
                            symbol: str,
                            timeframe: str = '5m',
                            filter: Tuple[str, ...] = ('titles',),
                            start: str = None,
                            end: str = None) -> ArticleMetricsResponse:
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

        # construct query
        query = f'{self.base_url}time-series/article-metrics?token={self.token}&'
        if symbol is not None:
            query += f'symbol={symbol}&'
        if timeframe is not None:
            query += f'timeframe={timeframe}&'
        if filter is not None:
            query += f'filter={",".join(filter)}&'
        if start is not None:
            query += f'start={start}&'
        if end is not None:
            query += f'end={end}'

        # query endpoint
        res = self.session.get(query).json()

        return ArticleMetricsResponse(res, query_args)

    def get_price_metrics(self,
                          symbol: str,
                          timeframe: str = '5m',
                          filter: Tuple[str, ...] = ('close',),
                          start: str = None,
                          end: str = None) -> PriceMetricsResponse:
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

        # construct query
        query = f'{self.base_url}time-series/price-metrics?token={self.token}&'
        if symbol is not None:
            query += f'symbol={symbol}&'
        if timeframe is not None:
            query += f'timeframe={timeframe}&'
        if filter is not None:
            query += f'filter={",".join(filter)}&'
        if start is not None:
            query += f'start={start}&'
        if end is not None:
            query += f'end={end}'

        # query endpoint
        res = self.session.get(query).json()

        return PriceMetricsResponse(res, query_args)

    def get_topic_metrics(self,
                          symbol: str,
                          timeframe: str = '5m',
                          filter: Tuple[str, ...] = ('words',),
                          start: str = None,
                          end: str = None) -> TopicMetricsResponse:
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

        # construct query
        query = f'{self.base_url}time-series/topic-metrics?token={self.token}&'
        if symbol is not None:
            query += f'symbol={symbol}&'
        if timeframe is not None:
            query += f'timeframe={timeframe}&'
        if filter is not None:
            query += f'filter={",".join(filter)}&'
        if start is not None:
            query += f'start={start}&'
        if end is not None:
            query += f'end={end}'

        # query endpoint
        res = self.session.get(query).json()

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

        # construct query
        query = f'{self.base_url}time-series/ranking-metrics?token={self.token}&'
        if symbol is not None:
            query += f'symbol={symbol}&'
        if timeframe is not None:
            query += f'timeframe={timeframe}&'
        if filter is not None:
            query += f'filter={",".join(filter)}&'
        if start is not None:
            query += f'start={start}&'
        if end is not None:
            query += f'end={end}'

        # query endpoint
        res = self.session.get(query).json()

        return RankingMetricsResponse(res, query_args)


if __name__ == '__main__':
    client = StockGeistClient('39f3fe9b-2759-487f-9c45-9e2cefa87840')
    response = client.get_topic_metrics(symbol='AAPL')

    print(response.data)