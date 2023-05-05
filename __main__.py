import argparse
import datetime
import sys
import time

import astronomy


class WheelInfo(astronomy.SeasonInfo):
    def __init__(self,
                 feb_cross: astronomy.Time,
                 mar_equinox: astronomy.Time,
                 may_cross: astronomy.Time, 
                 jun_solstice: astronomy.Time,
                 aug_cross: astronomy.Time,
                 sep_equinox: astronomy.Time,
                 nov_cross: astronomy.Time,
                 dec_solstice: astronomy.Time):
        super().__init__(mar_equinox, jun_solstice, sep_equinox, dec_solstice)
        self.feb_cross = feb_cross
        self.may_cross = may_cross
        self.aug_cross = aug_cross
        self.nov_cross = nov_cross

    def __repr__(self) -> str:
        return 'Wheel(feb_cross={}, mar_equinox={}, may_cross={}, jun_solstice={}, aug_cross={}, sep_equinox={}, nov_cross={}, dec_solstice={})'.format(
            repr(self.feb_cross),
            repr(self.mar_equinox),
            repr(self.may_cross),
            repr(self.jun_solstice),
            repr(self.aug_cross),
            repr(self.sep_equinox),
            repr(self.nov_cross),
            repr(self.dec_solstice)
        )


def Wheel(year: int) -> WheelInfo:
    seasons = astronomy.Seasons(year)
    # The implmentation of astronomy.Seasons searches starting at the 10th day
    # of each month, with the expected result being close to the 20th.
    # Since the cross-quarter days fall closer to the 5th, we search starting
    # on the 25th of the previous month for consistency.
    feb_cross = astronomy._FindSeasonChange(315, year, 1, 25)
    may_cross = astronomy._FindSeasonChange(45, year, 4, 25)
    aug_cross = astronomy._FindSeasonChange(135, year, 7, 25)
    nov_cross = astronomy._FindSeasonChange(225, year, 10, 25)
    return WheelInfo(
        feb_cross,
        seasons.mar_equinox,
        may_cross,
        seasons.jun_solstice,
        aug_cross,
        seasons.sep_equinox,
        nov_cross,
        seasons.dec_solstice
    )



def format_time(time: astronomy.Time, timezone: datetime.timezone) -> str:
    dt = datetime.datetime.strptime(str(time), '%Y-%m-%dT%H:%M:%S.%fZ')
    dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone(timezone)
    return dt.strftime('%b %d %H:%M')


def show_wheel(year: int, utc_offset: float) -> None:
    wheel = Wheel(year)
    dates = (
        wheel.feb_cross,
        wheel.mar_equinox,
        wheel.may_cross,
        wheel.jun_solstice,
        wheel.aug_cross,
        wheel.sep_equinox,
        wheel.nov_cross,
        wheel.dec_solstice
    )
    names = (
        'Imbolc',
        'Ostara',
        'Beltane',
        'Litha',
        'Lunasa', # Lughnasadh
        'Mabon',
        'Sauin', # Samhain
        'Yule'
    )
    timezone = datetime.timezone(offset=datetime.timedelta(hours=utc_offset))
    for name, date in zip(names, dates):
        print(f'{name:<12}{format_time(date, timezone)}')
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('year', nargs='?', default=datetime.datetime.now().year)
    parser.add_argument('--utc-offset', type=float, default=-time.timezone/60/60)
    args = parser.parse_args(sys.argv[1:])
    show_wheel(args.year, args.utc_offset)
