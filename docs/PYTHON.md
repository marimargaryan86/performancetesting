---
internal: true
---

# Python

## Money

> If I had a dime for every time I’ve seen someone use FLOAT to store currency, I’d have $999.997634

Always use integers when working with monetary values since floats are subject to rounding errors and variability.  To make this easier, we have `snowfall.stdlib.money.Money` in our Python standard library.

```py
from snowfall.stdlib import money

a = money.from_string("12.00", money.Currency("USD"))

print(a.amount)  # 1200
print(a)  # "12.00"
```

If you want to add or subtract money, you can use `add()`. Like this:


```py
from snowfall.stdlib import money

a = money.from_string("12.00", money.Currency("USD"))
b = a.add(money.from_string("-2.00", money.Currency("USD")))

print(b.amount)  # 1000
print(b)  # "10.00"
```

When sending monetary values between services, the protobuf `snowfall.stdlib.v1alpha.Money` should be used. An instance of `snowfall.stdlib.money.Money` can be created from a Python representation of `snowfall.stdlib.v1alpha.Money` and also be turned into one:

```py
from snowfall.stdlib import money
from snowfall.stdlib.v1alpha import money_pb2

a = money.from_protobuf(money_pb2.Money(units=24, currency_code="USD"))

print(a.amount)  # 2400
print(a)  # "24.00"

print(type(a.protobuf()))  # <class 'snowfall.stdlib.v1alpha.money_pb2.Money'>
```
