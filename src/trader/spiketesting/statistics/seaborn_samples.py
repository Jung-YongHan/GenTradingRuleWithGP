import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

df = sns.load_dataset("penguins")
sns.barplot(data=df, x="island", y="body_mass_g", hue="sex")

plt.show()