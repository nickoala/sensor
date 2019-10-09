from sensor import DS18B20

ds = DS18B20('28-00000736781c')

print(ds.temperature().C)
