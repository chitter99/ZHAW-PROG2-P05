import datetime

def parse_duration(duration: str) -> int:
    duration_format = "%H:%M:%S"
    duration_obj = datetime.datetime.strptime(duration.split("d")[1], duration_format)
    return duration_obj.hour * 60 + duration_obj.minute
