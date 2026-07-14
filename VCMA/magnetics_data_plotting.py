import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

Msat = 1.15e6

#1 data points
df = pd.read_csv('table.txt', sep='\t', header=0)
df.columns = [c.strip().lstrip('#').strip() for c in df.columns]

# Bz on x-axis, Mz on y-axis
x = df['B_extz (T)'].values * 1e4  #Convert to Oe
y = df['mz ()'].values * Msat #Scale by Msat to get Mz in A/m

#2 Generate the scatter plot
plt.plot(x, y, marker='.', markersize=2, linestyle='-')
# 3. Context and Lables

plt.title('Magnetization vs. External Field (Hysteresis Loop for Ku1 = 0.73e6 J/m^3)')
plt.xlabel('External B Field (Oe)')
plt.ylabel('Mz/Msat (A/m)')
plt.legend()
plt.show()      

