from config import *
import pandas as pd
import numpy as np
from logger_debug import *
from typing import Dict

def add_user_id(user_id:int, file:str, rating:str):
    all_users_ids_df = pd.read_csv(file, index_col=0)
    if user_id not in all_users_ids_df.user_id.values:
        users_ids_df = pd.concat([all_users_ids_df, pd.DataFrame([{'user_id': user_id}])], ignore_index=True)
        users_ids_df.to_csv(file)
        logger.info(f'chat_id {user_id} is new and added to file of unique users')
    else:
        logger.info(f'chat_id {user_id} is in file of unique users ')

    rating_df = pd.read_csv(rating, index_col=0)
    if user_id not in rating_df.user_id.values:
        rating_df = pd.concat([rating_df, pd.DataFrame([{'user_id': user_id, 'last_phone_number': 0, 'total_requested': 0, 'total_shared': 0}])], ignore_index=True)
        rating_df.to_csv(rating)
        logger.info(f'chat_id {user_id} is new and added to rating file')
    else:
        logger.info(f'chat_id {user_id} is in rating file')


def add_request(user_id:int, file:str, user_data:Dict[str, str]):
    requests_df = pd.read_csv(file, index_col=0)
    if "Телефон" in user_data:
        phone = user_data["Телефон"]
    else:
        phone = 0
    if user_data["Поделиться или попросить"] == "Поделиться":
        status = 'done'
        mode = 'share'
    else:
        status = 'pending'
        mode = 'req'
    df_to_add = pd.DataFrame([{'user_id': user_id, 'phone_number': phone,
                               'req_or_share': mode,
                               'amount': user_data["Количество стикеров"],
                               'time': datetime.datetime.today().strftime("%m/%d/%Y, %H:%M:%S"),
                               'status': status}])
    requests_df = pd.concat([requests_df, df_to_add], ignore_index=True)
    requests_df.to_csv(file)
    logger.info(f'requests updated for with new line for {user_id}')

def make_to_do_list(real_balance:int):
    a = pd.read_csv(REQUESTS_FILE, index_col=0)
    a['time'] = pd.to_datetime(a.time)
    b = pd.read_csv(USERS_RATING_FILE, index_col=0)
    if (np.unique(a.user_id) in np.unique(b.user_id)):
        logger.info(f'OK')
    else:
        logger.info(f'ERROR 0')
    c = pd.merge(a.reset_index(), b.loc[:, ['user_id', 'total_shared']])
    d = c[(c['req_or_share'] == 'req')&(c['status'] == 'pending')].sort_values(by='time').sort_values(by='total_shared', ascending=False)
    to_do_items = []
    for i in d.index.values:
        if (d.loc[i, 'amount'] > real_balance) & (real_balance > 0):
            to_do_items.append([real_balance, d.loc[i, 'phone_number'], d.loc[i, 'index']])
            real_balance = 0
        if d.loc[i, 'amount'] <= real_balance:
            to_do_items.append([d.loc[i, 'amount'], d.loc[i, 'phone_number'], d.loc[i, 'index']])
            real_balance = real_balance - d.loc[i, 'amount']
    return to_do_items

def formed_balance():
    a = pd.read_csv(REQUESTS_FILE)
    req_done_amount_total = np.sum(a[(a['req_or_share'] == 'req') & (a['status'] == 'done')]['amount'].values)
    shared_amount_total = np.sum(a[(a['req_or_share'] == 'share')]['amount'].values)
    return (shared_amount_total - req_done_amount_total)

def change_requests(to_do:Dict[str, str]):
    a = pd.read_csv(REQUESTS_FILE, index_col=0)
    for to_do_item in to_do:
        n_row = int(to_do_item[2])
        if (a.loc[n_row, 'req_or_share'] == 'share')\
                |(a.loc[n_row, 'phone_number'] != to_do_item[1])\
                |(a.loc[n_row, 'amount'] < to_do_item[0]):
            logger.info(f'ERROR 1')
        else:
            logger.info(f'OK')
        if a.loc[n_row, 'amount'] == int(to_do_item[0]):
            logger.info(f"path1 n_row {n_row}, {a.loc[n_row, 'amount']}")
            a.loc[n_row, 'status'] = 'done'
        if a.loc[n_row, 'amount'] > int(to_do_item[0]):
            logger.info(f"path2 n_row {n_row}, {a.loc[n_row, 'amount']}")
            appen = a.loc[n_row:n_row, :].copy()
            a.loc[n_row, 'amount'] = int(a.loc[n_row, 'amount']) - int(to_do_item[0])
            logger.info(f'{appen}')
            appen['status'] = 'done'
            appen['amount'] = int(to_do_item[0])
            logger.info(f'{appen}')
            logger.info(f'{a}')
            a = pd.concat([a, pd.DataFrame(appen)], ignore_index=True)
    a.to_csv(REQUESTS_FILE)