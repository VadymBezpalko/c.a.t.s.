import time
from stock_data.serializers import StockDataSerializer
from twitter_api.serializers import TwitterDataSerializer


def summarize_twitter_data_by_day(messages):
    result = []
    current_date = ''
    same_day_counter = 0  # used for calculating the average

    for message in messages:
        message['summary_sentimental'] = message['sentimental']['polarity'] * message['retweet_count'] if message['retweet_count'] > 0 else message['sentimental']['polarity']
        message['average_sentimental'] = message['summary_sentimental']
        message['created_at'] = message['created_at'][:10]

        if message['created_at'][:10] == current_date:  # messages from same day
            same_day_counter += 1
            result[-1]['summary_sentimental'] += message['summary_sentimental']
        else:  # messages from new day
            if same_day_counter > 0:
                # not the first day
                # if now we getting data from next day, then evaluate average value for previous day
                result[-1]['average_sentimental'] = result[-1]['summary_sentimental'] / (same_day_counter + 1)
                same_day_counter = 0

            result.append(message)
            current_date = message['created_at'][:10]  # get date substring without hours

    return result


def count_different_messages(messages):
    current_date = 'start'
    result = []
    daily_result = {"neutral": 0, "positive": 0, "negative": 0, "date": ""}

    for message in messages:
        if message['created_at'][:10] == current_date:  # messages from same day
            daily_result = get_message_emotion_tuple(message, daily_result)
        else:
            if current_date == 'start':
                current_date = message['created_at'][:10]
                daily_result['date'] = current_date
                daily_result = get_message_emotion_tuple(message, daily_result)
            else:
                result.append(daily_result)
                current_date = message['created_at'][:10]
                daily_result = {"neutral": 0, "positive": 0, "negative": 0, "date": current_date}
                daily_result = get_message_emotion_tuple(message, daily_result)
    return result


def count_daily_messages(messages):
    current_date = 'start'
    result = []
    daily_result = {"number": 0, "date": ""}

    for message in messages:
        if message['created_at'][:10] == current_date:  # messages from same day
            daily_result["number"] += 1
        else:
            if current_date == 'start':
                current_date = message['created_at'][:10]
                daily_result['date'] = current_date
                daily_result["number"] += 1
            else:
                result.append(daily_result)
                current_date = message['created_at'][:10]
                daily_result = {"number": 0, "date": current_date}
                daily_result["number"] += 1
    return result


def get_message_emotion_tuple(message, temp_tuple):
    if message['sentimental']['polarity'] == 0:
        temp_tuple["neutral"] += 1
    else:
        if message['sentimental']['polarity'] > 0:
            temp_tuple["positive"] += 1
        else:
            temp_tuple["negative"] += 1

    return temp_tuple


def get_serialized_data(data, data_type):
    if data_type == "twitter":
        return TwitterDataSerializer(data, many=True).data
    elif data_type == "stock":
        return StockDataSerializer(data, many=True).data
    else:
        raise ValueError('Wrong data type. Check type parameter.')


def format_date(date):  # helper method for twitter api
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date, '%a %b %d %H:%M:%S +0000 %Y'))
