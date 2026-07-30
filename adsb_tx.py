import numpy as np
import time
import pandas as pd
import threading
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import folium

_POLY_STR = "1111111111111010000001001"
_POLY_LEN = len(_POLY_STR)
_POLY_INT = int(_POLY_STR, 2)

def check_crc(binary_adsb):
    msg_len = len(binary_adsb) - 24
    reg = int(binary_adsb[:msg_len], 2) << 24
    parity = int(binary_adsb[-24:], 2)
    total_bits = msg_len + 24
    for i in range(msg_len):
        bit_pos = total_bits - 1 - i
        if (reg >> bit_pos) & 1:
            reg ^= _POLY_INT << (bit_pos - (_POLY_LEN - 1))
    return (reg & ((1 << 24) - 1)) == parity

def decode_callsign(me_field):
    char_assignment = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### ###############0123456789######" #Keyword Encoding for ADSB
    text_to_decode = me_field[8:]
    callsign = ""
    for i in range(0, 48, 6):
        char_index = int(text_to_decode[i:i+6], 2)
        callsign += char_assignment[char_index]
    return callsign

def decode_cpr_format(me_field):
    return me_field[21]

def decode_position(me_field):
    lat_cpr = int(me_field[22:39], 2)
    lon_cpr = int(me_field[39:56], 2)
    return lat_cpr, lon_cpr

def decode_altitude(me_field):
    altitude_data = me_field[8:20]
    q_bit = altitude_data[8]
    if q_bit == "1":
        n = int(altitude_data[0:8] + altitude_data[9:12], 2)
        return n * 25 - 1000
    return None

def decode_vertical_velocity(me_field):
    vertical_vel_abs = int(me_field[37:46], 2)
    if vertical_vel_abs == 0:
        return None
    if me_field[36] == "0":
        return 64 * (vertical_vel_abs - 1)
    else:
        return -64 * (vertical_vel_abs - 1)

def decode_directionals_ground(me_field, subtype):
    if subtype == 3 or subtype == 4:
        return None, None
    ew_raw = int(me_field[14:24], 2)
    ns_raw = int(me_field[25:35], 2)
    if ew_raw == 0 or ns_raw == 0:
        return None, None
    vel_x = (ew_raw - 1) if me_field[13] == "0" else -(ew_raw - 1)
    vel_y = (ns_raw - 1) if me_field[24] == "0" else -(ns_raw - 1)
    velocity = np.sqrt(vel_x**2 + vel_y**2)
    if subtype == 2:
        velocity = velocity * 4
    trackangle = np.degrees(np.arctan2(vel_x, vel_y)) % 360
    return velocity, trackangle

def decode_binary_adsb(binary_adsb):
    downlink = binary_adsb[0:5]
    ICAO_address = binary_adsb[8:32]
    Type_Code = binary_adsb[32:37]
    me_field = binary_adsb[32:88]

    if int(downlink, 2) != 17:
        return None
    if check_crc(binary_adsb) == False:
        return None

    ICAO = format(int(ICAO_address, 2), '06X')
    tc = int(Type_Code, 2)
    now = time.time()

    result = {"icao": ICAO, "time": now, "tc" : tc}
    if 1 <= tc <= 4:
        result["callsign"] = decode_callsign(me_field)
    elif 9 <= tc <= 18:
        result["altitude"] = decode_altitude(me_field)
        result["cpr_format"] = decode_cpr_format(me_field)
        result["cpr_lat"], result["cpr_lon"] = decode_position(me_field)
    elif tc == 19:
        subtype = int(me_field[5:8], 2)
        result["vertical_rate"] = decode_vertical_velocity(me_field)
        result["speed"], result["heading"] = decode_directionals_ground(me_field, subtype)
    return result

def NL(lat):
    if lat < 10**(-6):
        return 59
    elif abs(lat) == 87:
        return 2
    elif abs(lat) > 87:
        return 1
    else:
        nz = 15
        frac = (1 - np.cos(np.pi / (2 * nz))) / (np.cos(np.pi / 180.0 * abs(lat)) ** 2)
        return int(np.floor(2 * np.pi / np.arccos(1 - frac)))


def compute_M(lon_even, lon_odd, lat):
    return int(np.floor(lon_even * (NL(lat) - 1) - lon_odd * NL(lat) + 0.5))


def location_from_even_odd(CPR_lat_even, CPR_lat_odd, CPR_lon_even, CPR_lon_odd, time_even, time_odd):
    lat_even = CPR_lat_even / (2**17)
    lat_odd = CPR_lat_odd / (2**17)
    lon_even = CPR_lon_even / (2**17)
    lon_odd = CPR_lon_odd / (2**17)

    j = np.floor(59 * lat_even - 60 * lat_odd + 0.5)

    LAT_even = (360.0 / 60) * ((j % 60) + lat_even)
    LAT_odd = (360.0 / 59) * ((j % 59) + lat_odd)

    if LAT_even >= 270:
        LAT_even -= 360
    if LAT_odd >= 270:
        LAT_odd -= 360

    if NL(LAT_even) != NL(LAT_odd):
        return None

    if time_even >= time_odd:
        LAT = LAT_even
    else:
        LAT = LAT_odd

    m = compute_M(lon_even, lon_odd, LAT)
    LON_even = (360 / (max(NL(LAT), 1))) * ((m % (max(NL(LAT), 1))) + lon_even)
    LON_odd = (360 / (max(NL(LAT) - 1, 1))) * ((m % (max(NL(LAT) - 1, 1))) + lon_odd)

    if time_even >= time_odd:
        LON = LON_even
    else:
        LON = LON_odd

    if LON >= 180:
        LON = LON - 360

    return LAT, LON


def update_aircraft_dict(dictionary, message):
    tc = message["tc"]
    ICAO = message["icao"]        
    msg_time = message["time"]
    if ICAO not in dictionary:
        dictionary[ICAO] = {
            "callsign": None,
            "lat": None,
            "lon": None,
            "altitude": None,
            "speed": None,
            "heading": None,
            "vertical_rate": None,
            "cpr_even_lat": None,
            "cpr_even_lon": None,
            "cpr_even_time": None,
            "cpr_odd_lat": None,
            "cpr_odd_lon": None,
            "cpr_odd_time": None,
            "last_seen": None,
            "past_positions": [],
        }
       

    state = dictionary[ICAO]
    state["last_seen"] = msg_time

    if 1 <= tc <= 4:
        state["callsign"] = message["callsign"]

    elif 9 <= tc <= 18:
        state["altitude"] = message["altitude"]
        parity = message["cpr_format"]

        if parity == "0":
            state["cpr_even_lat"] = message["cpr_lat"]
            state["cpr_even_lon"] = message["cpr_lon"]
            state["cpr_even_time"] = msg_time
        else:
            state["cpr_odd_lat"] = message["cpr_lat"]
            state["cpr_odd_lon"] = message["cpr_lon"]
            state["cpr_odd_time"] = msg_time

    elif tc == 19:
        state["vertical_rate"] = message["vertical_rate"]
        state["speed"], state["heading"] = message["speed"], message["heading"]

    if state["cpr_even_time"] is not None and state["cpr_odd_time"] is not None:
        if state["cpr_even_lat"] is not None and state["cpr_even_lon"] is not None:
            if state["cpr_odd_lat"] is not None and state["cpr_odd_lon"] is not None:
                if abs(state["cpr_even_time"] - state["cpr_odd_time"]) <= 15:
                    fix = location_from_even_odd(
                        state["cpr_even_lat"],
                        state["cpr_odd_lat"],
                        state["cpr_even_lon"],
                        state["cpr_odd_lon"],
                        state["cpr_even_time"],
                        state["cpr_odd_time"],
                    )
                    if fix is not None:
                        state["lat"], state["lon"] = fix
                        new_pos = (state["lat"], state["lon"])
                        if (len(state["past_positions"]) == 0 or state["past_positions"][-1] != new_pos):
                            state["past_positions"].append(new_pos)
    return dictionary

def clear_stale(dictionary):
    now = time.time()

    for icao in list(dictionary.keys()):
        if now - dictionary[icao]["last_seen"] > 10:
            del dictionary[icao]


def vectorized_looks_like_preamble(magnitude):
    #entry for x is array of all xth elements of each window over all windows
    s = {x: np.array(magnitude[x:x + len(magnitude) - 240]) for x in range(12)}
    #measure the noise as usual
    noise = np.mean((s[1] + s[3] + s[4] + s[5] + s[6] + s[8] + s[10] + s[11]) / 8.0)
    #nonzero_noise = np.where(noise == 0, 1e-6, noise)
    pulse_ok = ((s[0] >= 2 * noise) & (s[2] >= 2 * noise) & (s[7] >= 2 * noise) & (s[9] >= 2 * noise))
    shape_ok = ((s[0] > s[1]) & (s[2] > s[1]) & (s[2] > s[3]) & (s[7] > s[6]) & (s[7] > s[8]) & (s[9] > s[8]) & (s[9] > s[10]))
    return np.nonzero(pulse_ok & shape_ok)[0] #return indexes where both pulse and shape ok

def looks_like_preamble(magnitude, index):
    pulse = [0, 2, 7, 9]
    quiet = [1, 3, 4, 5, 6, 8, 10, 11]

    if index + 240 >= len(magnitude):  # preamble (16) + 112-bit payload (224 samples)
        return False

    window = magnitude[index:(index+16)]
    noise = np.mean(window[quiet])
    if noise == 0:
        noise = 1e-6
    for p in pulse:
        if window[p] < 2 * noise:
            return False
    if not (window[0] > window[1]):
        return False
    if not (window[2] > window[1] and window[2] > window[3]):
        return False
    if not (window[7] > window[6] and window[7] > window[8]):
        return False
    if not (window[9] > window[8] and window[9] > window[10]):
        return False
    return True


def attempt_extract_adsb(magnitude, preamble_index):
    adsb_start = preamble_index + 16
    decoded_bit_string = []
    for x in range(0, 112):
        if magnitude[adsb_start + 2*x] >= magnitude[adsb_start + 2*x + 1]:
            decoded_bit_string.append("1")
        else:
            decoded_bit_string.append("0")
    return "".join(decoded_bit_string)

### --------------------------------------------------------------------- ###

def logbook_to_pandaframe(logbook):
    rows = []
    for icao, state in logbook.items():
        if state["lat"] is not None and state["lon"] is not None:
            rows.append({
                "icao": icao,
                "callsign": state["callsign"], #(state["callsign"] or "").strip() or icao,
                "lat": state["lat"],
                "lon": state["lon"],
                "altitude": state["altitude"],
                "vertical_rate": state["vertical_rate"],
                "speed": state["speed"],
                "heading": state["heading"],
                "last_seen": state["last_seen"],
                "recorded": state["past_positions"],
            })
    return pd.DataFrame(rows)

from matplotlib.path import Path
from matplotlib.markers import MarkerStyle
import matplotlib.patheffects as pe
from matplotlib.transforms import Affine2D

def _airplane_icon_html(heading, color="#ffe600"):
    rotation = heading if heading is not None else 0
    return f"""
    <div style="transform: rotate({rotation}deg); transform-origin: 50% 50%;
                width: 26px; height: 26px;">
        <svg viewBox="0 0 24 24" width="26" height="26">
            <path d="M9.333333333333332 5.964913333333333 14.666666666666666 9.333333333333332v1.3333333333333333l-5.333333333333333 -1.6842v3.5730666666666666L11.333333333333332 13.666666666666666V14.666666666666666l-3 -0.6666666666666666L5.333333333333333 14.666666666666666v-1l2 -1.1111333333333333v-3.5730666666666666L2 10.666666666666666v-1.3333333333333333l5.333333333333333 -3.3684199999999995V2.333333333333333c0 -0.5522866666666666 0.4477333333333333 -1 1 -1s1 0.4477133333333333 1 1v3.63158Z"
                  fill="{color}" stroke="#ffffff" stroke-width="0.6"/>
        </svg>
    </div>
    """

_LABEL_OUTLINE = [pe.withStroke(linewidth=2.5, foreground="black")]

_PLANE_VERTS = [
    (0.150000, 0.305263), (0.950000, -0.200000), (0.950000, -0.400000),
    (0.150000, -0.147370), (0.150000, -0.683330), (0.450000, -0.850000),
    (0.450000, -1.000000), (0.000000, -0.900000), (-0.450000, -1.000000),
    (-0.450000, -0.850000), (-0.150000, -0.683330), (-0.150000, -0.147370),
    (-0.950000, -0.400000), (-0.950000, -0.200000), (-0.150000, 0.305263),
    (-0.150000, 0.850000), (-0.150000, 0.932843), (-0.082840, 1.000000),
    (0.000000, 1.000000), (0.082840, 1.000000), (0.150000, 0.932843),
    (0.150000, 0.850000), (0.150000, 0.305263), (0.150000, 0.305263),
]
_PLANE_CODES = [
    Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
    Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CURVE4,
    Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CLOSEPOLY,
]
_PLANE_PATH = Path(_PLANE_VERTS, _PLANE_CODES)


def _airplane_marker(heading):
    angle = 0 if heading is None else heading
    return MarkerStyle(_PLANE_PATH, transform=Affine2D().rotate_deg(-angle))

def _fmt(data, unit):
    if data is None:
        return "Unknown"
    elif isinstance(data, (float, np.floating)):
        return str(round(data, 2)) + unit
    else:
        return str(data) + unit
   
import cartopy.io.img_tiles as cimgt

class CartoDB(cimgt.GoogleWTS):
    def __init__(self, style="light_all"):
        self.carto_style = style  
        super().__init__(cache=True)
       
    def _image_url(self, tile):
        x, y, z = tile
        return f"https://tiles.basemaps.cartocdn.com/{self.carto_style}/{z}/{x}/{y}.png"

_map_state = {"fig": None, "ax": None, "tiler": None, "basemap_loaded": False}


def setup_map():
    tiler = CartoDB(style="light_all")
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=tiler.crs)
    ax.set_extent([-118.719726, -118.211608, 33.917959, 34.210966], crs=ccrs.PlateCarree())

    _map_state["fig"] = fig
    _map_state["ax"] = ax
    _map_state["tiler"] = tiler
    try_load_basemap()


def try_load_basemap():
    if _map_state["basemap_loaded"]:
        return
    try:
        _map_state["ax"].add_image(_map_state["tiler"], 12)
        _map_state["basemap_loaded"] = True
        print("Basemap tiles loaded.")
    except Exception as e:
        print(f"Basemap unavailable (no internet?), continuing without it: {e}")

def build_folium_map(df, center_lat, center_lon, zoom, auto_refresh_seconds, out_path="map.html"):
    if df.empty:
        view_lat, view_lon = center_lat, center_lon
    else:
        latest = df.loc[df["last_seen"].idxmax()]
        view_lat, view_lon = latest["lat"], latest["lon"]
   
    m = folium.Map(location=[view_lat, view_lon], zoom_start=zoom, tiles="Cartodb Positron")

    for _, row in df.iterrows():
        icon = folium.DivIcon(
            html=_airplane_icon_html(row["heading"]),
            icon_size=(26, 26),
            icon_anchor=(13, 13),
        )
        label_html = (
            f"<b>{row['callsign']}</b><br>"
            f"Alt: {_fmt(row['altitude'], ' ft')}<br>"
            f"Spd: {_fmt(row['speed'], ' kt')}<br>"
            f"Hdg: {_fmt(row['heading'], '\u00b0')}<br>"
            f"Vsp: {_fmt(row['vertical_rate'], ' ft/s')}<br>"
            f"Upd: {_fmt(row['last_seen'], '')}<br>"
        )
 
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=icon,
            tooltip=folium.Tooltip(
                label_html,
                permanent=True,
                direction="right",
                offset=(0, 0),
                sticky=False,
            ),
        ).add_to(m)
        history = row["recorded"]

        if len(history) >= 2:
            folium.PolyLine(
                locations=history,
                color="red",
                weight=2,
                opacity=0.8,
            ).add_to(m)
 
    if auto_refresh_seconds:
        m.get_root().html.add_child(folium.Element(
            f'<meta http-equiv="refresh" content="{auto_refresh_seconds}">'
        ))

    m.get_root().html.add_child(folium.Element("""
        <style>
        .leaflet-tooltip {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #ffffff;
            font-size: 11px;
            line-height: 1.3;
            text-shadow: 0 0 3px #000000, 0 0 3px #000000, 0 0 3px #000000;
        }
        .leaflet-tooltip-right:before,
        .leaflet-tooltip-left:before {
            display: none !important;
        }
        </style>
    """))
 
    m.save(out_path)
    return out_path


def render_frame(df):
    ax = _map_state["ax"]
    fig = _map_state["fig"]

    for artist in list(ax.collections) + list(ax.texts) + list(ax.lines):
        artist.remove()

    for _, row in df.iterrows():
        ax.scatter(
            row["lon"], row["lat"], s=360,
            marker=_airplane_marker(row["heading"]),
            facecolor="#ffe600", edgecolor="white", linewidth=0.6,
            transform=ccrs.PlateCarree(), zorder=5,
        )
        label = "\n".join([
            "Callsign: " + _fmt(row["callsign"], ""),
            "Altitude: " + _fmt(row["altitude"], " ft"),
            "Speed: " + _fmt(row["speed"], " kt"),
            "Heading: " + _fmt(row["heading"], "\u00b0"),
            "Vertical: " + _fmt(row["vertical_rate"], " ft/s"),
            "Update: " + _fmt(time.time() - row["last_seen"], "sec"),
        ])
        ax.text(
            row["lon"] + 0.007, row["lat"], label,
            fontsize=9, color="white", ha="left", va="center",
            transform=ccrs.PlateCarree(), path_effects=_LABEL_OUTLINE, zorder=6,
        )
        history = row["recorded"]
        if len(history) >= 2:
            lats = [p[0] for p in history]
            lons = [p[1] for p in history]
            ax.plot(lons, lats, color="#ffe600", linewidth=2, transform=ccrs.PlateCarree())

    fig.savefig("map.png", dpi=150, bbox_inches="tight")


from compression import compress_24_to_8
import imageio.v3 as iio
import scipy.signal as signal
import time
import sys

from cosmos import *
from digicomm import *

import adi
import io

from common import *

# from bits_and_pam_skeleton import bits_to_pam_symbols
from bytes_and_bits_skeleton import bytes_to_bits, bits_to_bytes
from PIL import Image

dir_plots = 'plots/'
tx_busy = threading.Event()

def transmit_map(path="map.png"):
    if tx_busy.is_set():
        return  # already mid-transmission, skip this update
    tx_busy.set()
    try:
        img = Image.open(path).resize((width, height)).convert("RGB")
        if compression:
            values = compress_24_to_8(np.asarray(img, dtype=np.uint8))
        else:
            values = np.asarray(img, dtype=np.uint8)
        payload = np.array(values).tobytes()
        bits = bytes_to_bits(payload)
        tx_symbols, remainder = bits_to_qam_symbols(bits, M)
        print("transmitting", len(payload), "bytes,", len(tx_symbols), "symbols")
        tx.stop_transmission()
        tx.transmit(tx_symbols)
    finally:
        tx_busy.clear()
   

#Pluto
sdr = adi.Pluto("usb:3.1.5")

# RX config
sdr.rx_lo = int(1090e6)
sdr.rx_rf_bandwidth = int(4e6)
sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = 40
sdr.rx_buffer_size = int(2e6)
sdr.sample_rate = int(2e6)
sdr.rx_destroy_buffer()

# TX config — same object, independent TX chain
sdr.tx_lo = int(915e6)          # legal ISM band, not 1090 MHz
sdr.tx_rf_bandwidth = int(1e6)
sdr.tx_hardwaregain_chan0 = -10

tx = PlutoTransmitter()
tx.set_sdr(sdr)                 # pass the SAME sdr object, not sdr_tx
tx.set_channel(1)
tx.set_sample_rate(int(2e6))
tx.set_power_level(90)



setup_map()

previous_samples = None
previous_df = None
logbook = {}

while True:
    IQ_samples = sdr.rx()
    magnitudes = np.abs(IQ_samples)
    if previous_samples is not None:
        magnitudes = np.concatenate([previous_samples, magnitudes])
    indices_to_decode = vectorized_looks_like_preamble(magnitudes)
    for x in indices_to_decode:
        message = attempt_extract_adsb(magnitudes, x)
        decoded = decode_binary_adsb(message)
        if decoded is not None:
            update_aircraft_dict(logbook, decoded)
    clear_stale(logbook)
    print(logbook)

    df = logbook_to_pandaframe(logbook)
    if previous_df is None or not df.equals(previous_df):
        try_load_basemap()
        render_frame(df)  
        build_folium_map(
            df,
            center_lat=34.072237,
            center_lon=-118.452894,
            auto_refresh_seconds=1,
            zoom = 12,
        )
    threading.Thread(target=transmit_map, daemon=True).start()
    previous_samples = magnitudes[-240:]
    previous_df = df

