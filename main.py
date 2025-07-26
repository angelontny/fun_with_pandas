import sqlite3
import pandas as pd
import datetime as dt


'''
Notes:
Numbers don't add up. Check for messages containing credited and debited as keywords
'''
def main():
    with sqlite3.connect('./data/sms.db') as conn:
        trans_query = '''
            SELECT ROWID, handle_id, date, text
            FROM message
            WHERE (text LIKE '%Sent Rs%' OR text LIKE '%Received Rs%') and handle_id <> 1267;
        '''

        handle_query = '''
            SELECT ROWID, id
            FROM handle;
        '''

        trans_df = pd.read_sql_query(trans_query, conn)
        handle_df = pd.read_sql_query(handle_query, conn)

        trans_df['date'] = pd.DatetimeIndex(trans_df['date'].apply(apple_to_normal))
        amount = trans_df['text'].apply(extract_amount)
        trans_type = trans_df['text'].apply(check_type)
        beneficiary = trans_df['text'].apply(extract_sr)

        trans_df['amount'] = amount.astype(float)
        trans_df['type'] = trans_type
        trans_df['beneficiary'] = beneficiary

        trans_df = trans_df.drop(columns=['text'])

        final_df = trans_df.merge(handle_df, how='left', 
                                  left_on='handle_id', right_on='ROWID', copy=False)
        
        final_df = final_df.drop(columns=['handle_id', 'ROWID_y'])
        print(final_df.loc[final_df['type'] == False,'amount'].sum())
        print(final_df['date'].min(), final_df['date'].max())


        # print(trans_df)


def apple_to_normal(timestamp):
    apple_epoch = dt.datetime(2001, 1, 1)
    timestamp /= 1e9
    return apple_epoch + dt.timedelta(seconds=timestamp)

def extract_amount(text):
    amount = 0
    if 'Received Rs' in text and 'mobile' in text:
        amount = text.split('Received Rs.')[1].split(' on ')[0]
    elif 'Received Rs' in text:
        amount = text.split('Received Rs.')[1].split(' in your ')[0]
    elif 'Sent Rs' in text:
        amount = text.split('Sent Rs.')[1].split(' from ')[0]
    return amount

def check_type(text):
    amount = False
    if 'Received Rs' in text:
        amount = True
    elif 'Sent Rs' in text:
        amount = False
    return amount

def extract_sr(text):
    amount = 0
    if 'Received Rs' in text:
        try:
            amount = text.split(' from ')[1].split(' on ')[0]
        except:
            amount = text.split(' to ')[1].split('. ')[0]
    elif 'Sent Rs' in text:
        amount = text.split(' to ')[1].split(' on ')[0]
    return amount

if __name__ == "__main__":
    main()
