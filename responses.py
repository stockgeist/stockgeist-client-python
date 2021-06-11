from typing import Dict, List


class Response:
    """
    Base class for all response objects returned as endpoint-querying results.
    """

    def __init__(self, res: Dict):
        self.status_code = res['metadata']['status_code']
        self.message = res['metadata']['message']
        self.credits = res['metadata']['credits'] if 'credits' in res['metadata'] else None
        self.server_timestamp = res['metadata']['server_timestamp']
        self.raw_data = res['body']
        self._convert_raw_data_to_list()

    def _convert_raw_data_to_list(self):
        """
        Convert raw data from list of dicts to dict of lists.
        """

        self.data = {}
        if len(self.raw_data) != 0:
            for key in self.raw_data[0].keys():
                if key != 'symbol':
                    self.data[key] = [entry[key] for entry in self.raw_data]


class MessageMetricsResponse(Response):
    """
    Object containing data received from the *message-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<message-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class ArticleMetricsResponse(Response):
    """
    Object containing data received from the *article-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<article-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class PriceMetricsResponse(Response):
    """
    Object containing data received from the *price-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<price-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class TopicMetricsResponse(Response):
    """
    Object containing data received from the *topic-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<topic-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class RankingMetricsResponse(Response):
    """
    Object containing data received from the *ranking-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<ranking-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class SymbolsResponse(Response):
    """
    Object containing data received from the *symbols* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<symbols> endpoint data\n' \
               f'  symbol: {self.raw_data[0]["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class FundamentalsResponse(Response):
    """
    Object containing data received from the *fundametals* endpoint of StockGeist's API.
    """

    def __init__(self, res: Dict, query_args: Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<fundamentals> endpoint data\n' \
               f'  symbol: {self.raw_data[0]["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.raw_data[0]["timestamp"]} -- {self.raw_data[-1]["timestamp"]}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'