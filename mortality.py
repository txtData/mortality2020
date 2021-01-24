import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

data_file = 'mortality_germany.xlsx'
months = ['Jan', 'Feb', 'März', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sept', 'Okt', 'Nov', 'Dez']
days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # Ignoring that Feb has 27 days in a gap year.


def prepare_1950_data():
    df = pd.read_excel(data_file, sheet_name=0)
    df = df.drop(['m', 'w'], axis=1)
    df.columns = ['Jahr', 'Monat', 'Tote']
    return df


def prepare_2020_data():
    mort_daily = pd.read_excel(data_file, index_col='Jahr', sheet_name=1)
    mort_daily = mort_daily.T
    array = np.zeros([12, 3])
    for i, row_value in mort_daily[2020].iteritems():
        if np.isnan(row_value):
            row_value = 0
        row = int(i.split('.')[1])
        array[row - 1, 2] += row_value
    array[11, 2] = 106000  # estimating missing data for 12/2020
    for i in range(0, 12):
        array[i, 0] = 2020
        array[i, 1] = i+1
    df = pd.DataFrame(data=array, dtype=int)
    df.columns = ['Jahr', 'Monat', 'Tote']
    return df


def read_population_data():
    df = pd.read_excel(data_file, index_col='Jahr', sheet_name=2)
    df.loc[2020] = df.loc[2019]  # assuming missing data for 2020 is the same as 2019.
    return df


# Deaths per 100,000 chart
def deaths_per_10000(df, df_pop):
    df = df.pivot(index='Monat', columns='Jahr', values='Tote')
    df = df.iloc[:, -10:]
    df_pop = df_pop.iloc[-10:, :]
    df.loc['Year'] = df.sum(numeric_only=True, axis=0)
    df.loc['byPop'] = df.loc['Year'] / (df_pop['Bevölkerung']/100000)

    ax = sns.barplot(x=df.columns, y=df.loc['byPop'], palette="crest")
    ax.set(xlabel='', ylabel='Todesfälle pro 100,000 Einwohner')
    for i, tick in enumerate(ax.get_xticklabels()):
        ax.text(i, int(df.loc['byPop'].iloc[i]) - 40, int(df.loc['byPop'].iloc[i]), horizontalalignment='center', size='x-small', color='w')
    plt.show()


# Deaths per month chart
def deaths_per_month(df, df_pop):
    df = df.pivot(index='Monat', columns='Jahr', values='Tote')
    df = df.iloc[:, -10:]
    df_pop = df_pop.iloc[-10:, :]
    df = df.divide(df_pop['Bevölkerung']/100000, axis=1)
    df = df.divide(days_per_month, axis=0)
    
    markers = [['.', '.', '.', '.', '.'], ['X', 'o', 'D', 'v'], ['s']]
    dashes = [[(1, 1), (1, 1), (1, 1), (1, 1), (1, 1)], [(1, 0), (1, 0), (1, 0), (1, 0)], [(1, 0)]]
    ax = sns.lineplot(data=df.iloc[:, -10:-5], palette="flare", markers=markers[0], dashes=dashes[0], linewidth=.1)
    ax = sns.lineplot(data=df.iloc[:, -5:-1], palette="crest", markers=markers[1], dashes=dashes[1], linewidth=.5)
    ax = sns.lineplot(data=df.iloc[:, -1:], palette="crest", markers=markers[2], dashes=dashes[2], linewidth=1.5)
    ax.set_xticks(range(13))
    ax.set_xticklabels([''] + months + [''])
    ax.set(xlabel='', ylabel='Todesfälle pro 100,000 Einwohner pro Tag')
    plt.show()


# Deviation from yearly means
def deviation_from_mean(df, df_pop):
    df = df.pivot(index='Monat', columns='Jahr', values='Tote')
    df = df.divide(df_pop['Bevölkerung'] / 100000, axis=1)
    df.loc['Year'] = df.sum(numeric_only=True, axis=0)
    df.loc['Avg'] = df.loc['Year'].div(12)
    df.iloc[0:12] = df.sub(df.loc['Avg'])
    df = df.drop(['Year', 'Avg'])
    df = df.abs()
    df.loc['Abweichung'] = df.sum(numeric_only=True, axis=0).div(12)
    df.loc['10-Jahres-Mittel'] = df.loc['Abweichung'].rolling(window=10).mean()
    df = df.drop(range(1,13))

    ax = sns.lineplot(data=df.T, palette="crest", linewidth=1)
    ax.set(xlabel='', ylabel='Mittlere Abweichung eines Monats vom Jahresmittel\npro 100,000 Einwohner')
    plt.legend()
    plt.show()


# Deaths per month for selected years
def deaths_per_month_interesting_years(df, df_pop):
    df = df.pivot(index='Monat', columns='Jahr', values='Tote')
    years = [1957, 1963, 1969, 1970, 2015, 2017, 2018, 2020]
    df = df[years]
    df_pop = df_pop.loc[years]
    df = df.divide(df_pop['Bevölkerung']/100000, axis=1)
    df = df.divide(days_per_month, axis=0)

    markers = [['P', 'X', '^', 'v', 'o', 'D', 'P'], ['s']]
    dashes = [[(1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)], [(1, 0)]]
    ax = sns.lineplot(data=df.iloc[:, -8:-1], palette="crest", markers=markers[0], dashes=dashes[0], linewidth=.1)
    ax = sns.lineplot(data=df.iloc[:, -1:], palette="crest", markers=markers[1], dashes=dashes[1], linewidth=1.5)
    ax.set_xticks(range(13))
    ax.set_xticklabels([''] + months + [''])
    ax.set(xlabel='', ylabel='Todesfälle pro 100,000 Einwohner pro Tag')
    plt.show()


# Deaths per month, alternative visualization
def deaths_per_month_swarm(df):
    df = df.iloc[-120:, :]
    ax = sns.swarmplot(data=df, x=df['Monat'], y=df['Tote'], hue=df['Jahr'], size=7, palette="flare")
    ax.set_xticklabels(months)
    plt.show()


# load the data
df_1950 = prepare_1950_data()
df_2020 = prepare_2020_data()
df = df_1950.append(df_2020, ignore_index=True)
df_pop = read_population_data()

# display the charts
deaths_per_10000(df, df_pop)
deaths_per_month(df, df_pop)
deviation_from_mean(df, df_pop)
deaths_per_month_interesting_years(df, df_pop)

