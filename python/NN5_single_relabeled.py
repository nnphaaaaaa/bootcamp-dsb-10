# Raw dataset :  https://www.kaggle.com/datasets/ehsankhani/fixed-nn5-dataset
# Article : 


# ============================================================
### Imports ###
# ============================================================
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")           # เซฟรูปได้แม้ไม่มีจอ (รันบน server ได้)
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# ฟอนต์ไทยสำหรับกราฟ: เช็คก่อนว่าเครื่องมีฟอนต์ไหนจริง ค่อยตั้ง
# (ถ้าตั้งชื่อฟอนต์ที่ไม่มี matplotlib จะพ่น warning ทุกครั้งที่วาด)
from matplotlib import font_manager
_avail = {f.name for f in font_manager.fontManager.ttflist}
_thai = [f for f in ["Tahoma", "Loma", "Noto Sans Thai", "Garuda", "Norasi"]
         if f in _avail]
plt.rcParams["font.sans-serif"] = _thai + ["DejaVu Sans", "Arial", "sans-serif"]
plt.rcParams["font.family"] = "sans-serif"
if not _thai:
    print("(!) ไม่พบฟอนต์ไทยในเครื่อง — ข้อความไทยในกราฟอาจแสดงเป็นสี่เหลี่ยม")

# ============================================================
### Setting ###
# ============================================================
FILE        = "Fixed_nn5.xlsx"   # path ไฟล์ข้อมูล
ATM_INDEX   = 0                  # ตู้ที่จะวิเคราะห์ (0-110)
START_DATE  = "1996-03-18"       # วันเริ่มจริงของ NN5 (วันจันทร์)
TEST_DAYS   = 56                 # จำนวนวันที่กันไว้เป็นชุดทดสอบ
FUTURE_DAYS = 14                 # จำนวนวันที่จะทำนายอนาคตจริงในขั้นสุดท้าย
SEASON      = 7                  # รอบของข้อมูล (รายวันมีรอบสัปดาห์ = 7)
N_ATM_EXPECT = 111               # จำนวนตู้ที่ควรมีในไฟล์ NN5
EXPECT_START_DOW = 0             # วันในสัปดาห์ที่ START_DATE ควรเป็น 0 คือวันจันทร์
# ------------------------------------------------------------


# ============================================================
### Functions ### (เขียนรวมไว้บนสุด )
# ============================================================

def fill_value_gaps(train_series):
    """เติมปฏิทินให้ครบทุกวัน แล้วเติม 'ค่า' ที่หาย (NaN) ด้วย interpolation
    (ใช้กับ train เท่านั้น — ตอน deploy ใช้กับข้อมูลเต็มได้)"""
    out = train_series.asfreq("D")
    n_added_days = len(out) - len(train_series)
    n_missing = int(out.isna().sum())

    if n_missing > 0:
        if n_added_days > 0:
            print(f"   เติมวันที่ขาดจากปฏิทิน {n_added_days} วัน | "
                  f"ค่าที่หายรวม {n_missing} จุด -> เติมด้วย interpolation")
        else:
            print(f"   ปฏิทินครบทุกวัน | พบค่าหาย {n_missing} จุด "
                  f"-> เติมด้วย interpolation")
        out = out.interpolate(method="time").ffill().bfill()
    else:
        print("   ข้อมูลครบทุกวัน ไม่มีค่าหาย")
    return out


def cap_outliers_by_weekday(series, k=3.0):
    """cap ค่าที่หลุดโลก โดยคิดขอบแยกตามวันในสัปดาห์ (ไม่ทำลายรอบ 7 วัน)
    ทำไมต้องแยกตามวัน: วันศุกร์ยอดสูง 'โดยธรรมชาติ' ถ้าคิดขอบรวมทั้ง series
    วันศุกร์ปกติจะโดนหาว่าผิด ส่วนค่าผิดจริงของวันอาทิตย์จะหลบรอด
    ทำไม cap ไม่ลบ: ลบแถว = วันหายจากปฏิทิน รอบ 7 วันจะเคลื่อนทั้งเส้น
    หมายเหตุ: day-of-week จะถูกต้องก็ต่อเมื่อ START_DATE เป็นวันจริง
    """
    out = series.copy()
    total = 0
    for dow in range(7):                       # 0=จันทร์ ... 6=อาทิตย์
        mask = out.index.dayofweek == dow
        sub = out[mask]
        q1, q3 = sub.quantile(0.25), sub.quantile(0.75)
        iqr = q3 - q1
        lo = max(0.0, q1 - k * iqr)
        hi = q3 + k * iqr
        total += int(((sub < lo) | (sub > hi)).sum())
        out.loc[mask] = sub.clip(lo, hi)
    print(f"   cap outlier {total} จุด (~{total/len(series)*100:.1f}% ของข้อมูล)")
    return out


# ---------- Metrics: ทุกตัว mask จุดที่ actual เป็น NaN  ----------
def _mask_nan(actual, pred):
    actual = np.asarray(actual, dtype=float)
    pred = np.asarray(pred, dtype=float)
    m = ~np.isnan(actual) & ~np.isnan(pred)
    return actual[m], pred[m]


def mae(actual, pred):
    """พลาดเฉลี่ยกี่หน่วย (ยิ่งน้อยยิ่งดี)"""
    a, p = _mask_nan(actual, pred)
    return np.mean(np.abs(a - p))


def rmse(actual, pred):
    """คล้าย MAE แต่ลงโทษการพลาดก้อนใหญ่หนักกว่า"""
    a, p = _mask_nan(actual, pred)
    return np.sqrt(np.mean((a - p) ** 2))


def smape(actual, pred):
    """SMAPE (%) — metric ของการแข่งขัน NN5 เอาไว้เทียบกับ paper ได้
    จุดที่ actual = forecast = 0 พอดี นับเป็น error 0"""
    a, p = _mask_nan(actual, pred)
    denom = np.abs(a) + np.abs(p)
    ratio = np.where(denom == 0, 0.0, 2.0 * np.abs(p - a) / np.where(denom == 0, 1, denom))
    return 100.0 * np.mean(ratio)


# ---------- โมเดล: ทุกตัว clip ค่าทำนาย >= 0  ----------
def fit_seasonal_naive(train, horizon):
    """Baseline: 'วันนี้ = วันเดียวกันของสัปดาห์ที่แล้ว' (วนแพทเทิร์น 7 วันล่าสุด)"""
    if len(train) < SEASON:
        pred = np.full(horizon, train.mean())
    else:
        last_week = train.iloc[-SEASON:].values
        pred = np.tile(last_week, int(np.ceil(horizon / SEASON)))[:horizon]
    return np.clip(pred, 0, None)


def fit_holt_winters(train, horizon):
    """Holt-Winters: แยก level + trend + seasonal แล้วรวมกันทำนาย
    damped_trend=True กัน trend วิ่งเตลิดเมื่อทำนายไกลๆ (56 วัน)"""
    model = ExponentialSmoothing(
        train, trend="add", damped_trend=True,
        seasonal="add", seasonal_periods=SEASON,
        initialization_method="estimated",
    ).fit()
    return np.clip(model.forecast(horizon).values, 0, None)


def fit_sarima(train, horizon):
    """SARIMA(1,1,1)(1,1,1,7): ARIMA ที่รองรับรอบฤดูกาลรายสัปดาห์
    หมายเหตุ: order นี้เป็นค่าตั้งต้นที่ 'ยังไม่ได้จูน' — จูนจริงทำได้ด้วย
    grid search เล็กๆ แล้วเลือกตัวที่ AIC ต่ำสุด"""
    model = SARIMAX(
        train, order=(1, 1, 1), seasonal_order=(1, 1, 1, SEASON),
        enforce_stationarity=False, enforce_invertibility=False,
    ).fit(disp=False, method = 'lbfgs', maxiter=200 )
    return np.clip(model.forecast(horizon).values, 0, None)


def fit_prophet(train, horizon):
    """Prophet ของ Meta (ถ้ายังไม่ติดตั้ง: pip install prophet)"""
    from prophet import Prophet
    import logging
    logging.getLogger("prophet").setLevel(logging.ERROR)
    logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
    df = train.reset_index()
    df.columns = ["ds", "y"]
    m = Prophet(weekly_seasonality=True, daily_seasonality=False)
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon, freq ="D")
    pred = m.predict(future)["yhat"].iloc[-horizon:].values
    return np.clip(pred, 0, None)


# ตารางรวมโมเดลทั้งหมด: อยากเพิ่ม/ลดโมเดล แก้ตรงนี้ที่เดียว
MODELS = {
    "Seasonal Naive": fit_seasonal_naive,
    "Holt-Winters":   fit_holt_winters,
    "SARIMA":         fit_sarima,
    "Prophet":        fit_prophet,
}


# ============================================================
# STEP 1: โหลดข้อมูล [ read raw data + orientation + sanity check]
# ============================================================
print("STEP 1: โหลดข้อมูล")

raw = pd.read_excel(FILE, header=None)
print(raw.head())

## หากไม่ได้ตั้งชื่อ "Fixed_nn5.xlsx" ตามที่ตั้งไว้ สามารถใช้ for loop วนเข้าไปใน path ไปหาชือ่ไฟล์ที่ลงท้ายด้วย .xlsx, .xls, .csv ได้ 
# import os
# import glob 
#if not os.path.exists(FILE):        # หาไฟล์สำรองให้ ถ้าชื่อไม่ตรง
#    cands = [f for f in glob.glob("*.xlsx") + glob.glob("*.xls") + glob.glob("*.csv")
#             if "nn5" in f.lower()]
#    if cands:
#        FILE = cands[0]
#        print(f"   ไม่เจอไฟล์ตามชื่อที่ตั้ง -> ใช้ {FILE} แทน")
#    else:
#        raise FileNotFoundError(
#            f"ไม่พบไฟล์ '{FILE}' — ดาวน์โหลดจาก Kaggle แล้ววางไว้โฟลเดอร์เดียวกับสคริปต์")

#raw = (pd.read_excel(FILE, header=None) if FILE.lower().endswith((".xlsx", ".xls"))
#       else pd.read_csv(FILE, header=None))

## ตัดหัวตาราง (ข้อความ) และคอลัมน์วันที่ทิ้ง: บังคับทุกช่องเป็นตัวเลข
# ช่องที่ไม่ใช่ตัวเลข (เช่น "NN5-001" หรือวันที่) จะกลายเป็น NaN แล้วถูก drop
#for c in raw.columns:               # คอลัมน์ที่เป็นวันที่ -> ทิ้งทั้งคอลัมน์
#    if pd.api.types.is_datetime64_any_dtype(raw[c]):
#        raw = raw.drop(columns=[c])
#raw = raw.apply(pd.to_numeric, errors="coerce")
#raw = raw.dropna(axis=0, how="all").dropna(axis=1, how="all").reset_index(drop=True)
#raw.columns = range(raw.shape[1])


# เช็ค orientation: NN5 มี 111 ตู้
# ถ้าจำนวนแถวมากกว่าคอลัมน์มาก แปลว่าแถวคือ "วัน" -> พลิกให้แถวเป็น "ตู้"
if raw.shape[0] != N_ATM_EXPECT and raw.shape[1] == N_ATM_EXPECT:
    print(f"   เจอ {N_ATM_EXPECT} ตู้ที่แกนคอลัมน์ -> transpose")
    raw = raw.T.reset_index(drop=True)
elif raw.shape[0] > raw.shape[1]:
    print(f"   ไฟล์วางแบบ วัน x ตู้ ({raw.shape[0]} x {raw.shape[1]}) -> transpose")
    raw = raw.T.reset_index(drop=True)

if raw.shape[0] != N_ATM_EXPECT:    # sanity check — เตือนแต่ไม่หยุด 
    print(f"   (!) คาดว่า {N_ATM_EXPECT} ตู้ แต่พบ {raw.shape[0]} — เช็คไฟล์อีกทีถ้าไม่ตั้งใจ")

print(f"   ขนาด: {raw.shape[0]} ตู้ x {raw.shape[1]} วัน")


# ============================================================
# STEP 2: แปลงเป็น time series (index ต้องเป็นวันที่จริง)
# ------------------------------------------------------------
# NN5 เริ่ม 18 มี.ค. 1996 (วันจันทร์) การใช้วันจริงทำให้ day-of-week
# ของทุกขั้นถูกต้อง: cap outlier ตามวัน, weekly seasonality ของ Prophet, และคอลัมน์ day_of_week ในไฟล์ผลลัพธ์
# ============================================================
print(f"\nSTEP 2: แปลงเป็น time series (ATM #{ATM_INDEX})")

if ATM_INDEX >= raw.shape[0]:
    raise IndexError(f"ค่า ATM_INDEX ({ATM_INDEX}) เกินจำนวนตู้ที่มีอยู่จริง ({raw.shape[0]} ตู้)")

values = raw.iloc[ATM_INDEX].astype(float)
dates = pd.date_range(start=START_DATE, periods=len(values), freq="D")
y = pd.Series(values.values, index=dates, name="withdrawal")

# เดิมไม่มีอะไรตรวจ START_DATE เลย ตั้งผิดไปวันเดียวโปรแกรมก็รันผ่านหมด
# แต่ day-of-week จะเลื่อนทั้งเส้น ทำให้ cap outlier รายวัน, weekly seasonality
# และคอลัมน์ day_of_week ในไฟล์ผลลัพธ์ ผิดตามทั้งหมดโดยไม่มีสัญญาณเตือน
# เพิ่มเงื่อนไข : หยุดทันทีถ้าวันแรกไม่ตรงกับที่คาด (ปิดการตรวจได้ด้วย EXPECT_START_DOW = None)
if EXPECT_START_DOW is not None and y.index[0].dayofweek != EXPECT_START_DOW:
    _want = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][EXPECT_START_DOW]
    raise ValueError(
        f"START_DATE = {START_DATE} ตรงกับวัน{y.index[0].day_name()} "
        f"แต่คาดว่าต้องเป็นวัน{_want}\n"
        f"   ถ้าตั้งผิด day-of-week จะเลื่อนทั้งเส้น ทำให้ cap outlier รายวันและ "
        f"weekly seasonality ผิดทั้งหมด\n"
        f"   แก้ START_DATE ให้ถูก หรือถ้าใช้ข้อมูลชุดอื่น ให้แก้ค่า EXPECT_START_DOW")

n_nan = int(y.isna().sum())
print(f"   ช่วงเวลา: {y.index[0].date()} ({y.index[0].day_name()}) "
      f"ถึง {y.index[-1].date()} ({y.index[-1].day_name()}) | ค่าหาย {n_nan} จุด")


# ============================================================
# STEP 3: EDA — plot ก่อนโมเดลเสมอ
# ============================================================
print("\nSTEP 3: สำรวจข้อมูล -> เซฟรูป step3_explore.png")
fig, axes = plt.subplots(2, 1, figsize=(12, 7))
y.plot(ax=axes[0], title=f"ยอดถอนรายวัน ATM #{ATM_INDEX} (ทั้งหมด {len(y)} วัน)")
y.iloc[:60].plot(ax=axes[1], marker="o", markersize=3,
                 title="ซูม 60 วันแรก — เห็นรอบรายสัปดาห์ชัดๆ (ยอดขึ้นลงซ้ำทุก 7 วัน)")
plt.tight_layout()
plt.savefig("step3_explore.png", dpi=100)
plt.close()

# แยก 3 ส่วนประกอบ: trend + seasonal + noise
# (ใช้ดูภาพรวมเฉยๆ ไม่กระทบข้อมูลจริงที่จะเทรน/ทดสอบ)
y_for_plot = y.interpolate(method="time", limit_direction="both")
decomp = seasonal_decompose(y_for_plot, model="additive", period=SEASON)
fig = decomp.plot()
fig.set_size_inches(12, 8)
plt.tight_layout()
plt.savefig("step3_decompose.png", dpi=100)
plt.close()


# ============================================================
# STEP 4: split train/test ตามเวลา ( ห้ามสุ่ม!)
# ------------------------------------------------------------
# ลำดับสำคัญ: แบ่ง "ก่อน" preprocess เพื่อกัน data leakage
# (ถ้า preprocess ก่อนแบ่ง ข้อมูลอนาคตจะรั่วเข้าการคำนวณขอบ outlier)
# ============================================================
print("\nSTEP 4: แบ่งข้อมูล")
train_raw = y.iloc[:-TEST_DAYS]
test = y.iloc[-TEST_DAYS:]      # test ปล่อยดิบ ห้ามแตะเด็ดขาด
print(f"   train {len(train_raw)} วัน | test {len(test)} วัน "
      f"(56 วัน = horizon ของโจทย์ NN5)")


# ============================================================
# STEP 5: Preprocessing (เฉพาะ train เท่านั้น)
# ============================================================
print("\nSTEP 5: Preprocessing (เฉพาะ train)")
train = fill_value_gaps(train_raw)
train = cap_outliers_by_weekday(train, k=3.0)


# ============================================================
# STEP 6: เทรนทุกโมเดล แล้วทำนายช่วง test
# ============================================================
print("\nSTEP 6: เทรนโมเดล")
predictions = {}
not_converged = set()               # จำไว้ว่าโมเดลไหน fit ไม่ลู่เข้า
for name, fit_func in MODELS.items():
    try:
        # ดัก ConvergenceWarning เฉพาะช่วงที่โมเดลนี้กำลัง fit
        # เดิม warning ถูกปิดหมดตั้งแต่บรรทัด import จึงไม่มีทางรู้ว่าโมเดลไหน fit ไม่สำเร็จ
        # ทั้งที่โมเดลที่ไม่ลู่เข้า "ยังคืนค่าพยากรณ์ออกมาได้" และเข้าไปแข่งใน STEP 7 ได้
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            predictions[name] = fit_func(train, TEST_DAYS)
        if any(issubclass(c.category, ConvergenceWarning) for c in caught):
            not_converged.add(name)
            print(f"   {name} ... เสร็จ  (!) fit ไม่ลู่เข้า — ผลอาจไม่น่าเชื่อถือ")
        else:
            print(f"   {name} ... เสร็จ")
    except ImportError:
        print(f"   {name} ... ข้าม (ยังไม่ได้ติดตั้งไลบรารี)")
    except Exception as e:
        # print error จริง จะได้รู้ว่าพังเพราะอะไร
        print(f"   {name} ... พลาด ({type(e).__name__}: {e})")

# กันเคสทุกโมเดลพลาดหมด
if not predictions:
    raise RuntimeError("ทุกโมเดลล้มเหลว — เช็คข้อมูลและ error ด้านบน")


# ============================================================
# STEP 7:วัดผลและเลือกโมเดลที่ดีที่สุด
# ------------------------------------------------------------
# ใช้ SMAPE (metric ของ NN5) เป็นตัวตัดสิน — เทียบผล
# MAE/RMSE ไว้ดูประกอบ
# ============================================================
print("\nSTEP 7: วัดผลบนชุด test (ยิ่งน้อยยิ่งดี)")
if test.isna().any():
    print(f"   (test มีค่าหาย {int(test.isna().sum())} จุด "
          f"-> วัดผลเฉพาะจุดที่มีค่าจริง ไม่เติมค่าใน test)")
actual = test.values
print(f"   {'โมเดล':<16}{'SMAPE%':>8}{'MAE':>8}{'RMSE':>9}")
scores = {}
for name, pred in predictions.items():
    scores[name] = smape(actual, pred)
    #  ติดดาวโมเดลที่ fit ไม่ลู่เข้า จะได้ไม่เผลอเชื่อคะแนน
    flag = "  (!) ไม่ลู่เข้า" if name in not_converged else ""
    print(f"   {name:<16}{scores[name]:>8.2f}{mae(actual, pred):>8.2f}"
          f"{rmse(actual, pred):>9.2f}{flag}")

valid = {k: v for k, v in scores.items() if not np.isnan(v)}
if not valid:
    raise RuntimeError("ทุกโมเดลได้ SMAPE เป็น NaN — เช็คว่า test มีค่าจริงไหม")
best_name = min(valid, key=valid.get)
print(f"\n   >>> โมเดลที่ดีที่สุดคือ: {best_name} (SMAPE {scores[best_name]:.2f}%) <<<")
if best_name in not_converged:
    print(f"   (!) ระวัง: {best_name} fit ไม่ลู่เข้า คะแนนนี้อาจไม่สะท้อนความสามารถจริง")
print("   หมายเหตุ: ตัดสินจาก test ครั้งเดียวมี variance สูง — ระดับจริงจัง"
      "\n   ควรทำ rolling-origin backtest (เลื่อนจุดตัดหลายครั้งแล้วเฉลี่ย)")


# ============================================================
# STEP 8: พล็อตเปรียบเทียบทุกโมเดล
# ============================================================
print("\nSTEP 8: พล็อตเปรียบเทียบ -> step8_compare.png")
plt.figure(figsize=(12, 5))
plt.plot(train.index[-45:], train.iloc[-45:], color="gray",
         label="train (หลัง preprocess)")
plt.plot(test.index, actual, color="black", marker="o", markersize=3,
         label="ข้อมูลจริง (test, ดิบ)")
for name, pred in predictions.items():
    style = "-" if name == best_name else "--"
    width = 2.0 if name == best_name else 1.2
    plt.plot(test.index, pred, style, linewidth=width,
             label=name + (" (แชมป์)" if name == best_name else ""))
plt.title(f"เทียบการทำนาย {TEST_DAYS} วัน — ATM #{ATM_INDEX}")
plt.ylabel("จำนวนเงิน")
plt.legend()
plt.tight_layout()
plt.savefig("step8_compare.png", dpi=100)
plt.close()


# ============================================================
# STEP 9: ของจริง! เทรนโมเดลที่ดีที่สุดด้วยข้อมูล "ทั้งหมด" แล้วทำนายอนาคต
# ------------------------------------------------------------
# ที่ผ่านมาเราแค่"train"โมเดลกับข้อมูลที่รู้คำตอบอยู่แล้ว
# งานจริงจบที่: เอาโมเดลที่สอบผ่าน มาเทรนใหม่ด้วยข้อมูลทุกวันที่มี
# (รวม test ด้วย — ตอนนี้ไม่ต้องกันไว้แล้ว เพราะtrainเสร็จแล้ว)
# แล้วทำนาย "อนาคตที่ยังไม่เกิด" ซึ่งคือคำตอบที่ธุรกิจอยากได้
# ============================================================
print(f"\nSTEP 9: เทรน {best_name} ด้วยข้อมูลทั้งหมด แล้วทำนายอนาคต {FUTURE_DAYS} วัน")

full = fill_value_gaps(y)                       # คราวนี้ preprocess ทั้งก้อนได้
full_before_cap = full.copy()                   # เก็บไว้เทียบก่อน cap
full = cap_outliers_by_weekday(full, k=3.0)     # (ไม่มี leakage เพราะอนาคตยังไม่เกิด)

# cap ทำงานกับข้อมูลทั้งเส้น รวมช่วงท้ายสุดที่มีนัยยะสำคัญต่อการทำนายมากที่สุด
# ถ้าตู้เพิ่งเปลี่ยนพฤติกรรมจริง ค่าที่สูงขึ้นจะถูกกดลงกลายเป็น "ค่าผิดปกติ"
# ไม่ได้เปลี่ยนพฤติกรรมของโค้ด แค่รายงานให้เห็น จะได้ตัดสินใจเอง
_recent = full.index >= full.index[-FUTURE_DAYS * 2]
_n_recent_capped = int((full[_recent] != full_before_cap[_recent]).sum())
if _n_recent_capped:
    print(f"   (!) {FUTURE_DAYS * 2} วันล่าสุดถูก cap {_n_recent_capped} จุด "
          f"-> ถ้าเป็นการเปลี่ยนพฤติกรรมจริง ไม่ใช่ค่าผิด การทำนายอาจต่ำกว่าที่ควร")

try:
    future_pred = MODELS[best_name](full, FUTURE_DAYS)   
except Exception as e:
    print(f"   (!) {best_name} ล้มตอนเทรนข้อมูลเต็ม ({type(e).__name__}: {e})")
    print(f"       -> ถอยไปใช้ Seasonal Naive เป็น fallback")
    best_name = "Seasonal Naive"
    future_pred = fit_seasonal_naive(full, FUTURE_DAYS)
print(f"   โมเดลที่ใช้ทำนายจริง: {best_name}")
future_dates = pd.date_range(start=y.index[-1] + pd.Timedelta(days=1),
                             periods=FUTURE_DAYS, freq="D")

forecast_df = pd.DataFrame({
    "date": future_dates,
    "day_of_week": future_dates.day_name(),     
    "forecast": np.round(future_pred, 2),
})
forecast_df.to_csv("future_forecast.csv", index=False)

print("\n   ผลทำนายอนาคต:")
print(forecast_df.to_string(index=False))

# พล็อตปิดท้าย: อดีตล่าสุด + อนาคตที่ทำนาย
plt.figure(figsize=(12, 5))
plt.plot(y.index[-60:], y.iloc[-60:], color="black", label="ข้อมูลจริงล่าสุด")
plt.plot(future_dates, future_pred, color="#1D9E75", marker="o",
         linestyle="--", label=f"ทำนายอนาคต ({best_name})")
plt.axvline(y.index[-1], color="gray", linestyle=":", alpha=0.7)
plt.title(f"ทำนายอนาคต {FUTURE_DAYS} วันข้างหน้า — ATM #{ATM_INDEX}")
plt.ylabel("จำนวนเงิน")
plt.legend()
plt.tight_layout()
plt.savefig("step9_future.png", dpi=100)
plt.close()

print("\n" + "=" * 56)
print("เสร็จสมบูรณ์! ไฟล์ที่ได้:")
print("   step3_explore.png / step3_decompose.png  (สำรวจข้อมูล)")
print("   step8_compare.png                        (เทียบโมเดล)")
print("   step9_future.png / future_forecast.csv   (คำตอบสุดท้าย)")
print("=" * 56)

