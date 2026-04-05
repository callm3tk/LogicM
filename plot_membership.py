import numpy as np
import matplotlib.pyplot as plt
from scipy.special import expit
import skfuzzy as fuzz

# Hàm trimf (giống scipy-fuzzy)
def trimf(x, abc):
    """Triangular membership function"""
    a, b, c = abc[0], abc[1], abc[2]
    y = np.zeros_like(x, dtype=float)
    
    # Trái
    if a != b:
        y += np.maximum(0, (x - a) / (b - a)) * (x <= b)
    
    # Phải
    if b != c:
        y += np.maximum(0, (c - x) / (c - b)) * (x >= b)
    
    return np.minimum(y, 1.0)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Fuzzy Logic Membership Functions - Smart Watering System\n(Based on Code)', 
             fontsize=14, fontweight='bold')

# ============= BIỂU ĐỒ 1: SOIL MOISTURE (Top-Left) =============
ax1 = axes[0, 0]
soil_range = np.arange(0, 101, 1)

# Từ code: soil['dry'] = [0, 0, 40], soil['normal'] = [30, 50, 70], soil['wet'] = [60, 100, 100]
dry = trimf(soil_range, [0, 0, 40])
normal = trimf(soil_range, [30, 50, 70])
wet = trimf(soil_range, [60, 100, 100])

ax1.fill_between(soil_range, 0, dry, alpha=0.3, label='Dry', color='orange')
ax1.fill_between(soil_range, 0, normal, alpha=0.3, label='Normal', color='yellow')
ax1.fill_between(soil_range, 0, wet, alpha=0.3, label='Wet', color='blue')

ax1.plot(soil_range, dry, 'o-', color='orange', linewidth=2, markersize=4, label='dry: [0,0,40]')
ax1.plot(soil_range, normal, 's-', color='green', linewidth=2, markersize=4, label='normal: [30,50,70]')
ax1.plot(soil_range, wet, '^-', color='blue', linewidth=2, markersize=4, label='wet: [60,100,100]')

ax1.set_xlabel('Soil Moisture (%)', fontweight='bold', fontsize=11)
ax1.set_ylabel('Membership Degree', fontweight='bold', fontsize=11)
ax1.set_title('Input 1: Soil Moisture', fontweight='bold', fontsize=12)
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0, 1.1])

# ============= BIỂU ĐỒ 2: TEMPERATURE (Top-Right) =============
ax2 = axes[0, 1]
temp_range = np.arange(0, 51, 1)

# Từ code: temp['cold'] = [0, 0, 20], temp['warm'] = [15, 30, 35], temp['hot'] = [30, 50, 50]
cold = trimf(temp_range, [0, 0, 20])
warm = trimf(temp_range, [15, 30, 35])
hot = trimf(temp_range, [30, 50, 50])

ax2.fill_between(temp_range, 0, cold, alpha=0.3, label='Cold', color='cyan')
ax2.fill_between(temp_range, 0, warm, alpha=0.3, label='Warm', color='yellow')
ax2.fill_between(temp_range, 0, hot, alpha=0.3, label='Hot', color='red')

ax2.plot(temp_range, cold, 'o-', color='cyan', linewidth=2, markersize=4, label='cold: [0,0,20]')
ax2.plot(temp_range, warm, 's-', color='gold', linewidth=2, markersize=4, label='warm: [15,30,35]')
ax2.plot(temp_range, hot, '^-', color='red', linewidth=2, markersize=4, label='hot: [30,50,50]')

ax2.set_xlabel('Temperature (°C)', fontweight='bold', fontsize=11)
ax2.set_ylabel('Membership Degree', fontweight='bold', fontsize=11)
ax2.set_title('Input 2: Temperature', fontweight='bold', fontsize=12)
ax2.legend(loc='upper right', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_ylim([0, 1.1])

# ============= BIỂU ĐỒ 3: HUMIDITY (Bottom-Left) =============
ax3 = axes[1, 0]
hum_range = np.arange(0, 101, 1)

# Từ code: hum['low'] = [0, 0, 50], hum['high'] = [50, 100, 100]
low = trimf(hum_range, [0, 0, 60])
high = trimf(hum_range, [40, 100, 100])

ax3.fill_between(hum_range, 0, low, alpha=0.3, label='Low', color='lightcoral')
ax3.fill_between(hum_range, 0, high, alpha=0.3, label='High', color='lightblue')

ax3.plot(hum_range, low, 'o-', color='red', linewidth=2, markersize=4, label='low: [0,0,50]')
ax3.plot(hum_range, high, 's-', color='blue', linewidth=2, markersize=4, label='high: [50,100,100]')

ax3.set_xlabel('Air Humidity (%)', fontweight='bold', fontsize=11)
ax3.set_ylabel('Membership Degree', fontweight='bold', fontsize=11)
ax3.set_title('Input 3: Air Humidity', fontweight='bold', fontsize=12)
ax3.legend(loc='upper right', fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.set_ylim([0, 1.1])

# ============= BIỂU ĐỒ 4: MISTING OUTPUT (Bottom-Right) =============
ax4 = axes[1, 1]
mist_range = np.arange(0, 101, 1)

# Từ code: mist['off'] = [0, 0, 20], mist['medium'] = [30, 50, 70], mist['long'] = [60, 100, 100]
off = trimf(mist_range, [0, 0, 35])
medium = trimf(mist_range, [15, 50, 70])
long = trimf(mist_range, [60, 100, 100])

ax4.fill_between(mist_range, 0, off, alpha=0.3, label='Off', color='lightblue')
ax4.fill_between(mist_range, 0, medium, alpha=0.3, label='Medium', color='lightgreen')
ax4.fill_between(mist_range, 0, long, alpha=0.3, label='Long', color='darkgreen')

ax4.plot(mist_range, off, 'o-', color='blue', linewidth=2, markersize=4, label='off: [0,0,20]')
ax4.plot(mist_range, medium, 's-', color='green', linewidth=2, markersize=4, label='medium: [30,50,70]')
ax4.plot(mist_range, long, '^-', color='darkgreen', linewidth=2, markersize=4, label='long: [60,100,100]')

ax4.set_xlabel('Misting Duration (%)', fontweight='bold', fontsize=11)
ax4.set_ylabel('Membership Degree', fontweight='bold', fontsize=11)
ax4.set_title('Output: Misting Level', fontweight='bold', fontsize=12)
ax4.legend(loc='upper right', fontsize=9)
ax4.grid(True, alpha=0.3)
ax4.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig('membership_functions_2x2.png', dpi=300, bbox_inches='tight')
print("✅ Saved: membership_functions_2x2.png")
print("\n📊 Membership Functions Summary:")
print("=" * 60)
print(f"Soil:       Dry=[0,0,40]       Normal=[30,50,70]   Wet=[60,100,100]")
print(f"Temp:       Cold=[0,0,20]      Warm=[15,30,35]     Hot=[30,50,50]")
print(f"Humidity:   Low=[0,0,50]       High=[50,100,100]")
print(f"Misting:    Off=[0,0,20]       Medium=[30,50,70]   Long=[60,100,100]")
print("=" * 60)
plt.show()
