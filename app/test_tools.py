from tools.weather import check_weather
from tools.carriers import check_alternate_carriers


print("WEATHER TEST")
print(check_weather("Midwest"))

print("\nCARRIER TEST")
print(check_alternate_carriers("Long Beach", "Chicago"))