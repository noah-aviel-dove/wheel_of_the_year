import abc
import datetime
import functools

import ephem
import scipy.optimize


class WheelDay(abc.ABC):
    basedate_fmt = '%m/%d'
    _search_days = 10

    def __init__(self, name: str, basedate: str):
        self.name = name
        self.basedate = datetime.datetime.strptime(basedate, self.basedate_fmt)

    def __str__(self) -> str:
        return self.name

    @abc.abstractmethod
    def _dec_error(self, dec: float) -> float:
        raise NotImplementedError

    @functools.cache
    def compute(self, year: int) -> tuple[datetime.datetime, float]:
        search_range = datetime.timedelta(days=self._search_days)
        t0 = self.basedate.replace(year=year) - search_range/2

        def t(delta_seconds):
            return t0 + datetime.timedelta(seconds=delta_seconds)

        def dec(delta_seconds):
            return ephem.Sun(t(delta_seconds)).g_dec

        def error(delta_seconds):
            return self._dec_error(dec(delta_seconds))

        delta_seconds = scipy.optimize.fminbound(error, 0, search_range.total_seconds())
        return t(delta_seconds), dec(delta_seconds)


class Equinox(WheelDay):

    def _dec_error(self, dec: float) -> float:
        return abs(dec)


class SummerSolstice(WheelDay):

    def _dec_error(self, dec: float) -> float:
        return -dec


class WinterSolstice(WheelDay):

    def _dec_error(self, dec: float) -> float:
        return dec


class CrossQuarterDay(WheelDay, abc.ABC):

    def __init__(self, name: str, basedate: str, solstice_dec: float):
        super().__init__(name, basedate)
        self.solstice_dec = solstice_dec

    def _dec_error(self, dec: float) -> float:
        return abs(dec - self.solstice_dec / 2)


def wheel(year: int) -> list[WheelDay]:
    mar_eqn = Equinox('Ostara', '3/20')
    jun_sol = SummerSolstice('Litha', '6/20')
    sep_eqn = Equinox('Mabon', '9/20')
    dec_sol = WinterSolstice('Yule', '12/20')

    _, max_dec = jun_sol.compute(year)
    _, min_dec = dec_sol.compute(year)
    assert min_dec < 0 < max_dec, (min_dec, max_dec)

    feb_crs = CrossQuarterDay('Imbolc', '2/15', min_dec)
    may_crs = CrossQuarterDay('Beltane', '4/20', max_dec)
    aug_crs = CrossQuarterDay('Lunasa', '8/20', max_dec)  # Lughnasadh
    nov_crs = CrossQuarterDay('Sauin', '10/25', min_dec)  # Samhain

    return [
        feb_crs,
        mar_eqn,
        may_crs,
        jun_sol,
        aug_crs,
        sep_eqn,
        nov_crs,
        dec_sol
    ]
