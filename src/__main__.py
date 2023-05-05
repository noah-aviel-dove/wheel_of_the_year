import argparse
import datetime
import sys
import time

import wheel


def show_wheel(year: int, utc_offset: float) -> None:
    timezone_offset = datetime.timedelta(hours=utc_offset)
    for wheel_day in wheel.wheel(year):
        date, _ = wheel_day.compute(year)
        date += timezone_offset
        fmt = '%b %d %H:%M'
        print(f'{wheel_day.name:<12}{date.strftime(fmt)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('year', nargs='?', default=datetime.datetime.now().year)
    parser.add_argument('--utc-offset', type=float, default=-time.timezone / 60 / 60 + time.daylight)
    args = parser.parse_args(sys.argv[1:])
    show_wheel(args.year, args.utc_offset)
