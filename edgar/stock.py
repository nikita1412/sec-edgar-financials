'''
This module ties it all together; it will be the main module that's used 
'''
import pandas as pd
from edgar.edgar import get_financial_filing_info, get_latest_quarter_dir, find_latest_filing_info_going_back_from, SYMBOLS_DATA_PATH
from edgar.filing import Filing
from datetime import datetime

class Stock:
    def __init__(self, symbol, period='annual', year=0, quarter=0):
        self.symbol = symbol
        self.cik = self._find_cik()
        self.period = period
        self.filing = self._get_filing(year, quarter)


    def _find_cik(self):
        df = pd.read_csv(SYMBOLS_DATA_PATH, converters={'cik' : str})
        try:
            cik = df.loc[df['symbol'] == self.symbol]['cik'].iloc[0]
            print('cik for {} is {}'.format(self.symbol, cik))
            return cik
        except IndexError as e:
            raise IndexError('could not find cik, must add to symbols.csv') from None


    def _get_filing(self, year=0, quarter=0):
        filing_info_list = get_financial_filing_info(period=self.period, cik=self.cik, year=year, quarter=quarter)

        if len(filing_info_list) == 0:
            # get the latest
            current_year = datetime.now().year if year == 0 else year
            current_quarter = quarter if quarter > 0 else get_latest_quarter_dir(current_year)[0]
            print('No {} filing info found for year={} quarter={}. Finding latest.'.format(self.period, current_year, current_quarter))

            # go back through the quarters to find the latest
            filing_info_list = find_latest_filing_info_going_back_from(self.period, self.cik, current_year, current_quarter)

            if len(filing_info_list) == 0:
                # we still have nothing, one last try with the previous year
                # this is useful when you're checking for data early on in a
                # calendar year, since it takes time for the filings to come in
                print('Will do a final attempt to find filing info from last year')
                filing_info_list = find_latest_filing_info_going_back_from(self.period, self.cik, current_year - 1, 4)

            if len(filing_info_list) == 0:
                # still not successful, throw hands up and quit
                raise NoFilingInfoException('No filing info found. Try a different period (annual/quarterly), year, and/or quarter.')

        filing_info = filing_info_list[0]

        url = filing_info.url
        filing = Filing(company=self.symbol, url=url)

        return filing



    def get_income_statements(self):
        return self.filing.get_income_statements()

    def get_balance_sheets(self):
        return self.filing.get_balance_sheets()

    def get_cash_flows(self):
        return self.filing.get_cash_flows()



class NoFilingInfoException(Exception):
    pass
