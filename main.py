from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Float, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os

app = FastAPI()

# ===== Database =====
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
engine = create_engine(f"sqlite:///{DB_PATH}")
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

hum['low'] = fuzz.trimf(hum.universe, [0, 0, 60])
hum['high'] = fuzz.trimf(hum.universe, [40, 100, 100])

mist['off'] = fuzz.trimf(mist.universe, [0, 0, 35])
mist['medium'] = fuzz.trimf(mist.universe, [15, 50, 70])
mist['long'] = fuzz.trimf(mist.universe, [60, 100, 100])

# 1. NHÓM BẢO VỆ RỄ: Ưu tiên cao nhất
# Đất đã ướt thì tắt bơm tuyệt đối. (Vì các luật dưới đều yêu cầu đất khô/bình thường mới chạy, 
# nên khi đất ướt, CHỈ MÌNH LUẬT NÀY được kích hoạt).
rule1 = ctrl.Rule(soil['wet'], mist['off'])

# 2. NHÓM ĐẤT KHÔ: Ưu tiên cấp nước nhanh cho đất
# Đất khô + Trời nóng -> Tưới thật đẫm (Cứu cây)
rule2 = ctrl.Rule(soil['dry'] & temp['hot'], mist['long'])
# Đất khô + Trời mát/lạnh -> Tưới vừa phải để đất ngấm từ từ, tránh úng rễ
rule3 = ctrl.Rule(soil['dry'] & temp['warm'], mist['medium'])
rule4 = ctrl.Rule(soil['dry'] & temp['cold'], mist['medium'])

# 3. NHÓM ĐẤT BÌNH THƯỜNG: Cân bằng môi trường không khí (Cần kết hợp cả Nhiệt độ & Độ ẩm)
# --- Khi trời nóng ---
# Đất bình thường + Nóng + Khô hanh -> Phun lâu để hạ nhiệt không khí (thay thế cho Rule 9 cũ)
rule5 = ctrl.Rule(soil['normal'] & temp['hot'] & hum['low'], mist['long'])
# Đất bình thường + Nóng + Nồm ẩm -> Bù nước vừa phải, không phun lâu để tránh làm không khí ngột ngạt hơn
rule6 = ctrl.Rule(soil['normal'] & temp['hot'] & hum['high'], mist['medium'])

# --- Khi trời ấm ---
# Đất bình thường + Ấm + Khô hanh -> Tưới sương sương bù ẩm không khí
rule7 = ctrl.Rule(soil['normal'] & temp['warm'] & hum['low'], mist['medium'])
# Đất bình thường + Ấm + Nồm ẩm -> Nghỉ tưới
rule8 = ctrl.Rule(soil['normal'] & temp['warm'] & hum['high'], mist['off'])

# --- Khi trời lạnh ---
# Đất bình thường + Lạnh -> Giữ nguyên, không tưới để tránh nấm mốc
rule9 = ctrl.Rule(soil['normal'] & temp['cold'], mist['off'])

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
