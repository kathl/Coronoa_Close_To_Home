import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import glob

def log_10(x, a):
    return 10.0**(a * x)
def lin(x, a, b):
    return a * x + b

all_data = {}
all_dates = []
all_timestamps = []
base_folder = 'RKI_data/'
for day in range(4, 32):
    date = '2020-03-{0:02d}'.format(day)
    tab = pd.read_csv(base_folder + date + '.csv', header=0, index_col=0)
    all_data[date] = tab
    all_dates.append(date)
    all_timestamps.append(pd.Timestamp(date))

for day in range(1, 10):
    date = '2020-04-{0:02d}'.format(day)
    tab = pd.read_csv(base_folder + date + '.csv', header=0, index_col=0)
    all_data[date] = tab
    all_dates.append(date)
    all_timestamps.append(pd.Timestamp(date))

bundeslaender = ['Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg',
                 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern',
                 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz',
                 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein',
                 'Thüringen']
bl_folks = {'Baden-Württemberg': 11069533, 'Bayern': 13076721,
            'Berlin': 3644826, 'Brandenburg': 2511917, 'Bremen': 682986,
            'Hamburg': 1841179, 'Hessen': 6265809,
            'Mecklenburg-Vorpommern': 1609675, 'Niedersachsen': 7982448,
            'Nordrhein-Westfalen': 17932651, 'Rheinland-Pfalz': 4084844,
            'Saarland': 990509, 'Sachsen': 4077937, 'Sachsen-Anhalt': 2208321,
            'Schleswig-Holstein': 2896712, 'Thüringen': 2143145}

out_faelle = {'Datum': all_dates, 'Timestamp': all_timestamps}
out_all_data = pd.DataFrame(out_faelle)

for land in bundeslaender:
    land_faelle = []
    land_todesfaelle = []
    for day in all_dates:
        if land in all_data[day]['Bundesland'].tolist():
            add_faelle = \
                all_data[day][all_data[day]['Bundesland'] ==
                              land]['Faelle'].iloc[0]
        else:
            add_faelle = 0.0
        if (land in all_data[day]['Bundesland'].tolist()) &\
            ('Todesfaelle' in all_data[day].columns):
            add_todesfaelle = \
                all_data[day][all_data[day]['Bundesland'] ==
                              land]['Todesfaelle'].iloc[0]
        else:
            add_todesfaelle = 0.0
        land_faelle.append(add_faelle)
        land_todesfaelle.append(add_todesfaelle)
    out_all_data[land + ' Faelle'] = land_faelle
    out_all_data[land + ' Faelle pro 100000'] = np.array(land_faelle) / \
                                                (bl_folks[land] / 1.0e5)
    out_all_data[land + ' Todesfaelle'] = land_todesfaelle
    out_all_data[land + ' Todesfaelle pro 100000'] = np.array(land_todesfaelle) / \
                                                     (bl_folks[land] / 1.0e5)
    out_all_data[land + ' neue Faelle'] = np.zeros(len(all_data))
    out_all_data[land + ' neue Faelle pro 100000'] = np.zeros(len(all_data))
    out_all_data[land + ' Wachstumsrate (5d)'] = np.zeros(len(all_data))
    out_all_data[land + ' Verdopplungszeit (5d)'] = np.zeros(len(all_data))

for index in out_all_data.index:
    for land in bundeslaender:
        if index == 0:
            out_all_data.at[index, land + ' neue Faelle'] = np.nan
            out_all_data.at[index, land + ' neue Faelle pro 100000'] = np.nan
        else:
            out_all_data.at[index, land + ' neue Faelle'] = \
                out_all_data.at[index, land + ' Faelle'] - \
                out_all_data.at[index - 1, land + ' Faelle']
            out_all_data.at[index, land + ' neue Faelle pro 100000'] = \
                out_all_data.at[index, land + ' neue Faelle'] / \
                (bl_folks[land] / 1.0e5)
    if index < 5:
        for land in bundeslaender:
            out_all_data.at[index, land + ' Wachstumsrate (5d)'] = np.nan
            out_all_data.at[index, land + ' Verdopplungszeit (5d)'] = np.nan
    else:
        for land in bundeslaender:
            out_all_data.at[index, land + ' Wachstumsrate (5d)'] = \
                np.mean(out_all_data.loc[index - 4: index,
                                         land + ' Faelle']) / \
                np.mean(out_all_data.loc[index - 5: index - 1,
                                         land + ' Faelle'])
            x = out_all_data.index[index - 4: index + 1]
            y = out_all_data.loc[index - 4: index, land + ' Faelle']
            if np.min(y) <= 0.0:
                out_all_data.at[index, land + ' Verdopplungszeit (5d)'] = np.nan
            else:
                popt, pcov = curve_fit(lin, x, np.log10(y))
                if (np.log10(2)/popt[0] < 0.0) | (np.log10(2)/popt[0] > 1.0e5):
                    out_all_data.at[index, land + ' Verdopplungszeit (5d)'] = \
                        np.nan
                else:
                    out_all_data.at[index, land + ' Verdopplungszeit (5d)'] = \
                        (np.log10(2) / popt[0])
out_all_data.to_csv('RKI_data/all_data.csv')
