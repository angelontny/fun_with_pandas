import sqlite3
import pandas as pd
import datetime as dt


'''
Notes:
Numbers don't add up. Check for messages containing credited and debited as keywords
credited to - kotak and axis ( no debited to ) done (only checking kotak)
credited by - sbi ( no debit, guessing this is when they use my upi id of sbi bank ) ( done )
credited for - union done
Debited for - union done
'''
def main():
    with sqlite3.connect('./data/sms.db') as conn:
        sent_received_format = '''
            SELECT ROWID, handle_id, date, text
            FROM message
            WHERE (text LIKE '%Sent Rs%' OR text LIKE '%Received Rs%') and handle_id <> 1267
        '''

        sbi_credited_by = '''
            SElECT ROWID, handle_id, date, text FROM message
            WHERE text like '%credited by%'
        '''

        kotak_credited_to = '''
            SElECT ROWID, handle_id, date, text
            FROM message
            WHERE text like '%credited to%' and text like '%kotak%'
        '''

        union_for = '''
            SELECT ROWID, handle_id, date, text
            FROM message
            WHERE text like '%credited for%' or text like '%debited for%'
        '''


        final_query = f'''
            {sent_received_format}
            UNION
            {sbi_credited_by}
            UNION
            {union_for}
            UNION
            {kotak_credited_to};
        '''


        handle_query = '''
            SELECT ROWID, id
            FROM handle;
        '''

        trans_df = pd.read_sql_query(final_query, conn)
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
        # print(final_df['ROWID_x'].is_unique) # meaning, no duplicate records
        total = final_df['amount'].sum()
        received = final_df.loc[final_df['type'],'amount'].sum()
        sent = final_df.loc[final_df['type'] == False,'amount'].sum()
        first_trans = final_df['date'].min()
        last_trans = final_df['date'].max()
        diff = received - sent

        status = {
            'total': total,
            'sent': sent,
            'received': received,
            'diff': diff,
            'first transaction': first_trans,
            'last transaction': last_trans,
            'total transactions': len(final_df)
        }


        final_df.rename(columns={'ROWID_x': 'trans_id'}, inplace=True)
        print(final_df.info())
        for k, v in status.items():
            print(k ,': ', v)
        print(final_df['id'].nunique())

        final_df.to_csv('./data/final.csv', index=False)

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
    elif 'credited by' in text:
        amount = text.split('credited by Rs')[1].split(' on ')[0]
        amount = amount.lstrip('.')
    elif 'credited to' in text:
        amount = text.split('Rs.')[1].split(' is ')[0]
    elif 'Credited for' in text or 'Debited for' in text:
        amount = text.split('Rs:')[1].split(' on ')[0]
    return amount

def check_type(text):
    amount = False
    if 'Received Rs' in text:
        amount = True
    elif 'Sent Rs' in text:
        amount = False
    elif 'credited' in text or 'Credited' in text:
        amount = True
    elif 'Debited' in text:
        amount = False
    return amount

def extract_sr(text):
    amount = 'unkown'
    if 'Received Rs' in text:
        try:
            amount = text.split(' from ')[1].split(' on ')[0]
        except:
            amount = text.split(' to ')[1].split('. ')[0]
    elif 'Sent Rs' in text:
        amount = text.split(' to ')[1].split(' on ')[0]
    elif 'transfer from' in text:
        amount = text.split('transfer from')[1].split(' Ref')[0]
    elif 'reversal' in text:
        amount = 'reversal'
    return amount

def test():
    with sqlite3.connect('./data/sms.db') as conn:
        cursor = conn.cursor()
        query = '''
            SELECT text FROM message
            WHERE text like '%credited%' or text like '%Credited%'
            or text like '%debited%' or text like '%Debited%' and text not like '%requested%';
        '''

        new_query = '''
            SELECT text FROM message
            WHERE text like '%Dear SBI User%' or text like '%Union Bank of India%' and text like '%Rs%';
        '''

        trans_query = '''
            SELECT count(*)
            FROM message
            WHERE (text LIKE 'Sent Rs%' OR text LIKE 'Received Rs%') and handle_id <> 1267
            UNION
            select count(*) from message;
        '''

        result = cursor.execute(trans_query).fetchall()
        for i in result:
            print(i)


if __name__ == "__main__":
    main()
