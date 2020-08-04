from mechanize import Browser
from bs4 import BeautifulSoup
from urllib import parse
import json

data = {}
hiddens = {}
br = Browser()

br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_debug_http(False)

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
br.addheaders = [('User-agent', user_agent)]

url = '	https://bluechipindia.co.in/MutualFund/MFInner.aspx?id=8'


def dump_mf_data():
    br.open(url)
    resp = br.response().read()
    soup = BeautifulSoup(resp, 'html.parser')
    hidden = soup.find_all('input', {"type" : "hidden"})
    for hid in hidden:
        hiddens.update({hid['id']: hid['value']})

    AMCs = soup.find_all('option')
    for amc in AMCs[1:-1]:
        data.update({str((amc['value'], amc.text)): []})
        print(amc['value'], amc.text)
        dat = parse.urlencode({b'__EVENTTARGET': 'ctl07$ddl_AMC',
                           b'__EVENTARGUMENT': '',
                           b'__LASTFOCUS': '',
                           b'__VIEWSTATE': hiddens['__VIEWSTATE'],
                           b'__VIEWSTATEGENERATOR': hiddens['__VIEWSTATEGENERATOR'],
                           b'__VIEWSTATEENCRYPTED': hiddens['__VIEWSTATEENCRYPTED'],
                           b'__EVENTVALIDATION': hiddens['__EVENTVALIDATION'],
                           b'ctl07$ddl_AMC': amc['value'],
                           b'ctl07$ddl_Scheme': 'Select a Scheme',
        })
        br.open(url, dat)
        scheme_soup = BeautifulSoup(br.response().read(), 'html.parser')
        schemes = scheme_soup.select('#ctl07_ddl_Scheme')[0]
        for scheme in schemes.findChildren('option')[1:]:
            # print('    ', scheme['value'], scheme.text)
            data[str((amc['value'], amc.text))].append((scheme['value'], scheme.text))

    with open('mf_data.json', 'w') as fp:
        json.dump(data, fp)


def dump_div_data():
    i = 0
    br.open(url)
    resp = br.response().read()
    soup = BeautifulSoup(resp, 'html.parser')
    hidden = soup.find_all('input', {"type": "hidden"})
    for hid in hidden:
        # print('Setting Hiddens:', {hid['id']: hid['value']})
        hiddens.update({hid['id']: hid['value']})

    AMCs = soup.find_all('option')
    for amc in AMCs[1:-1]:
        data.update({amc.text: {}})
        print(amc.text)
        dat = parse.urlencode({b'__EVENTTARGET': 'ctl07$ddl_AMC',
                               b'__EVENTARGUMENT': hiddens['__EVENTARGUMENT'],
                               b'__LASTFOCUS': hiddens['__LASTFOCUS'],
                               b'__VIEWSTATE': hiddens['__VIEWSTATE'],
                               b'__VIEWSTATEGENERATOR': hiddens['__VIEWSTATEGENERATOR'],
                               b'__VIEWSTATEENCRYPTED': hiddens['__VIEWSTATEENCRYPTED'],
                               b'__EVENTVALIDATION': hiddens['__EVENTVALIDATION'],
                               b'ctl07$ddl_AMC': amc['value'],
                               b'ctl07$ddl_Scheme': 'Select a Scheme',
                               })
        br.open(url, dat)
        scheme_soup = BeautifulSoup(br.response().read(), 'html.parser')

        hidden = scheme_soup.find_all('input', {"type": "hidden"})
        for hid in hidden:
            # print('Updating Hiddens:', {hid['id']: hid['value']})
            hiddens.update({hid['id']: hid['value']})

        schemes = scheme_soup.select('#ctl07_ddl_Scheme')[0]

        for scheme in schemes.findChildren('option')[1:]:
            if 'Monthly Dividend' not in scheme.text or 'Direct' not in scheme.text:
                continue
            data[amc.text].update({scheme.text: []})
            load = {b'__EVENTTARGET': hiddens['__EVENTTARGET'],
                    b'__EVENTARGUMENT': hiddens['__EVENTARGUMENT'],
                    b'__LASTFOCUS': hiddens['__LASTFOCUS'],
                    b'__VIEWSTATE': hiddens['__VIEWSTATE'],
                    b'__VIEWSTATEGENERATOR': hiddens['__VIEWSTATEGENERATOR'],
                    b'__VIEWSTATEENCRYPTED': hiddens['__VIEWSTATEENCRYPTED'],
                    b'__EVENTVALIDATION': hiddens['__EVENTVALIDATION'],
                    b'ctl07$ddl_AMC': amc['value'],
                    b'ctl07$ddl_Scheme': scheme['value'],
                    b'ctl07$btn_submit': 'Get Records'
                   }
            dat = parse.urlencode(load)
            br.open(url, dat)
            div_soup = BeautifulSoup(br.response().read(), 'html.parser')

            hidden = div_soup.find_all('input', {"type": "hidden"})
            for hid in hidden:
                hiddens.update({hid['id']: hid['value']})

            table = div_soup.find_all('table', {'id': 'ctl07_dg_Div_Hist'})
            if len(table) < 1:
                print(scheme.text, 'BLANK')
                continue
            print('    ', scheme.text)
            rows = table[0].find_all('tr')
            num_pages = len(rows[0].find_all('a'))
            # print('Number of pages:', num_pages)
            for row in rows[2:-1]:
                tds = row.find_all('td')
                row_data = (tds[0].text, tds[1].text, tds[2].text)
                # print('        ', row_data)
                data[amc.text][scheme.text].append(row_data)
            iter = 1
            while iter < num_pages + 1:
                load = {b'__EVENTTARGET': 'ctl07$dg_Div_Hist$ctl01$ctl0' + str(iter),
                    b'__EVENTARGUMENT': hiddens['__EVENTARGUMENT'],
                    b'__LASTFOCUS': hiddens['__LASTFOCUS'],
                    b'__VIEWSTATE': hiddens['__VIEWSTATE'],
                    b'__VIEWSTATEGENERATOR': hiddens['__VIEWSTATEGENERATOR'],
                    b'__VIEWSTATEENCRYPTED': hiddens['__VIEWSTATEENCRYPTED'],
                    b'__EVENTVALIDATION': hiddens['__EVENTVALIDATION'],
                    b'ctl07$ddl_AMC': amc['value'],
                    b'ctl07$ddl_Scheme': scheme['value']
                    # b'ctl07$btn_submit': 'Get Records'
                   }
                dat =parse.urlencode(load)
                br.open(url, dat)
                table_soup = BeautifulSoup(br.response().read(), 'html.parser')

                # hidden = table_soup.find_all('input', {"type": "hidden"})
                # for hid in hidden:
                    # print('Updating Hiddens:', {hid['id']: hid['value']})
                #     hiddens.update({hid['id']: hid['value']})
                rows = table_soup.find_all('table', {'id': 'ctl07_dg_Div_Hist'})[0].find_all('tr')
                for row in rows[2:-1]:
                    tds = row.find_all('td')
                    row_data = (tds[0].text, tds[1].text, tds[2].text)
                    # print('        ', row_data)
                    data[amc.text][scheme.text].append(row_data)

                iter += 1
    with open('mf_div_data.json', 'w') as fp:
        json.dump(data, fp)


dump_div_data()
