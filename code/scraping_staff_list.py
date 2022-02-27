#https://qiita.com/kunishou/items/b2e8754886107292926d
#https://qiita.com/kanedaq/items/e65507878c52ad67d002
#https://qiita.com/tobesan/items/12189abc5adbda4a49bd
#https://qiita.com/shikasama/items/d0418fa4a604cfc00337

import time
import re
import pickle
import pandas as pd
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
from atlassian import Confluence

def get_page_from_confluence(page_name):
    limit_ = 1000
    page = confluence.get_page_child_by_type(page_id=page_name, type='page', start=None, limit=limit_)
    return page
def extract_page_name(page_url):
    url_text = 'https://brainpad.atlassian.net/wiki/rest/api/content/'
    return re.sub(url_text, '', page_url)
def clean_text(text):
    return re.sub("\u3000","",text)
def extratct_next_page_from_home(page_list):
    return {clean_text(p_l['title']): int(extract_page_name(p_l['_links']['self'])) for p_l in page_list}
def record_now_time(string=True):
    now_time = datetime.now(pytz.timezone('Asia/Tokyo'))
    if string:
        return now_time.strftime('%Y%m%d%H%M%S')
    else:
        return now_time
def init():
    global confluence
    confluence = Confluence(
        url='https://brainpad.atlassian.net/',
        username='', #自分の会社メアド
        password=''# https://support.atlassian.com/ja/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
    )

# コンフルAPIの設定
init()
print('In progress...')
# 保存用df
list_for_df = []

# トップページ情報を取得
top_page_name = 147980796
home_page = get_page_from_confluence(top_page_name)
time.sleep(1)
# 部署ごとの情報を取得
dep_dict = extratct_next_page_from_home(home_page)
dep_items = sorted(list(dep_dict.items()), reverse=True)
for dep_item in dep_items:
    dep = dep_item[0]
    dep_page_name = dep_item[1]
    dep_page = get_page_from_confluence(dep_page_name)
    time.sleep(1)
    # 課ごとの情報を取得
    div_dict = extratct_next_page_from_home(dep_page)
    div_items = list(div_dict.items())
    # リスト格納
    if len(div_items)==0:
        list_for_df.append([dep_item]+['']+[''])
        break
    for div_item in div_items:
        div = div_item[0]
        div_page_name = div_item[1]
        div_page = get_page_from_confluence(div_page_name)
        time.sleep(1)
        # 従業員ごとの情報を取得
        staff_dict = extratct_next_page_from_home(div_page)
        staff_items = list(staff_dict.items())
        # リスト格納
        if len(staff_items) == 0:
            list_for_df.append([dep_item]+['']+div_items)
        else:
            list_for_df.append([dep_item]+[div_item]+staff_items)
            #break
df_list = pd.DataFrame(list_for_df).set_index(0).drop_duplicates().T

# save
EXCEL_PATH = 'staff_list_%s.xlsx'%record_now_time()
df_excel = pd.DataFrame()
df_excel.to_excel(EXCEL_PATH, index=None)
with pd.ExcelWriter(EXCEL_PATH) as writer:
	#to excel
	sheet_name = '社員リスト'
	df_list.to_excel(writer, sheet_name=sheet_name,index=None)
	worksheet = writer.sheets[sheet_name]
	len_ = 40
	for idx, _ in enumerate(df_list):
		worksheet.set_column(idx, idx, len_)
print('Finish!')




