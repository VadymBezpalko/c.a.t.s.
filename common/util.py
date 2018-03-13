import time
from stock_data.serializers import StockDataSerializer
from twitter_api.serializers import TwitterDataSerializer


def summarize_twitter_data(messages):
    result = []
    current_date = ''

    for message in messages:
        message['summary_sentimental'] = message['sentimental']['polarity'] * message['retweet_count'] \
            if message['retweet_count'] > 0 \
            else message['sentimental']['polarity']
        message['created_at'] = message['created_at'][:10]

        if message['created_at'][:10] == current_date:
            result[-1]['summary_sentimental'] += message['summary_sentimental']
        else:
            result.append(message)
            current_date = message['created_at'][:10]  # get date substring without hours

    return result


def get_serialized_data(data, data_type):
    if data_type == "twitter":
        return TwitterDataSerializer(data, many=True).data
    elif data_type == "stock":
        return StockDataSerializer(data, many=True).data
    else:
        raise ValueError('Wrong data type. Check type parameter.')


def format_date(date):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date, '%a %b %d %H:%M:%S +0000 %Y'))
