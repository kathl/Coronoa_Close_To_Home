# Coronoa Close To Home

I wanted to have a look at some of the official data myself and visualise certain aspects. So this is what I am doing with the code in this repository. The following scripts are included:
 - `get_and_read_rki_data.py` : This script downloads daily situation reports in .pdf format from the RKI webpage [here](https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Situationsberichte/Gesamt.html) and converts Table 2 from these reports to .csv files.
 - `sort_into_csv_rki_data.py`: This script takes the daily .csv files that were create by the previous scrpt, combines them into one big table and does a few calculations. The big table is written to `all_data.csv`
 - `visualise_rki_data.py`: This script attempts a useful visualisation of the data. 
