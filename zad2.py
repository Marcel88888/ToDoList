import logging
from decimal import Decimal
import random
import string

logging.basicConfig(level=logging.INFO)


class EnvironmentalError(Exception):
    def __init__(self, statement):
        self.difference = statement
        print(statement)


def get_carpool(n):
    res = set()
    for i in range(n):
        while True:
            letters = string.ascii_letters
            name = ''.join(random.choice(letters) for i in range(10))
            if name not in res:
                break
        cap = random.randint(80, 101)
        while True:
            lev = random.randint(1, 101)
            if lev <= cap:
                break
        obj = Car(name, cap, lev)
        res.add(obj)

    return res


class Car(object):
    def __init__(self, brand, tank_capacity, tanked_fuel):
        self.brand = brand
        self.tank_capacity = tank_capacity
        self.tanked_fuel = tanked_fuel
        full = tanked_fuel / tank_capacity * 100
        tank = Decimal(full).quantize(Decimal('0.1'))
        logging.info("New car of brand {} with tank full in {}% ".format(self.brand, tank))

    def fill_tank(self, *, limit=None, liters=None):
        if limit is not None and liters is not None:
            raise TypeError('Too many arguments.')
        if limit is not None and isinstance(limit, (float, int)) is False:
            raise TypeError('Limit must be float or integer type')
        if liters is not None and isinstance(liters, (float, int)) is False:
            raise TypeError('Liters must be float or integer type')
        result = 0
        if limit is not None:
            tf = limit * self.tank_capacity
            tf2 = Decimal(tf).quantize(Decimal('0.1'))
            if tf2 > self.tanked_fuel:
                result = tf2 - self.tanked_fuel
                self.tanked_fuel = tf2
                return result
            return result
        elif liters is not None:
            if liters + self.tanked_fuel > self.tank_capacity:
                raise ValueError('Too many liters.')
            else:
                return liters

        sub = self.tank_capacity - self.tanked_fuel
        self.tanked_fuel = self.tank_capacity
        return sub

    def __repr__(self):
        tank = self.tanked_fuel / self.tank_capacity * 100
        result = Decimal(tank).quantize(Decimal('0.1'))
        return '<Car at {} od brand {} with tank full in {}%>'.format(
            hex(id(self)), self.brand, result)


class DieselCar(Car):
    def fill_tank(self, *, limit=None, liters=None):
        raise EnvironmentalError('​Diesel fuel not available due to environmental reasons.')

