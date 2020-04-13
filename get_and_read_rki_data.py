import tabula
import numpy as np
import pandas as pd
import os
import requests
import subprocess

def find_first_data_line(tab):
    ''' Up and running '''
    for i, row in tab.iterrows():
        if (type(row[0]) == float):
            continue
        if ('Brandenburg' in row[0]):
            BB_index = i
        if ('Baden' in row[0]):
            BW_index = i
    return np.min([BB_index, BW_index])

def find_column_names(tab, data_start_index, date_vortag='03.2020'):
    ''' Up and running '''
    keywords_to_search = {'Bundesland': ['Bundesland'],
                          'Gebiete, besond.': ['Besonders betroffene'],
                          'Faelle': ['Fallzahl', 'bestätigter',
                                     'Anzahl', 'Vorab'],
                          'Faelle pro 10^5': ['100.000 Einw.', 'Fälle/100.000'],
                          'Faelle, elekt.': ['elektronisch'],
                          'Aenderung': [#'Änderung',
                                        'Differenz', 'Vortag',
                                        '03.2020', '04.2020'],
                          'Todesfaelle': ['Todesfälle']}
    columns = {}
    for col in tab.columns:
        col_content = []
        for i, row in tab.iterrows():
            if i >= data_start_index:
                continue
            for keyword in keywords_to_search.keys():
                for indicator in keywords_to_search[keyword]:
                    if type(row[col]) == float:
                        continue
                    elif indicator in row[col]:
                        col_content.append(keyword)
        col_content = list(set(col_content))
#         print(col_content)
        if (len(col_content) > 2) & (col_content[-1] == 'Aenderung'):
            col_content = col_content[: -1]
        if (len(col_content) == 2) & ('Aenderung' in col_content) & \
            ('Vortag' in col_content):
            col_content = ['Vortag']
#         if (len(col_content) == 2) & (col_content[0] == col_content[-1]):
#             col_content = [col_content[0]]
        columns[col] = col_content
    return columns

def parse_numbers(num_str):
    if type(num_str) == float:
        return num_str
    if ('+' in num_str):
        num_str_split = num_str.split('+')
        num_str = num_str_split[0] + num_str_split[1]
    if ',' in num_str:
        num_str_split = num_str.split(',')
        num_out = float(num_str_split[0] + '.' + num_str_split[1])
    elif '.' in num_str:
        num_str_split = num_str.split('.')
        if len(num_str_split[1]) == 3:
            num_out = float(num_str_split[0] + num_str_split[1])
        else:
            num_out = float(num_str_split[0] + '.' + num_str_split[1])
    else:
        try:
            num_out = float(num_str)
        except ValueError:
            num_out = -99.9
            # print('Can not convert --{}-- to number'.format(num_str))
    return num_out

def convert_column_to_numbers(old_col):
    if old_col[0] in ['Brandenburg', 'Baden-Württemberg']:
        new_col = old_col
    else:
        new_col = []
        for entry in old_col:
            new_entry = parse_numbers(entry)
            new_col.append(new_entry)
    return new_col

def separate_columns(tab, data_start_index):
    '''Up and running'''
    out_data = {}
    split_nec = False
    for col in tab.columns:
        if type(tab[col].iloc[7]) == float:
            out_data[col] = tab[col].tolist()[data_start_index: ]
            continue
        if (len(tab[col].iloc[7].split(' ')) == 2) & \
            ('+' not in tab[col].iloc[7].split(' ')):
            split_nec = True
            out1, out2 = [], []
            for row in tab[col]:
                if type(row) == float:
                    out1.append(row)
                    out2.append(row)
                elif type(row) == str:
                    splitted = row.split(' ')
                    out1.append(splitted[0])
                    out2.append(splitted[1])
                else:
                    # print('Can\'t deal with this row: ')
                    # print(row)
                    continue
            out1 = convert_column_to_numbers(out1[data_start_index: ])
            out2 = convert_column_to_numbers(out2[data_start_index: ])
            out_data['{}a'.format(col)] = out1
            out_data['{}b'.format(col)] = out2
        elif (len(tab[col].iloc[7].split(' ')) == 3) & \
            ('+' in tab[col].iloc[7].split(' ')):
            out1, out2 = [], []
            for row in tab[col]:
                if type(row) == float:
                    out1.append(row)
                    out2.append(row)
                elif '+' not in row.split(' '):
                    out1.append(row)
                    out2.append(row)
                elif type(row) == str:
                    splitted = row.split(' ')
                    ind = splitted.index('+')
                    splitted = splitted[ : ind] + splitted[ind + 1 : ]
                    out1.append(splitted[0])
                    out2.append(splitted[1])
            out1 = convert_column_to_numbers(out1[data_start_index: ])
            out2 = convert_column_to_numbers(out2[data_start_index: ])
            out_data['{}a'.format(col)] = out1
            out_data['{}b'.format(col)] = out2
        elif (len(tab[col].iloc[7].split(' ')) == 2) & \
            ('+' in tab[col].iloc[7].split(' ')):
            out = []
            for row in tab[col]:
                if type(row) == float:
                    out.append(row)
                elif type(row) == str:
                    splitted = row.split(' ')
                    out.append(splitted[-1])
            out = convert_column_to_numbers(out[data_start_index: ])
            out_data[col] = out
        else:
            out = convert_column_to_numbers(
                    tab[col].tolist()[data_start_index: ])
            out_data[col] = out
    return out_data, split_nec

def sort_complicated_by_comparing(column_list, data_a, data_b):
    index_100000 = column_list.index('Faelle pro 10^5')
    if index_100000 == 1:
        other_index = 0
    else:
        other_index = 1
    if data_a[2] < data_b[2]:
        column1 = column_list[index_100000]
        data1 = data_a
        column2 = column_list[other_index]
        data2 = data_b
    else:
        column2 = column_list[index_100000]
        data2 = data_b
        column1 = column_list[other_index]
        data1 = data_a
    return column1, data1, column2, data2

def sort_complicated_data(columns, data):
    out_data = {}
    for possib_key in columns.keys():
        if (possib_key in columns.keys()) & (possib_key in data.keys()):
            out_data[columns[possib_key][0]] = data[possib_key]
        elif(len(columns[possib_key]) == 2) & \
            ('{}a'.format(possib_key) in data.keys()):
            if 'Bundesland' in columns[possib_key]:
                bl_index = columns[possib_key].index('Bundesland')
                if bl_index == 1:
                    other_index = 0
                else:
                    other_index = 1
                try:
                    float(data['{}a'.format(possib_key)][0])
                    out_data[columns[possib_key][other_index]] = \
                        data['{}a'.format(possib_key)]
                    out_data[columns[possib_key][bl_index]] = \
                        data['{}b'.format(possib_key)]
                except ValueError:
                    out_data[columns[possib_key][other_index]] = \
                        data['{}b'.format(possib_key)]
                    out_data[columns[possib_key][bl_index]] = \
                        data['{}a'.format(possib_key)]
            elif 'Faelle pro 10^5' in columns[possib_key]:
                column1, data1, column2, data2 = \
                    sort_complicated_by_comparing(columns[possib_key],
                                              data['{}a'.format(possib_key)],
                                              data['{}b'.format(possib_key)])
                out_data[column1] = data1
                out_data[column2] = data2
        elif(len(columns[possib_key]) == 3) & \
            ('{}a'.format(possib_key) in data.keys()):
            if ('Faelle' in columns[possib_key]) & \
                ('{}c'.format(possib_key) not in data.keys()):
                # remove 'Faelle' from the columns list
                index = columns[possib_key].index('Faelle')
                column_list = columns[possib_key][: index] + \
                              columns[possib_key][index + 1 :]
                # assume that ''
                column1, data1, column2, data2 = \
                    sort_complicated_by_comparing(column_list,
                                                 data['{}a'.format(possib_key)],
                                                 data['{}b'.format(possib_key)])
                out_data[column1] = data1
                out_data[column2] = data2
            else:
                continue
                # print('Can\'t deal with three different columns in one column')
        else:
            continue
            # print('Seems like this is not yet implemented')
    return out_data

def sort_columns_data(columns, data, split_nec):
    if (split_nec == False) & (len(columns.keys()) == len(data.keys())):
        out_data = {}
        for key in columns.keys():
            out_data[columns[key][0]] = data[key]
    elif (len(columns.keys()) == len(data.keys())):
        out_data = {}
        for key in columns.keys():
            out_data[columns[key][0]] = data[key]
    else:
        out_data = sort_complicated_data(columns, data)
    df = pd.DataFrame(out_data)
    return df

def read_table(year, month, day):
    # issues i cleaned by hand so far:
    #         can't read: 2020-03-11 (blue font), 2020-03-29 (table in image),
    #                     2020-04-02 (iable in image)
    #         NaNs in 'Bundesland': 2020-03-23
    #         Mecklenburg and Vorpommern in seperate lines: 2020-04-01
    #         Sachsen-Anhalt mit *: 2020-03-30, 2020-03-31
    rki_file_url = 'http://www.rki.de/DE/Content/InfAZ/N/' + \
                   'Neuartiges_Coronavirus/Situationsberichte/' + \
                   '{0:04d}-{1:02d}-{2:02d}'.format(year, month, day) + \
                   '-de.pdf?__blob=publicationFile'
    rki_file_path = 'RKI_data/{0:04d}-{1:02d}-{2:02d}-de.pdf'.format(year,
                                                                     month,
                                                                     day)
    try:
        rki_file_downloaded = requests.get(rki_file_url, allow_redirects=True)
    except requests.exceptions.RequestException:
        print('requests is causing the issue')
        return 0
    with open(rki_file_path, 'wb') as file_open:
        file_open.write(rki_file_downloaded.content)
    try:
        table_list = tabula.read_pdf(rki_file_path, pages='2',
                                      pandas_options={"header": 'None'})
    except subprocess.CalledProcessError:
        print('Can\'t read this file: {}'.format(rki_file_path))
        return 0
    if len(table_list) < 1:
        # print('couldn\'t read file on {0:04d} {1:02d} {2:02d}'.format(year,
        #                                                               month,
        #                                                               day))
        return 0
    tab = table_list[0]
    # print(tab)
    data_start = find_first_data_line(tab)
    columns = find_column_names(tab, data_start)
    out_data, split_nec = separate_columns(tab, data_start)
    out_table = sort_columns_data(columns, out_data, split_nec)
    out_path = 'RKI_data/{0:04d}-{1:02d}-{2:02d}.csv'.format(year, month, day)
    out_table.to_csv(out_path)
    return 1

if __name__ == '__main__':
    date_start = pd.Timestamp('2020-03-04')
    date_end = pd.Timestamp.today()
    date_range = pd.date_range(date_start, date_end)
    for day in date_range:
        # print('{0:04d}-{1:02d}-{2:02d}'.format(day.year, day.month, day.day))
        if os.path.isfile('RKI_data/{0:04d}-{1:02d}-{2:02d}.csv'.format(day.year,
                                                               day.month,
                                                               day.day)):
            # print('Date already here')
            continue
        else:
            success = read_table(day.year, day.month, day.day)
        if success == 0:
            report_file = 'RKI_data/report_{0:04d}-{1:02d}-{2:02d}.txt'.format(day.year,
                                                                     day.month,
                                                                     day.day)
            with open(report_file, 'a') as report:
                report.write('Couldn\'t read report from ')
                report.write('RKI_data/{0:04d}-{1:02d}-{2:02d} \n'.format(day.year,
                                                               day.month,
                                                               day.day))
