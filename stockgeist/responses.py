from typing import Dict as _Dict
from typing import List as _List

import pandas as pd
import plotly.graph_objects as _go
from collections import deque as _deque
import pandas as _pd
import logging
from plotly.subplots import make_subplots
import numpy as np


logger = logging.getLogger()

import cufflinks as cf

cf.go_offline(connected=False)


class _Response:
    """
    Base class for all response objects returned as endpoint-querying results.
    """

    def __init__(self, res: _List[_Dict]):
        self._status_codes = [entry['metadata']['status_code'] for entry in res]
        self._messages = [entry['metadata']['message'] for entry in res]
        self._credits = [entry['metadata']['credits'] if 'credits' in entry['metadata'] else None for entry in res]
        self._server_timestamps = [entry['metadata']['server_timestamp'] for entry in res]
        self._data_dict = [entry['body'] for entry in res]
        self._data_list = self._convert_raw_data_to_list()
        self._data_df = self._convert_data_to_df()

    def _convert_raw_data_to_list(self):
        """
        Convert raw data from list of dicts to dict of lists.
        """

        data = {}
        for batch in self._data_dict:
            if len(batch) != 0:
                for key in batch[0].keys():
                    if key != 'symbol':
                        if key not in data:
                            data[key] = _deque([entry[key] for entry in batch])
                        else:
                            data[key].extendleft([entry[key] for entry in batch][::-1])

        # convert deques to lists
        for key in data.keys():
            data[key] = list(data[key])

        return data

    def _convert_data_to_df(self):
        # create pandas DataFrame
        df = pd.DataFrame(self._data_list, index=pd.DatetimeIndex(self._data_list['timestamp']))
        df = df.drop('timestamp', axis=1)

        return df

    @property
    def status_codes(self):
        return self._status_codes

    @property
    def messages(self):
        return self._messages

    @property
    def credits(self):
        return self._credits

    @property
    def server_timestamps(self):
        return self._server_timestamps

    @property
    def data_dict(self):
        return self._data_dict

    @property
    def data_list(self):
        return self._data_list

    @property
    def data_df(self):
        return self._data_df

    def _validate_metrics(self, to_parse, available_metrics):
        # parse and validate plotting options
        metric_names = to_parse.split('+')
        for name in metric_names:
            if name not in available_metrics:
                raise Exception(f'{name} is not a valid metric!')
            if name not in self._data_list.keys():
                raise Exception(
                    f'{name} metric not downloaded! Check the arguments of the appropriate StockGeistClient fetcher function!')

        return metric_names

    def _plot_simple(self, title, metric_names, right_y_metric_names):

        # plot metrics
        fig = pd.DataFrame(index=self._data_list['timestamp']) \
            .iplot(kind='scatter',
                   xTitle='Time',
                   title=title,
                   asFigure=True)
        fig = fig.set_subplots(specs=[[{"secondary_y": True}]])

        left_y_metrics = []
        right_y_metrics = []
        for name in metric_names:
            # add trace
            plot_args = dict(
                x=self._data_list['timestamp'],
                y=self._data_list[name],
                mode='lines',
                name=name,
            )

            if name in right_y_metric_names:
                fig.add_trace(_go.Scatter(**plot_args), secondary_y=True)
                right_y_metrics.append(name)
            else:
                fig.add_trace(_go.Scatter(**plot_args), secondary_y=False)
                left_y_metrics.append(name)

        # set y axis titles
        fig.update_yaxes(title_text=', '.join(left_y_metrics), secondary_y=False)
        fig.update_yaxes(title_text=', '.join(right_y_metrics), secondary_y=True)

        return fig


class MessageMetricsResponse(_Response):
    """
    Object containing data received from the *message-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: _List[_Dict], query_args: _Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(zip(self._server_timestamps, self._messages))

        self.query_args = query_args
        self.available_metrics = ['inf_positive_count', 'inf_neutral_count', 'inf_negative_count', 'inf_total_count',
                                  'em_positive_count', 'em_neutral_count', 'em_negative_count', 'em_total_count',
                                  'total_count', 'pos_index', 'msg_ratio', 'ma', 'ma_diff', 'std_dev', 'ma_count_change']

    def visualize(self, what='total_count'):

        # validate metrics
        metric_names = self._validate_metrics(what, self.available_metrics)

        # plot metrics
        fig = self._plot_simple(title=f'{self.query_args["symbol"]} Message Metrics',
                                metric_names=metric_names,
                                right_y_metric_names=['pos_index', 'msg_ratio', 'ma_count_change'])
        fig.show()

    def __repr__(self):
        return f'<message-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self._data_list["timestamp"][0]} -- {_pd.Timestamp(self._data_list["timestamp"][-1]) + pd.Timedelta(self.query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class ArticleMetricsResponse(_Response):
    """
    Object containing data received from the *article-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: _List[_Dict], query_args: _Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self.query_args = query_args
        self.available_metrics = ['titles', 'mentions', 'title_sentiments', 'summaries', 'sentiment_spans']

    def visualize(self, what='titles'):

        # validate metrics
        metric_names = self._validate_metrics(what, self.available_metrics)

        if 'summaries' not in metric_names and 'sentiment_spans' not in metric_names:
            fig = self._plot_simple(title=f'{self.query_args["symbol"]} Article Metrics',
                                    metric_names=metric_names)
            fig.show()

        else:
            self._visualize_sentiment()

    def _plot_simple(self, title, metric_names):

        # plot metrics
        fig = pd.DataFrame(index=self._data_list['timestamp']) \
            .iplot(kind='scatter',
                   xTitle='Time',
                   title=title,
                   asFigure=True)
        fig = fig.set_subplots(specs=[[{"secondary_y": True}]])

        left_y_metrics = []
        right_y_metrics = []
        for name in metric_names:
            if name == 'titles':
                # add trace
                plot_args = dict(
                    x=self._data_list['timestamp'],
                    y=[len(entry) for entry in self._data_list[name]],
                    mode='lines',
                    name='titles_count',
                )
                # prepare hover-on text
                text = []
                for entry in self._data_list[name]:
                    txt = "<br>Titles:"
                    for title in entry:
                        txt += f"<br> - {title}"
                    text.append(txt)
                fig.add_trace(_go.Scatter(**plot_args,
                                          hovertemplate=
                                          '<br>Timestamp: %{x}' +
                                          '<br>Counts: %{y}' +
                                          '%{text}',
                                          text=text
                                          ), secondary_y=False)
                left_y_metrics.append(name)
            elif name == 'mentions':
                # add trace
                plot_args = dict(
                    x=self._data_list['timestamp'],
                    y=[sum(entry) for entry in self._data_list[name]],
                    mode='lines',
                    name='mentions_count',
                )
                fig.add_trace(_go.Scatter(**plot_args,
                                          hovertemplate=
                                          '<br>Timestamp: %{x}' +
                                          '<br>Mentions: %{y}'
                                          ), secondary_y=False)
                left_y_metrics.append(name)
            elif name == 'title_sentiments':
                # add traces
                counts = [np.unique(entry, return_counts=True) for entry in self._data_list[name]]
                y = {label: [] for label in ['positive', 'neutral', 'negative']}
                for entry in counts:
                    d = dict(zip(entry[0], entry[1]))
                    for label in ['positive', 'neutral', 'negative']:
                        y[label].append(d.get(label, 0))

                for label in ['positive', 'neutral', 'negative']:
                    plot_args = dict(
                        x=self._data_list['timestamp'],
                        y=y[label],
                        mode='lines',
                        name=f'titles_count_{label}',
                    )
                    # prepare hover-on text
                    if 'titles' in metric_names:
                        # add titles as hover-on
                        text = []
                        for i, entry in enumerate(self._data_list[name]):
                            titles = np.array(self._data_list['titles'][i])
                            if len(entry) != 0:
                                titles = titles[np.array(entry) == label]
                            else:
                                titles = []

                            txt = "<br>Titles:"
                            for title in titles:
                                txt += f"<br> - {title}"
                            text.append(txt)

                        hovertemplate = '<br>Timestamp: %{x}' + \
                                        '<br>Counts: %{y}' + \
                                        '%{text}'
                        fig.add_trace(_go.Scatter(**plot_args,
                                                  hovertemplate=hovertemplate,
                                                  text=text), secondary_y=False)
                    else:
                        # don't add titles
                        hovertemplate = '<br>Timestamp: %{x}' + \
                                        '<br>Counts: %{y}'
                        fig.add_trace(_go.Scatter(**plot_args,
                                                  hovertemplate=hovertemplate), secondary_y=False)
                    left_y_metrics.append(name)

        # set y axis titles
        fig.update_yaxes(title_text=', '.join(left_y_metrics), secondary_y=False)
        fig.update_yaxes(title_text=', '.join(right_y_metrics), secondary_y=True)

        return fig

    def _visualize_sentiment(self):
        pass

    def __repr__(self):
        return f'<article-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self._data_list["timestamp"][0]} -- {_pd.Timestamp(self._data_list["timestamp"][-1]) + pd.Timedelta(self.query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class PriceMetricsResponse(_Response):
    """
    Object containing data received from the *price-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: _List[_Dict], query_args: _Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self.query_args = query_args
        self.available_metrics = ['open', 'high', 'low', 'close', 'volume']

    def visualize(self, what='close', display_candlesticks=False):

        # validate metrics
        metric_names = self._validate_metrics(what, self.available_metrics)

        # plot metrics
        if not display_candlesticks:
            fig = self._plot_simple(title=f'{self.query_args["symbol"]} Price Metrics',
                                    metric_names=metric_names,
                                    right_y_metric_names=['volume'])

            # remove gaps in chart where there is no data
            fig.update_xaxes(
                rangebreaks=[
                    dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                    dict(bounds=[21.5, 12], pattern="hour"),  # hide non-market hours
                ]
            )
            fig.show()

        else:
            if 'open' in metric_names and 'high' in metric_names and 'low' in metric_names and 'close' in metric_names \
                    and 'volume' in metric_names:

                # candlestick chart
                qf = cf.QuantFig(self._data_df, title=f'{self.query_args["symbol"]} Price Chart', legend='top',
                                 name=self.query_args["symbol"])
                qf.add_volume()
                fig = qf.figure()

                # remove gaps in chart where there is no data
                fig.update_xaxes(
                        rangebreaks=[
                            dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                            dict(bounds=[21.5, 12], pattern="hour"),  # hide non-market hours
                        ]
                    )
                fig.show()

            else:
                logger.warning("Can't display candlestick chart! Make sure, that you downloaded full OHLCV data!")

    def __repr__(self):
        return f'<price-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self._data_list["timestamp"][0]} -- {_pd.Timestamp(self._data_list["timestamp"][-1]) + pd.Timedelta(self.query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class TopicMetricsResponse(_Response):
    """
    Object containing data received from the *topic-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: _List[_Dict], query_args: _Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self.query_args = query_args
        self.available_metrics = ['words', 'scores']



    def __repr__(self):
        return f'<topic-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self._data_list["timestamp"][0]} -- {_pd.Timestamp(self._data_list["timestamp"][-1]) + pd.Timedelta(self.query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class RankingMetricsResponse(_Response):
    """
    Object containing data received from the *ranking-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: _List[_Dict], query_args: _Dict):
        super().__init__(res)

        if self.status_code != 200:
            raise Exception(self.message)

        self.query_args = query_args

    def __repr__(self):
        return f'<ranking-metrics> endpoint data\n' \
               f'  symbol: {self.query_args["symbol"]}\n' \
               f'  timeframe: {self.query_args["timeframe"]}\n' \
               f'  time range: {self.data["timestamp"][0]} -- {_pd.Timestamp(self.data["timestamp"][-1]) + pd.Timedelta(self.query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self.query_args["filter"])}'


class SymbolsResponse(_Response):
    """
    Object containing data received from the *symbols* endpoint of StockGeist's API.
    """

    def __init__(self, res: _Dict, query_args: _Dict):
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


class FundamentalsResponse(_Response):
    """
    Object containing data received from the *fundametals* endpoint of StockGeist's API.
    """

    def __init__(self, res: _Dict, query_args: _Dict):
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