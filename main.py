from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Float, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = FastAPI()

# ===== Database =====
engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    soil = Column(Float)
    temp = Column(Float)
    hum = Column(Float)
    mist = Column(Float)

Base.metadata.create_all(engine)

# ===== Fuzzy =====
soil = ctrl.Antecedent(np.arange(0, 101, 1), 'soil')
temp = ctrl.Antecedent(np.arange(0, 51, 1), 'temp')
hum = ctrl.Antecedent(np.arange(0, 101, 1), 'hum')
mist = ctrl.Consequent(np.arange(0, 101, 1), 'mist')

soil['dry'] = fuzz.trimf(soil.universe, [0, 0, 40])
soil['normal'] = fuzz.trimf(soil.universe, [30, 50, 70])
soil['wet'] = fuzz.trimf(soil.universe, [60, 100, 100])

temp['cold'] = fuzz.trimf(temp.universe, [0, 0, 20])
temp['warm'] = fuzz.trimf(temp.universe, [15, 30, 35])
temp['hot'] = fuzz.trimf(temp.universe, [30, 50, 50])

hum['low'] = fuzz.trimf(hum.universe, [0, 0, 50])
hum['high'] = fuzz.trimf(hum.universe, [50, 100, 100])

mist['off'] = fuzz.trimf(mist.universe, [0, 0, 20])
mist['medium'] = fuzz.trimf(mist.universe, [30, 50, 70])
mist['long'] = fuzz.trimf(mist.universe, [60, 100, 100])

# Đất đã ướt thì tuyệt đối không tưới thêm, bất chấp thời tiết
rule1 = ctrl.Rule(soil['wet'], mist['off'])

# Đất khô + Trời nóng rát -> Tưới thật đẫm
rule2 = ctrl.Rule(soil['dry'] & temp['hot'], mist['long'])
# Đất khô + Trời mát/lạnh -> Tưới vừa phải để đất ngấm từ từ, tránh úng rễ
rule3 = ctrl.Rule(soil['dry'] & temp['warm'], mist['medium'])
rule4 = ctrl.Rule(soil['dry'] & temp['cold'], mist['medium'])

# Đất bình thường + Trời nóng -> Tưới bù nước (bốc hơi nhanh)
rule5 = ctrl.Rule(soil['normal'] & temp['hot'], mist['medium'])
# Đất bình thường + Trời lạnh -> Giữ nguyên, không tưới để tránh nấm mốc
rule6 = ctrl.Rule(soil['normal'] & temp['cold'], mist['off'])

# Đất bình thường + Trời ấm: Cần xét thêm độ ẩm không khí
# Không khí khô hanh -> Tưới sương sương
rule7 = ctrl.Rule(soil['normal'] & temp['warm'] & hum['low'], mist['medium'])
# Không khí nồm ẩm -> Nghỉ tưới
rule8 = ctrl.Rule(soil['normal'] & temp['warm'] & hum['high'], mist['off'])

# Dù đất thế nào, nếu trời quá nóng và quá khô thì bơm chạy dài để hạ nhiệt không khí
rule9 = ctrl.Rule(temp['hot'] & hum['low'], mist['long'])

# Đưa TẤT CẢ các luật vào hệ thống
system = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9
])
sim = ctrl.ControlSystemSimulation(system)

# ===== API =====
@app.get("/predict")
def predict(soil: float, temp: float, hum: float):
    sim.input['soil'] = soil
    sim.input['temp'] = temp
    sim.input['hum'] = hum
    sim.compute()
    result = sim.output['mist']

    db = Session()
    log = Log(soil=soil, temp=temp, hum=hum, mist=result)
    db.add(log)
    db.commit()
    db.close()

    return {"misting": result}
