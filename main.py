from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_sun, SkyCoord, solar_system_ephemeris
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import get_body


def get_location_coordinates(city_name: str):

    city_coordinates = {
        "Toronto": (43.6532, -79.3832, 76),
        "New York": (40.7128, -74.0060, 10),
        "London": (51.5074, -0.1278, 11),
        "Budapest": (47.4979, 19.0402, 96),
        "Tokyo": (35.6895, 139.6917, 40),
    }
    if city_name in city_coordinates:
        return city_coordinates[city_name]
    else:
        raise ValueError(f"A '{city_name}' nevű város nem található az adatbázisban.")


# Város kiválasztása

print('Kérem adja meg a város nevét:')
city_name = input()
LAT, LON, HEIGHT = get_location_coordinates(city_name)

# Földrajzi helyzet beállítása
location = EarthLocation(lat=LAT * u.deg, lon=LON * u.deg, height=HEIGHT * u.m)

# Időzóna és idő beállítása
TIME_ZONE = ZoneInfo("Europe/Budapest")  # Frissítsd a város időzónájára
current_time = datetime.now(TIME_ZONE)
time = Time(current_time)

# Horizontális koordináta-rendszer az adott helyen
altaz_frame = AltAz(obstime=time, location=location)

# Nap és Hold helyzetének számítása
sun = get_sun(time).transform_to(altaz_frame)
moon = get_body("moon", time, location).transform_to(altaz_frame)  # Javított hívás

# Bolygók helyzetének számítása
planets = ["mercury", "venus", "mars", "jupiter", "saturn"]
planet_coords = {}
with solar_system_ephemeris.set("builtin"):
    for planet in planets:
        planet_coords[planet.capitalize()] = get_body(planet, time, location).transform_to(altaz_frame)

# Fényes csillagok (pl. Vega, Sirius, Polaris)
bright_stars = {
    "Vega": SkyCoord(ra=18.615649 * u.hourangle, dec=38.78369 * u.deg).transform_to(altaz_frame),
    "Sirius": SkyCoord(ra=6.752569 * u.hourangle, dec=-16.7161 * u.deg).transform_to(altaz_frame),
    "Polaris": SkyCoord(ra=2.5303 * u.hourangle, dec=89.2641 * u.deg).transform_to(altaz_frame),
}

# Adatok összeállítása
objects = {"Nap": sun, "Hold": moon, **planet_coords, **bright_stars}
azimuths = [obj.az.deg for obj in objects.values()]
altitudes = [obj.alt.deg for obj in objects.values()]
labels = list(objects.keys())

# Égbolt megjelenítése
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, polar=True)

# Azimut átalakítása radiánná a pólusdiagramhoz
azimuths_rad = np.radians(azimuths)

# Pólusdiagram beállításai
ax.set_theta_zero_location("N")  # Észak 0 fok
ax.set_theta_direction(-1)       # Azimut óramutató járásával ellentétes

# Adatok rajzolása
for i, name in enumerate(labels):
    ax.scatter(azimuths_rad[i], 90 - altitudes[i], label=name, s=100)

# Diagram címkék
ax.set_rmax(90)  # Magasság maximuma 90 fok
ax.set_yticks([0, 30, 60, 90])  # Körív skála
ax.set_yticklabels(["90°", "60°", "30°", "Horizont"])
ax.set_xticks(np.radians([0, 90, 180, 270]))  # Azimut skála
ax.set_xticklabels(["Észak", "Kelet", "Dél", "Nyugat"])

# Jelmagyarázat és cím
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.05))
ax.set_title(f"Égbolt {city_name} felett\n{current_time.strftime('%Y-%m-%d %H:%M:%S')}", va="bottom")

plt.show()
