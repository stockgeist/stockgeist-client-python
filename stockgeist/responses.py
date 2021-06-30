import logging
from collections import deque
from typing import Dict, List

import cufflinks as cf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import wordcloud
from plotly.subplots import make_subplots
from termcolor import colored

import pickle

logger = logging.getLogger()
cf.go_offline(connected=False)

# type aliases
Figure = go.Figure


class _Response:
    """
    Base class for all response objects returned as endpoint-querying results.
    """

    def __init__(self, res: List[Dict]):
        self._status_codes = [entry['metadata']['status_code'] for entry in res]
        self._messages = [entry['metadata']['message'] for entry in res]
        self._credits = [entry['metadata']['credits'] if 'credits' in entry['metadata'] else None for entry in res]
        self._server_timestamps = [entry['metadata']['server_timestamp'] for entry in res]
        self._raw_data = res
        self._data_dict = self._convert_raw_data_to_time_series()

    def _convert_raw_data_to_time_series(self) -> Dict[str, List]:
        """
        Convert raw data from list of dicts to dict of lists.
        :return: Dictionary of lists of data.
        """

        data = {}
        is_time_series_data = False
        for batch in self._raw_data:
            if isinstance(batch['body'], list):
                # time series endpoint data
                is_time_series_data = True
                if len(batch['body']) != 0:
                    for key in batch['body'][0].keys():
                        if key != 'symbol':
                            if key not in data:
                                data[key] = deque([entry[key] for entry in batch['body']])
                            else:
                                data[key].extendleft([entry[key] for entry in batch['body']][::-1])

        if is_time_series_data:
            # convert deques to lists
            data = {key: list(val) for key, val in data.items()}

        return data

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
    def raw_data(self):
        return self._raw_data

    @property
    def as_dict(self):
        return self._data_dict

    @property
    def as_dataframe(self):
        # create pandas DataFrame
        df = pd.DataFrame(self._data_dict, index=pd.DatetimeIndex(self._data_dict['timestamp']))
        df = df.drop('timestamp', axis=1)
        return df

    def _validate_metrics(self, to_parse: str, available_metrics: List[str]) -> List[str]:
        """
        Check whether metrics to be visualized are valid for the particular data.
        :param to_parse: String with metrics joined by + signs.
        :param available_metrics: List of metrics available for visualization for particular data.
        :return: List of validated metric names.
        """
        # parse and validate plotting options
        metric_names = to_parse.split('+')
        for name in metric_names:
            if name not in available_metrics:
                raise Exception(f'{name} is not a valid metric!')
            if name not in self._data_dict.keys():
                raise Exception(
                    f'{name} metric not downloaded! Check the arguments of the appropriate StockGeistClient fetcher function!')

        return metric_names

    def _plot_simple(self, title: str, metric_names: List[str], right_y_metric_names: List[str]) -> Figure:
        """
        Standard method for plotting line plots.
        :param title: String displayed as graph title.
        :param metric_names: List of validated metrics.
        :param right_y_metric_names: List of metrics to be displayed on right-y axis.
        :return: plotly Figure object.
        """
        # plot metrics
        fig = pd.DataFrame(index=self._data_dict['timestamp']) \
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
                x=self._data_dict['timestamp'],
                y=np.array(self._data_dict[name]).flatten(),
                mode='lines',
                name=name,
            )

            if name in right_y_metric_names:
                fig.add_trace(go.Scatter(**plot_args), secondary_y=True)
                right_y_metrics.append(name)
            else:
                fig.add_trace(go.Scatter(**plot_args), secondary_y=False)
                left_y_metrics.append(name)

        # set y axis titles
        fig.update_yaxes(title_text=', '.join(left_y_metrics), secondary_y=False)
        fig.update_yaxes(title_text=', '.join(right_y_metrics), secondary_y=True)
        fig['layout']['yaxis']['autorange'] = "reversed"

        return fig


class MessageMetricsResponse(_Response):
    """
    Object containing data received from the *message-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(zip(self._server_timestamps, self._messages))

        self._query_args = query_args
        self._available_metrics = ['inf_positive_count', 'inf_neutral_count', 'inf_negative_count', 'inf_total_count',
                                   'em_positive_count', 'em_neutral_count', 'em_negative_count', 'em_total_count',
                                   'total_count', 'pos_index', 'msg_ratio', 'ma', 'ma_diff', 'std_dev', 'ma_count_change']

    def visualize(self, what: str = 'total_count', show_fig: bool = True) -> Figure:
        """
        Visualize selected metrics from the downloaded message metrics data.

        :param what: String with metrics joined by + signs.

        :param show_fig: Whether to show generated plotly figure or not.

        :return: plotly Figure object.
        """
        # validate metrics
        metric_names = self._validate_metrics(what, self._available_metrics)

        # plot metrics
        fig = self._plot_simple(title=f'{self._query_args["symbol"]} Message Metrics',
                                metric_names=metric_names,
                                right_y_metric_names=['pos_index', 'msg_ratio', 'ma_count_change'])

        if show_fig:  # pragma: no cover
            fig.show()

        return fig

    def __repr__(self):  # pragma: no cover
        return f'<message-metrics> endpoint data\n' \
               f'  symbol: {self._query_args["symbol"]}\n' \
               f'  timeframe: {self._query_args["timeframe"]}\n' \
               f'  time range: {self._data_dict["timestamp"][0]} -- {pd.Timestamp(self._data_dict["timestamp"][-1]) + pd.Timedelta(self._query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self._query_args["filter"])}'


class ArticleMetricsResponse(_Response):
    """
    Object containing data received from the *article-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self._query_args = query_args
        self._available_metrics = ['titles', 'mentions', 'title_sentiments']
        self._max_title_words = 10
        self._max_titles = 15

    def _plot_simple(self, title: str, metric_names: List[str], right_y_metric_names=None) -> Figure:
        """
        Method for plotting line plots tailored to article metrics data.

        :param title: String displayed as graph title.

        :param metric_names: List of validated metrics.

        :param right_y_metric_names: Not used.

        :return: plotly Figure object.
        """

        # plot metrics
        fig = pd.DataFrame(index=self._data_dict['timestamp']) \
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
                    x=self._data_dict['timestamp'],
                    y=[len(entry) for entry in self._data_dict[name]],
                    mode='lines',
                    name='titles_count',
                )
                # prepare hover-on text
                text = []
                for entry in self._data_dict[name]:
                    txt = "<br>Titles:"

                    # format titles
                    for title in entry[:self._max_titles]:
                        title_words = title.split()
                        if len(title_words) <= self._max_title_words:
                            txt += f"<br> - {' '.join(title_words)}"
                        else:
                            txt += f"<br> - {' '.join(title_words[:self._max_title_words])} ..."
                    if len(entry) > self._max_titles:
                        txt += "<br> ..."
                    text.append(txt)
                fig.add_trace(go.Scatter(**plot_args,
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
                    x=self._data_dict['timestamp'],
                    y=[sum(entry) for entry in self._data_dict[name]],
                    mode='lines',
                    name='mentions_count',
                )
                fig.add_trace(go.Scatter(**plot_args,
                                          hovertemplate=
                                          '<br>Timestamp: %{x}' +
                                          '<br>Mentions: %{y}'
                                          ), secondary_y=False)
                left_y_metrics.append(name)
            elif name == 'title_sentiments':
                # add traces
                counts = [np.unique(entry, return_counts=True) for entry in self._data_dict[name]]
                y = {label: [] for label in ['positive', 'neutral', 'negative']}
                for entry in counts:
                    d = dict(zip(entry[0], entry[1]))
                    for label in ['positive', 'neutral', 'negative']:
                        y[label].append(d.get(label, 0))

                for label in ['positive', 'neutral', 'negative']:
                    plot_args = dict(
                        x=self._data_dict['timestamp'],
                        y=y[label],
                        mode='lines',
                        name=f'titles_count_{label}',
                    )
                    # prepare hover-on text
                    if 'titles' in metric_names:
                        # add titles as hover-on
                        text = []
                        for i, entry in enumerate(self._data_dict[name]):
                            titles = np.array(self._data_dict['titles'][i])
                            if len(entry) != 0:
                                titles = titles[np.array(entry) == label]
                            else:
                                titles = []

                            # format titles
                            txt = "<br>Titles:"
                            for title in titles[:self._max_titles]:
                                title_words = title.split()
                                if len(title_words) <= self._max_title_words:
                                    txt += f"<br> - {' '.join(title_words)}"
                                else:
                                    txt += f"<br> - {' '.join(title_words[:self._max_title_words])} ..."
                            if len(titles) > self._max_titles:
                                txt += "<br> ..."
                            text.append(txt)

                        hovertemplate = '<br>Timestamp: %{x}' + \
                                        '<br>Counts: %{y}' + \
                                        '%{text}'
                        fig.add_trace(go.Scatter(**plot_args,
                                                  hovertemplate=hovertemplate,
                                                  text=text), secondary_y=False)
                    else:
                        # don't add titles
                        hovertemplate = '<br>Timestamp: %{x}' + \
                                        '<br>Counts: %{y}'
                        fig.add_trace(go.Scatter(**plot_args,
                                                  hovertemplate=hovertemplate), secondary_y=False)
                    left_y_metrics.append(f'titles_count_{label}')

        # set y axis titles
        fig.update_yaxes(title_text=', '.join(left_y_metrics), secondary_y=False)
        fig.update_yaxes(title_text=', '.join(right_y_metrics), secondary_y=True)

        return fig

    def visualize(self, what: str = 'titles', show_fig: bool = True) -> Figure:
        """
        Visualize selected metrics from the downloaded article metrics data.

        :param what: String with metrics joined by + signs.

        :param show_fig: Whether to show generated plotly figure or not

        :return: plotly Figure object.
        """
        # validate metrics
        metric_names = self._validate_metrics(what, self._available_metrics)

        fig = self._plot_simple(title=f'{self._query_args["symbol"]} Article Metrics',
                                metric_names=metric_names)

        if show_fig:  # pragma: no cover
            fig.show()

        pickle.dump(fig, open(f'tests/data/article-metrics/NVDA-fig.pkl', 'wb'))

        return fig

    @staticmethod
    def visualize_sentiment(summary: str, sentiment_spans: List[Dict]) -> None:
        """
        Print specified summary text with positive-sentiment parts displayed as green and negative-sentiment parts as red.
        :param summary: Single summary string from downloaded article metrics data.
        :param sentiment_spans: Sentiment spans corresponding to specified summary string.
        """
        def print_colored(text, sentiment=None):
            if sentiment == 'positive':
                print(colored(text, 'green'), end='')
            elif sentiment == 'negative':
                print(colored(text, 'red'), end='')
            else:
                print(text, end='')

        i = 0
        for entry in sentiment_spans:
            span = entry['idx']
            sentiment = entry['sentiment']
            print_colored(summary[i:span[0]])
            print_colored(summary[span[0]: span[1]], sentiment)
            i = span[1]
        print_colored(summary[i:])
        print()

    def __repr__(self):  # pragma: no cover
        return f'<article-metrics> endpoint data\n' \
               f'  symbol: {self._query_args["symbol"]}\n' \
               f'  timeframe: {self._query_args["timeframe"]}\n' \
               f'  time range: {self._data_dict["timestamp"][0]} -- {pd.Timestamp(self._data_dict["timestamp"][-1]) + pd.Timedelta(self._query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self._query_args["filter"])}'


class PriceMetricsResponse(_Response):
    """
    Object containing data received from the *price-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self._query_args = query_args
        self._available_metrics = ['open', 'high', 'low', 'close', 'volume']

    def visualize(self, what: str = 'close', display_candlesticks: bool = False) -> None:
        """
        Visualize selected metrics from the downloaded price metrics data.
        :param what: String with metrics joined by + signs.
        :param display_candlesticks: Whether to display candlestick OHLCV chart (requires all corresponding metrics).
        """
        # validate metrics
        metric_names = self._validate_metrics(what, self._available_metrics)

        # plot metrics
        if not display_candlesticks:
            fig = self._plot_simple(title=f'{self._query_args["symbol"]} Price Metrics',
                                    metric_names=metric_names,
                                    right_y_metric_names=['volume'])

            # remove gaps in chart where there is no data
            if self._query_args['timeframe'] != '1d':
                fig.update_xaxes(
                    rangebreaks=[
                        dict(bounds=[21.5, 12], pattern="hour"),  # hide non-market hours
                        dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                    ]
                )
            else:
                fig.update_xaxes(
                    rangebreaks=[
                        dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                    ]
                )
            fig.show()

        else:
            if 'open' in metric_names and 'high' in metric_names and 'low' in metric_names and 'close' in metric_names \
                    and 'volume' in metric_names:

                # candlestick chart
                qf = cf.QuantFig(self.as_dataframe, title=f'{self._query_args["symbol"]} Price Chart', legend='top',
                                 name=self._query_args["symbol"])
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

    def __repr__(self):  # pragma: no cover
        return f'<price-metrics> endpoint data\n' \
               f'  symbol: {self._query_args["symbol"]}\n' \
               f'  timeframe: {self._query_args["timeframe"]}\n' \
               f'  time range: {self._data_dict["timestamp"][0]} -- {pd.Timestamp(self._data_dict["timestamp"][-1]) + pd.Timedelta(self._query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self._query_args["filter"])}'


class TopicMetricsResponse(_Response):
    """
    Object containing data received from the *topic-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self._query_args = query_args
        self._available_metrics = ['words', 'scores']

    def _plot_wordcloud(self, n: int) -> Figure:
        """
        Create word cloud and popular topics bar chart.
        :param n: Index of the data point to be visualized.
        :return: plotly Figure object.
        """
        fig = make_subplots(1, 2)

        # calculate word cloud
        words = self._data_dict['words'][n]
        scores = self._data_dict['scores'][n]
        wc = wordcloud.WordCloud(width=800, height=800)
        wc.generate_from_frequencies(dict(zip(words, scores)))
        img = wc.to_array()

        # word cloud plot
        fig.append_trace(go.Image(z=img), 1, 1)

        # bar plot
        fig.append_trace(go.Bar(
            x=scores[::-1],
            y=list(range(1, len(words)+1)),
            text=words[::-1],
            textposition='auto',
            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(
                    color='rgba(50, 171, 96, 1.0)',
                    width=1),
            ),
            orientation='h',
            hovertemplate='Score: %{x}'
        ), 1, 2)

        fig.update_layout(title={
            'text': f'{self._query_args["symbol"]} Popular Topics',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

        fig.update_xaxes(showticklabels=False, col=1, row=1)
        fig.update_yaxes(showticklabels=False, col=1, row=1)
        fig.update_yaxes(showticklabels=False, col=2, row=1)

        return fig

    def visualize(self, timestamp: str) -> None:
        """
        Visualize selected metrics from the downloaded article metrics data.
        :param timestamp: Timestamp of data point to be visualized.
        """
        try:
            # check whether timestamp is valid
            n = self.as_dataframe.index.get_loc(timestamp)
        except:
            raise Exception("Can't visualize topics at given timestamp! Timestamp is not valid or out of range!")

        if 'words' in self._available_metrics and 'scores' in self._available_metrics:
            fig = self._plot_wordcloud(n)
            fig.show()
        else:
            logger.warning("Can't display word cloud! Make sure, that you downloaded words and scores data!")

    def __repr__(self):  # pragma: no cover
        return f'<topic-metrics> endpoint data\n' \
               f'  symbol: {self._query_args["symbol"]}\n' \
               f'  timeframe: {self._query_args["timeframe"]}\n' \
               f'  time range: {self._data_dict["timestamp"][0]} -- {pd.Timestamp(self._data_dict["timestamp"][-1]) + pd.Timedelta(self._query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self._query_args["filter"])}'


class RankingMetricsResponse(_Response):
    """
    Object containing data received from the *ranking-metrics* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self._query_args = query_args

    def _plot_animated(self):
        """
        Create animated plot showing stock ranking changes over time.
        """
        # create dataframe suitable for plotly express animation
        d = {}
        n = len(self._data_dict['symbols'][0])
        for key in self._data_dict.keys():
            lst = []
            for entry in self._data_dict[key]:
                if key == 'timestamp':
                    lst.extend([entry[:-6]] * n)
                else:
                    lst.extend(entry)
            d[key.rstrip('s')] = lst
        df = pd.DataFrame(d)

        # create animated plot
        fig = px.bar(df, x="score", y="value",
                     animation_frame="timestamp",
                     color="symbol", hover_name="symbol",
                     range_x=[-0.5, len(self._data_dict['scores'][0]) - 0.5],
                     range_y=[0, df['value'][0]],
                     text='symbol')
        fig.update_layout(showlegend=False)
        fig.update_layout(title={
            'text': f'Ranking by {self._query_args["by"]}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

        return fig

    def visualize(self):
        """
        Visualize selected metrics from the downloaded ranking metrics data.
        """
        if self._query_args['symbol'] is None:
            fig = self._plot_animated()
        else:
            fig = self._plot_simple(title=f'{self._query_args["symbol"]} Ranking by {self._query_args["by"]}',
                                    metric_names=['scores'],
                                    right_y_metric_names=['values'])
        fig.show()

    def __repr__(self):  # pragma: no cover
        return f'<ranking-metrics> endpoint data\n' \
               f'  symbol: {self._query_args["symbol"]}\n' \
               f'  timeframe: {self._query_args["timeframe"]}\n' \
               f'  time range: {self._data_dict["timestamp"][0]} -- {pd.Timestamp(self._data_dict["timestamp"][-1]) + pd.Timedelta(self._query_args["timeframe"])}\n' \
               f'  metrics: {", ".join(self._query_args["filter"])}'


class SymbolsResponse(_Response):
    """
    Object containing data received from the *symbols* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self._query_args = query_args

    @property
    def as_dict(self):
        return self._raw_data[0]['body']['symbols']

    @property
    def as_dataframe(self):
        stocks = self._raw_data[0]['body']['symbols']['stocks']
        crypto = self._raw_data[0]['body']['symbols']['crypto']
        crypto.extend(['-' for _ in range(len(stocks)-len(crypto))])
        d = {'stocks': stocks, 'crypto': crypto}
        df = pd.DataFrame(d)
        return df

    def __repr__(self):  # pragma: no cover
        return f'<symbols> endpoint data\n' \
               f'  date: {self._raw_data[0]["body"]["timestamp"]}'


class FundamentalsResponse(_Response):
    """
    Object containing data received from the *fundametals* endpoint of StockGeist's API.
    """

    def __init__(self, res: List[Dict], query_args: Dict):
        super().__init__(res)

        if self._status_codes[0] != 200:
            raise Exception(self._messages)

        self._query_args = query_args

    @property
    def as_dict(self):
        return self._raw_data[0]['body']

    @property
    def as_dataframe(self):
        d = self._raw_data[0]['body']
        df = pd.DataFrame({key: [val] for key, val in d.items()})
        return df

    def __repr__(self):  # pragma: no cover
        return f'<fundamentals> endpoint data\n' \
               f'  symbol: {self._query_args["symbol"]}\n' \
               f'  date: {self._raw_data[0]["body"]["timestamp"]}' \
               f'  metrics: {", ".join(self._query_args["filter"])}'


