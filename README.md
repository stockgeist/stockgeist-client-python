# stockgeist-client-python
Python client for fetching data from StockGeist's REST API. 

## Installation
The package can be installed using `pip`:

`pip install stockgeist`

To import the package:

`import stockgeist`

## Getting started
Basic usage is very straightforward. First you have to create an instance of `StockGeistClient` and pass 
your STockGeist REST API token to it:

`client = stockgeist.StockGeistClient(token="example-token")`

Now through the `client` object you get the access to all methods for fetching data from the REST API. 
Let's say that you want to find out how many messages have been posted on social media in the last hour
about the Apple stock (NASDAQ:AAPL). All you have to do is to run the following code snippet:

```
aapl_response = client.get_message_metrics(symbol="AAPL", timeframe="1h")
print(aapl_response.data)
```

Resulting output:

```
{'timestamp': ['2021-06-11 13:20:00+00:00'], 'total_count': [13.0]}
```


## Licence
This package is provided as open source under the terms of the [MIT Licence](https://opensource.org/licenses/MIT).
