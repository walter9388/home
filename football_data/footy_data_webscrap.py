import urllib.request
import numpy as np
import re
import datetime
import pandas as pd

from bs4 import BeautifulSoup


class football_match():

    def __init__(self,url):
        self.url=url
        text = self.get_webtext()

        self.text=text

        self.get_fixture_details(text[1])
        self.match_data['kickoff_dt'] = datetime.datetime.strptime(re.split(r', (.*?) Clock', text[4])[1], '%d. %B %Y%H:%M')
        self.match_data['kickoff_str'] = self.match_data['kickoff_dt'].strftime('%d/%m/%Y %H:%M')
        # self.match_data['score'] = re.split(r'([0-9]:[0-9])', text[7])[1]
        self.get_match_details(text)

        self.get_goals_details(text)
        self.get_lineups(text)

    def get_webtext(self):
        html = urllib.request.urlopen(self.url).read()
        self.soup = BeautifulSoup(html, "html.parser")
        for script in self.soup(["script", "style"]):
            script.extract()  # rip it out
        text = self.soup.get_text()
        text = [text.split('\n')[i] for i in range(len(text.split('\n'))) if text.split('\n')[i] != '']
        strfind = lambda listt, strr: np.where([listt[i] == strr for i in range(len(listt))])[0][0]
        text = text[strfind(text, 'Head to head'): strfind(text, 'Impressum – Legal Notice')]
        return text

    def get_fixture_details(self,strr):
        home_team, away_team = strr[strr.find(',') + 2:].split('\t')[0].split(' - ')
        dictt = {'home_team' : home_team, 'away_team' : away_team}
        dictt['competition'] = re.split(r'Slideshow (.*?) [0-9]{4}/[0-9]{4}', strr)[1]
        dictt['season'] = re.split(r'([0-9]{4}/[0-9]{4})', strr)[1]
        dictt['round'] = re.split(r'[0-9]{4}/[0-9]{4} (.*?),',strr)[1]
        self.match_data=dictt

    def get_goals_details(self, text):
        rm_space_s = lambda strr: strr[1:] if strr[0] == ' ' else strr
        rm_space = lambda strr: rm_space_s(strr)[:-1] if rm_space_s(strr)[-1] == ' ' else rm_space_s(strr)
        strfind = lambda listt, strr: list(np.where([listt[i] == strr for i in range(len(listt))])[0])
        strfind2 = lambda listt: list(
            np.where([re.fullmatch('[0-9]{,2}', listt[i]) is not None for i in range(len(listt))])[0])
        temptext = text[strfind(text, 'goals')[0] + 1: strfind2(text)[0]]
        if temptext[0] == 'none':
            self.match_data['score_fulltime'] = '0 : 0'
        else:
            # check if there was a incident
            if len(strfind(temptext, 'Incidents')) != 0:
                tempinc=[]
                for i in range(len(temptext[strfind(temptext, 'Incidents')[0]+1:])):
                    tempp=re.split(r'\((.* ?)\)',temptext[strfind(temptext, 'Incidents')[0]+1+i])
                    tempinc={
                        'event': rm_space(tempp[0]),
                        'minute': int(rm_space(tempp[1][:-1])),
                    }
                self.match_data['incidence']=tempinc
                temptext = temptext[:strfind(temptext, 'Incidents')[0]]

            # check if there was a penatly shootout
            if len(strfind(temptext, 'Penalty shootout')) != 0:
                self.match_data['penalty_shootout'] = True
                goallist = []
                for i in range(strfind(temptext, 'Penalty shootout')[0] + 1, len(temptext), 2):
                    goallist.append({
                        'score': temptext[i],
                        'taker': rm_space(' '.join(re.split(r'(.*?) ', temptext[i + 1])[-4::2])),
                        'scored?': temptext[i] != '---',
                    })
                self.match_data['ps_goals'] = goallist
                self.match_data['score_fulltime'] = temptext[i]
                temptext = temptext[:strfind(temptext, 'Penalty shootout')[0]]
            else:
                self.match_data['penalty_shootout'] = False

            goallist = []
            for i in range(0, len(temptext), 2):
                goallist.append({
                    'score': temptext[i],
                    'scorer': re.split(r'(.*?) [0-9]', temptext[i + 1])[1],
                    'minute': int(re.split(r'([0-9][0-9][0-9]|[0-9][0-9]|[0-9])', temptext[i + 1])[1]),
                    'method': re.split(r'/ (.*?)\t', temptext[i + 1])[1],
                })
                goallist[-1]['goalnum']=len(goallist)
                if len(re.split(r'\((.* ?)\)', temptext[i + 1])) > 1:
                    goallist[-1]['assist']= re.split(r'\((.* ?)\)', temptext[i + 1])[1]
            self.match_data['goals'] = goallist
            self.match_data['score_fulltime'] = temptext[i]
            if self.match_data['penalty_shootout']:
                self.match_data['score_fulltime']=self.match_data['score_fulltime'] + ' (' + self.match_data['ps_goals'][-1]['score'] +')'

    def get_lineups(self,text):
        def lineup(listt,subs=True):
            tempdict={
                'player_num':int(listt[0]),
                'player_name': rm_space(listt[1])
            }
            card=[tempdict['player_name'] == self.match_data['cards'][k]['player_name'] for k in range(len(self.match_data['cards']))]
            if any(card):
                self.match_data['cards'][card.index(True)]['card_time'] = int(rm_space(listt.pop(2))[:-1])
            if len(listt)==3:
                if subs:
                    tempdict['subbed_off'] = int(rm_space(listt[2])[:-1])
                else:
                    tempdict['subbed_on'] = int(rm_space(listt[2])[:-1])
            return tempdict

        def find_players_with_cards(card_type='y'):
            card_type_dict = {
                card_list[0]: 'yellow',
                card_list[1]: 'Second yellow',
                card_list[2]: 'red'
            }
            a = lambda cls_name: list(self.soup.find_all(class_=cls_name))
            b = a('hell') + a('dunkel')
            c = [len(re.split(r'img alt="' + card_type_dict[card_type] + '"', str(b[k]))) > 1 for k in range(len(b))]
            d = [rm_space(re.split(r'title="(.* ?)">', str(b[k]))[1]) for k in range(len(b)) if c[k]]
            return d

        rm_space_s = lambda strr: strr[1:] if strr[0] == ' ' else strr
        rm_space = lambda strr: rm_space_s(strr)[:-1] if rm_space_s(strr)[-1] == ' ' else rm_space_s(strr)

        strfind2 = lambda listt: list(np.where(
            [(re.fullmatch('[0-9]{,2}', listt[i]) is not None) | (re.fullmatch('Substitutes', listt[i]) is not None) for
             i in range(len(listt))])[0])
        strfind3 = lambda listt: list(np.where(
            [len(re.split('Manager:', listt[i]))>1 for i in range(len(listt))])[0])
        temptext = strfind2(text)
        temptext3 = strfind3(text)

        playerlist=[]
        for i in range(len(temptext)):
            if i+1==len(temptext):
                ii=temptext3[0]
            else:
                ii=temptext[i+1]
            playerlist.append(text[temptext[i]:ii])
        sublines=list(np.where([re.fullmatch('Substitutes', playerlist[i][0]) is not None for i in range(len(playerlist))])[0])

        # find which players got cards
        card_list = ['y', 'y2', 'r']
        players_with_cards=[find_players_with_cards(card_type=k) for k in card_list]
        templist = []
        for k in range(len(card_list)):
            templist=templist+[{'player_name':players_with_cards[k][kk],'card_type':card_list[k]} for kk in range(len(players_with_cards[k]))]
        self.match_data['cards']=templist

        self.match_data['lineup']={
            'home_team' : [lineup(playerlist[i],subs=True) for i in range(11)],
            'home_team_subs': [lineup(playerlist[i], subs=False) for i in range(sublines[0] + 1, sublines[1] - 11)],
            'away_team': [lineup(playerlist[i], subs=True) for i in range(sublines[1] - 11, sublines[1])],
            'away_team_subs': [lineup(playerlist[i], subs=False) for i in range(sublines[1] + 1, len(playerlist))],
        }


    def get_match_details(self,text):
        strfind3 = lambda listt: list(np.where(
            [len(re.split('Manager:', listt[i])) > 1 for i in range(len(listt))])[0])
        strfind4 = lambda listt: list(np.where(
            [(re.fullmatch(' ', listt[i]) is not None) or (re.fullmatch('Reports', listt[i]) is not None) for i in
             range(len(listt))])[0])
        rm_space_s = lambda strr: strr[1:] if strr[0] == ' ' else strr
        rm_space = lambda strr: rm_space_s(strr[:-1]) if strr[-1] == ' ' else rm_space_s(strr)

        temptext=text[strfind3(text)[0]:]
        self.match_data['home_manager'] = rm_space(re.split('Manager: ', temptext[0])[1])
        self.match_data['away_manager'] = rm_space(re.split('Manager: ', temptext[1])[1])
        self.match_data['stadium']={
            'name': rm_space(re.split(r'\((.* ?)\)',temptext[2])[0]),
            'location': rm_space(re.split(r'\((.* ?)\)',temptext[2])[1])
        }
        self.match_data['attendance'] = int(temptext[3].split()[0].replace('.', ''))
        templist = []
        for i in temptext[4:strfind4(temptext)[0]]:
            templist.append({
                'name': rm_space(re.split(r'\((.* ?)\)',i)[0]),
                'nationality': rm_space(re.split(r'\((.* ?)\)',i)[1])
            })
        self.match_data['officals']=templist



    def to_pandas(self,*df_old):
        df = pd.Series(dtype=object)

        # for i in self.match_data.keys():
        #     if isinstance(self.match_data[i],list):
        #         for ii in range(len(self.match_data[i])):
        #             if isinstance(self.match_data[i][ii], list):
        #                 # for iii in range(len(self.match_data[i][iii])):
        #                 pass
        #             elif isinstance(self.match_data[i][ii], dict):
        #                 df[i + '_' + str] = self.match_data[i][ii]
        #             else:
        #                 df[i + '_' + str(ii)] = self.match_data[i][ii]
        #     elif: isinstance(self.match_data[i],dict):
        #         for ii in range(len(self.match_data[i])):
        #             if isinstance(self.match_data[i][ii], list):
        #                 # for iii in range(len(self.match_data[i][iii])):
        #                 pass
        #             elif: isinstance(self.match_data[i][ii], dict):
        #
        #                 df[i][ii]
        #     else:
        #         df[i] = self.match_data[i]

        for i in self.match_data.keys():
            if isinstance(self.match_data[i], bool) or isinstance(self.match_data[i], int):
                pass
            elif (isinstance(self.match_data[i], datetime.datetime)) or (len(self.match_data[i]) == 0):
                continue

            if isinstance(self.match_data[i], list):
                df2 = pd.DataFrame(self.match_data[i]).T.stack()
                df2.index = pd.MultiIndex.from_tuples([tuple([i]+list(a)) for a in df2.index])
                df = df.append(df2)
            elif isinstance(self.match_data[i], dict):
                for ii in self.match_data[i].keys():
                    if isinstance(self.match_data[i][ii], bool) or isinstance(self.match_data[i][ii], int):
                        pass
                    elif (isinstance(self.match_data[i][ii], datetime.datetime)) or (len(self.match_data[i][ii]) == 0):
                        continue

                    if isinstance(self.match_data[i][ii], list):
                        df2 = pd.DataFrame(self.match_data[i][ii]).T.stack()
                        df2.index = pd.MultiIndex.from_tuples([tuple([i,ii] + list(a)) for a in df2.index])
                        df = df.append(df2)
                    elif isinstance(self.match_data[i][ii], dict):
                        pass
                    else:
                        df = df.append(pd.Series(index=[(i,ii)], data=self.match_data[i][ii]))
            else:
                df = df.append(pd.Series(index=[i],data=self.match_data[i]))



        if len(df_old)>0:
            if isinstance(df_old[0], pd.Series):
                df = pd.concat([df_old[0],df],axis=1).T
            elif isinstance(df_old[0], pd.DataFrame):
                df = pd.concat([df_old[0],df.to_frame().T],axis=0,sort=True).reset_index(drop=True)

                priority_cols=[
                    'home_team',
                    'away_team',
                    'competition',
                    'round',
                    'season',
                    'kickoff_str',
                    'score_fulltime',
                    'home_manager',
                    'away_manager'
                ]
                cols = list(df.columns.values)  # Make a list of all of the columns in the df
                [cols.pop(cols.index(priority_cols[i])) for i in range(len(priority_cols))]  # Remove b from list
                df = df[priority_cols + cols]





        return df



if __name__ == "__main__":
    testurls=[
        r'https://www.worldfootball.net/report/championship-2018-2019-sheffield-united-millwall-fc/',
        r'https://www.worldfootball.net/report/championship-2017-2018-sheffield-united-brentford-fc/',
        r'https://www.worldfootball.net/report/league-cup-2018-2019-1-runde-sheffield-united-hull-city/',
        r'https://www.worldfootball.net/report/league-cup-2019-2020-viertelfinale-oxford-united-manchester-city/',
        r'https://www.worldfootball.net/report/championship-2018-2019-sheffield-wednesday-sheffield-united/',
        r'https://www.worldfootball.net/report/champions-league-2011-2012-finale-bayern-muenchen-chelsea-fc/'
    ]

    for i in range(len(testurls)):
        a=football_match(testurls[i])
        if i==0:
            df = a.to_pandas()
        else:
            df = a.to_pandas(df)

    print(df)