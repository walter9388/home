import urllib.request
import numpy as np
import re
import datetime
import pandas as pd

from bs4 import BeautifulSoup

def get_fixture_urls(team,year,top_url= r'https://www.worldfootball.net'):
    report_urls = []
    season_url = r'https://www.worldfootball.net/teams/'+team.lower().replace(' ','-')+'/'+year+'/3/'
    html = urllib.request.urlopen(season_url).read()
    soup = BeautifulSoup(html, "html.parser")
    for i in soup.find_all('a', href=True):
        if len(re.split(r'<a href="/report', str(i))) > 1:
            if len(re.split(r'<a href="/report/freundschaft', str(i))) == 1:  # remove friendlies
                report_urls.append(top_url + re.split(r'<a href="(.*?)" title=', str(i))[1])
    return report_urls

class football_match():

    def __init__(self,url):
        self.url=url
        text = self.get_webtext()

        # self.text=text

        self.get_fixture_details(text[1])
        print(self.match_data['season'] + ' ' + self.match_data['competition'] + ': ' + self.match_data['home_team'] + ' vs ' + self.match_data['away_team'])
        if len(re.split(r'([0-9]:[0-9])', text[7]))>1: #handle games which haven't taken place yet
            self.match_data['kickoff_dt'] = datetime.datetime.strptime(re.split(r', (.*?) Clock', text[4])[1], '%d. %B %Y%H:%M')
            self.match_data['kickoff_str'] = self.match_data['kickoff_dt'].strftime('%d/%m/%Y %H:%M')
            self.get_goals_details(text)
            if not hasattr(self, 'no_lineup'):
                self.get_lineups(text)
            self.get_match_details(text)

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
        strfind4 = lambda strr: (re.fullmatch('^[^0-9]+$', strr) is not None) & ('Incidents' != strr) & ('---' != strr) & ('Penalty shootout' != strr) & (not strfind3('scores',(rm_space('asdf '+strr)).split()[-1])) & (not strfind3('misses',(rm_space('asdf '+strr)).split()[-1]))
        strfind3=lambda strr, strr2: re.fullmatch(strr, strr2) is not None

        if len(strfind2(text))==0: # when no line up is provided
            self.no_lineup = True
            temptext = text[strfind(text, 'goals')[0] + 1: np.where([len(re.split('Manager: ', text[i]))>1 for i in range(len(text))])[0][0]]
        else:
            temptext = text[strfind(text, 'goals')[0] + 1: min(np.where([strfind4(text[i]) for i in range(len(text))])[0][np.where(np.where([strfind4(text[i]) for i in range(len(text))])[0] > (strfind(text, 'goals')[0] + 1))[0][0]]+1,strfind2(text)[0])]
        if (strfind4(temptext[-1])) & (temptext[-1]!='none') & (not strfind3('scores',rm_space(temptext[-1]).split()[-1])) & (not strfind3('misses',rm_space(temptext[-1]).split()[-1])):
            self.temp_homegoaliename=re.fullmatch('^[^0-9]+$', temptext[-1])[0]
            temptext.pop()

        self.match_data['penalty_shootout'] = False
        if temptext[0] == 'none':
            self.match_data['score_fulltime'] = '0 : 0'
        else:
            # check if there was a incident
            if len(strfind(temptext, 'Incidents')) != 0:
                tempinc=[]
                for i in range(len(temptext[strfind(temptext, 'Incidents')[0]+1:])):
                    tempp=re.split(r'\((.* ?)\)',temptext[strfind(temptext, 'Incidents')[0]+1+i])
                    tempinc.append({
                        'event': rm_space(tempp[0]),
                        'minute': int(rm_space(tempp[1][:-1])),
                    })
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
            # else:
                # self.match_data['penalty_shootout'] = False

            goallist = []
            for i in range(0, len(temptext), 2):
                goallist.append({
                    'score': temptext[i],
                    'scorer': re.split(r'(.*?) [0-9]', temptext[i + 1])[1],
                    'minute': int(re.split(r'([0-9][0-9][0-9]|[0-9][0-9]|[0-9])', temptext[i + 1])[1])
                    })
                if len(re.split(r'/ (.*?)\t', temptext[i + 1]))>1:
                    goallist[-1]['method'] = re.split(r'/ (.*?)\t', temptext[i + 1])[1]
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
                'player_name': rm_space(listt[1])
            }
            if len(listt[0])>0:
                tempdict['player_num'] = int(listt[0])
            card=[tempdict['player_name'] == self.match_data['cards'][k]['player_name'] for k in range(len(self.match_data['cards']))]
            if any(card):
                cardmin=listt.pop(2)
                if cardmin!=' ':
                    if cardmin.count('\'')==2: # for if a player gets a yellow then a straight red
                        self.match_data['cards'][card.index(True)]['card_type'] = 'yr'
                        self.match_data['cards'][card.index(True)]['card_time_0'] = int(rm_space(cardmin).split()[0][:-1])
                        self.match_data['cards'][card.index(True)]['card_time'] = int(rm_space(cardmin).split()[1][:-1])
                    else:
                        self.match_data['cards'][card.index(True)]['card_time'] = int(rm_space(cardmin)[:-1])
            # if (~subs) & (len(listt)==4): # special case for a sub which is subbed off
            #     tempdict['subbed_on'] = int(rm_space(listt.pop(2))[:-1])
            if len(listt)==3:
                if subs:
                    tempdict['subbed_off'] = int(rm_space(listt[2])[:-1])
                else:
                    # special case for a sub which is subbed off
                    if re.fullmatch(r'([0-9][0-9][0-9]|[0-9][0-9]|[0-9])\' ([0-9][0-9][0-9]|[0-9][0-9]|[0-9])\'',rm_space(listt[2])) is not None:
                        tempdict['subbed_off'] = int(rm_space(listt[2]).split()[1][:-1])
                        listt[2]=rm_space(listt[2]).split()[0]
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
            d = [rm_space(re.split(r'title="(.* ?)">', str(b[k]))[1])  for k in range(len(b)) if c[k]]
            return d

        rm_space_s = lambda strr: strr[1:] if strr[0] == ' ' else strr
        rm_space = lambda strr: rm_space_s(strr)[:-1] if rm_space_s(strr)[-1] == ' ' else rm_space_s(strr)

        strfind2 = lambda listt: list(np.where(
            [(re.fullmatch('[0-9]{,2}', listt[i]) is not None) | (re.fullmatch('Substitutes', listt[i]) is not None) for
             i in range(len(listt))])[0])
        strfind4 = lambda listt: list(np.where(
            [((re.fullmatch('[a-zA-Z]', listt[i+1][0]) is not None) & (re.fullmatch('\'', listt[i][-1]) is None)) | (re.fullmatch('Substitutes', listt[i]) is not None) for
             i in range(len(listt)-1)])[0])
        strfind3 = lambda listt: list(np.where(
            [len(re.split('Manager:', listt[i]))>1 for i in range(len(listt))])[0])
        temptext = strfind2(text)
        temptext3 = strfind3(text)

        playerlist=[]
        if hasattr(self, 'temp_homegoaliename'):
            # playerlist=[['',self.temp_homegoaliename]]
            temptext=[[self.temp_homegoaliename==text[i] for i in range(len(text))].index(True)]+temptext
            del self.temp_homegoaliename
        for i in range(len(temptext)):
            if i+1==len(temptext):
                ii=temptext3[0]
            else:
                ii=temptext[i+1]
            playerlist.append(text[temptext[i]:ii])
        # find players with no numbers
        ss=lambda listt: [[len(re.split(r'[a-zA-Z]',listt[i][j]))>1 for j in range(len(listt[i]))] for i in range(len(listt))]
        while any([sum(i)>1 for i in ss(playerlist)]):
            n1, n2 = [], []
            for k in list(np.where([sum(i)>1 for i in ss(playerlist)])[0])[::-1]:
                nametemp = np.where(ss(playerlist)[k])[0][-1]
                n1 = playerlist[k][:nametemp]
                n2 = ['']+playerlist[k][nametemp:]
                playerlist=playerlist[:k]+[n1]+[n2]+playerlist[k+1:]
        if len(strfind2(playerlist[0]))==0:
            playerlist[0] = ['']+playerlist[0]
        if any([playerlist[i]==['0'] for i in range(len(playerlist))]): # removes weird website substitute 0 error
            playerlist[[playerlist[i] == ['0'] for i in range(len(playerlist))].index(True)-1].append('0\'')
            playerlist.remove(['0'])

        sublines=list(np.where([re.fullmatch('Substitutes', playerlist[i][0]) is not None for i in range(len(playerlist))])[0])

        # find which players got cards
        card_list = ['y', 'y2', 'r']
        players_with_cards=[find_players_with_cards(card_type=k) for k in card_list]
        templist = []
        for k in range(len(card_list)):
            templist=templist+[{'player_name':players_with_cards[k][kk],'card_type':card_list[k]} for kk in range(len(players_with_cards[k]))]
        self.match_data['cards']=templist

        if len(sublines)!=2:
            if sublines[0]==11:
                # no away subs
                sublines=sublines+[len(playerlist)]
            else:
                # no home subs
                sublines=sublines+sublines
        self.match_data['lineup']={
            'home_team' : [lineup(playerlist[i],subs=True) for i in range(11)],
            'home_team_subs': [lineup(playerlist[i], subs=False) for i in range(sublines[0] + 1, sublines[1] - 11)],
            'away_team': [lineup(playerlist[i], subs=True) for i in range(sublines[1] - 11, sublines[1])],
            'away_team_subs': [lineup(playerlist[i], subs=False) for i in range(sublines[1] + 1, len(playerlist))],
        }
        # # fix card structure
        # for i in range(len(self.match_data['cards'])):
        #     self.match_data['cards'][i]['player_name'] = self.match_data['cards'][i]['player_name'][0]

    def get_match_details(self,text):
        strfind3 = lambda listt: list(np.where(
            [len(re.split('Manager:', listt[i])) > 1 for i in range(len(listt))])[0])
        strfind4 = lambda listt: list(np.where(
            [(re.fullmatch(' ', listt[i]) is not None) or (re.fullmatch('Reports', listt[i]) is not None) for i in
             range(len(listt))])[0])
        rm_space_s = lambda strr: strr[1:] if strr[0] == ' ' else strr
        rm_space = lambda strr: rm_space_s(strr[:-1]) if strr[-1] == ' ' else rm_space_s(strr)

        temptext=text[strfind3(text)[0]:strfind4(text)[np.where([strfind4(text)[i]>strfind3(text)[0] for i in range(len(strfind4(text)))])[0][0]]]
        if len(temptext) > 1:
            self.match_data['home_manager'] = rm_space(re.split('Manager: ', temptext[0])[1])
            self.match_data['away_manager'] = rm_space(re.split('Manager: ', temptext[1])[1])
        if len(temptext) > 2:
            self.match_data['stadium']={
                'name': rm_space(re.split(r'\((.* ?)\)',temptext[2])[0]),
                'location': rm_space(re.split(r'\((.* ?)\)',temptext[2])[1])
            }
        if len(temptext) > 3:
            self.match_data['attendance'] = int(temptext[3].split()[0].replace('.', ''))
        if len(temptext) > 4:
            templist = []
            for i in temptext[4:]:
                templist.append({
                    'name': rm_space(re.split(r'\((.* ?)\)',i)[0]),
                    'nationality': rm_space(re.split(r'\((.* ?)\)',i)[1])
                })
            self.match_data['officals']=templist



    # def to_pandas_all(self,*df_old):
    #     df = pd.Series(dtype=object)
    #
    #     for i in self.match_data.keys():
    #         if isinstance(self.match_data[i], bool) or isinstance(self.match_data[i], int):
    #             pass
    #         elif (isinstance(self.match_data[i], datetime.datetime)) or (len(self.match_data[i]) == 0):
    #             continue
    #
    #         if isinstance(self.match_data[i], list):
    #             df2 = pd.DataFrame(self.match_data[i]).T.stack()
    #             df2.index = pd.MultiIndex.from_tuples([tuple([i]+list(a)) for a in df2.index])
    #             df = df.append(df2)
    #         elif isinstance(self.match_data[i], dict):
    #             for ii in self.match_data[i].keys():
    #                 if isinstance(self.match_data[i][ii], bool) or isinstance(self.match_data[i][ii], int):
    #                     pass
    #                 elif (isinstance(self.match_data[i][ii], datetime.datetime)) or (len(self.match_data[i][ii]) == 0):
    #                     continue
    #
    #                 if isinstance(self.match_data[i][ii], list):
    #                     df2 = pd.DataFrame(self.match_data[i][ii]).T.stack()
    #                     df2.index = pd.MultiIndex.from_tuples([tuple([i,ii] + list(a)) for a in df2.index])
    #                     df = df.append(df2)
    #                 elif isinstance(self.match_data[i][ii], dict):
    #                     pass
    #                 else:
    #                     df = df.append(pd.Series(index=[(i,ii)], data=self.match_data[i][ii]))
    #         else:
    #             df = df.append(pd.Series(index=[i],data=self.match_data[i]))
    #
    #
    #
    #     if len(df_old)>0:
    #         if isinstance(df_old[0], pd.Series):
    #             df = pd.concat([df_old[0],df],axis=1).T
    #         elif isinstance(df_old[0], pd.DataFrame):
    #             df = pd.concat([df_old[0],df.to_frame().T],axis=0,sort=True).reset_index(drop=True)
    #
    #             priority_cols=[
    #                 'home_team',
    #                 'away_team',
    #                 'competition',
    #                 'round',
    #                 'season',
    #                 'kickoff_str',
    #                 'score_fulltime',
    #                 'home_manager',
    #                 'away_manager'
    #             ]
    #             cols = list(df.columns.values)  # Make a list of all of the columns in the df
    #             [cols.pop(cols.index(priority_cols[i])) for i in range(len(priority_cols))]  # Remove b from list
    #             df = df[priority_cols + cols]
    #
    #     return df

    def to_pandas_players(self,*df_old):
        # lineups
        key = 'lineup'
        if key in self.match_data.keys():
            key2 = list(self.match_data[key].keys())
            temp = []
            for i in range(0, 4, 2):
                temp.append(pd.concat(
                    [pd.DataFrame(self.match_data[key][key2[i]]), pd.DataFrame(self.match_data[key][key2[i + 1]])],
                    ignore_index=True))
                # temp[-1].insert(loc=0, column='home_away', value = key2[i][:4])
                temp[-1].index = [key2[i][:4] + '_' + '{:02d}'.format(ii) for ii in range(temp[-1].shape[0])]
            df = pd.concat(temp, axis=0).T
        else:
            df=pd.DataFrame([[],[]])

        # cards
        key = 'cards'
        if key in self.match_data.keys():
            temp = pd.DataFrame(self.match_data[key]).T
            if len(temp)>0:
                df = pd.merge(df.T, temp.T, how='left', on='player_name', right_index=True).T

        df = df.T.stack()

        # goals
        key='goals'
        if key in self.match_data.keys():
            df2 = pd.DataFrame(self.match_data[key]).T
            df2.columns = ['goal_' + '{:02d}'.format(i) for i in range(df2.shape[1])]
            df2=df2.drop('goalnum')
            df=df.append(df2.T.stack())

        # penalty_shootout
        key='ps_goals'
        if self.match_data['penalty_shootout']:
            df3=pd.DataFrame(self.match_data[key]).T
            df3.columns=['ps_'+'{:02d}'.format(i) for i in range(df3.shape[1])]
            df=df.append(df3.T.stack())

        # incidences & officals
        for ii in ['incidence','officals']:
            if ii in self.match_data.keys():
                df4=pd.DataFrame(self.match_data[ii]).T
                df4.columns = [ii + '_' + '{:02d}'.format(i) for i in range(df4.shape[1])]
                df = df.append(df4.T.stack())

        dd=lambda data,n1,n2: pd.Series(data=data, index=pd.MultiIndex.from_tuples([(n1, n2)]))

        ll=lambda x: (not isinstance(x,list)) & (not isinstance(x,dict)) & (not isinstance(x,datetime.datetime))
        for ii in list(self.match_data.keys()):
            if ll(self.match_data[ii]):
                df=df.append(dd(self.match_data[ii], '_', ii))

        # stadium
        if 'stadium' in self.match_data.keys():
            for ii in list(self.match_data['stadium'].keys()):
                df=df.append(dd(self.match_data['stadium'][ii],'stadium',ii))

        df=df.to_frame().T

        if len(df_old) > 0:
            df = df_old[0].append(df, ignore_index=True)

            priority_cols = [
                'home_team',
                'away_team',
                'competition',
                'round',
                'season',
                'kickoff_str',
                'score_fulltime',
                'penalty_shootout',
                'home_manager',
                'away_manager'
            ]
            priority_cols = [('_', priority_cols[i]) for i in range(len(priority_cols)) if
                             ('_', priority_cols[i]) in list(df.columns.values)]

            flatten = lambda l: [item for sublist in l for item in sublist]
            ss=lambda strr: [list(df.columns.values)[j] for j in list(np.where([len(re.split(strr,list(df.columns.values)[i][0]))>1 for i in range(df.shape[1])])[0])]
            priority_cols2=[
                'home',
                'away',
                'goal',
                'incidence',
                'ps',
                'officals',
                'stadium'
            ]
            priority_cols2 = flatten([ss(priority_cols2[i]) for i in range(len(priority_cols2)) if len(ss(priority_cols2[i]))!=0])

            cols = list(df.columns.values)  # Make a list of all of the columns in the df
            for ii in [priority_cols,priority_cols2]:
                [cols.pop(cols.index(ii[i])) for i in range(len(ii))]  # Remove b from list
            df = df[priority_cols + priority_cols2 + cols]

        return df



if __name__ == "__main__":
    testurls=[
        r'https://www.worldfootball.net/report/championship-2018-2019-sheffield-united-millwall-fc/',
        r'https://www.worldfootball.net/report/championship-2017-2018-sheffield-united-brentford-fc/',
        r'https://www.worldfootball.net/report/league-cup-2018-2019-1-runde-sheffield-united-hull-city/',
        r'https://www.worldfootball.net/report/league-cup-2019-2020-viertelfinale-oxford-united-manchester-city/',
        r'https://www.worldfootball.net/report/championship-2018-2019-sheffield-wednesday-sheffield-united/',
        r'https://www.worldfootball.net/report/champions-league-2011-2012-finale-bayern-muenchen-chelsea-fc/',
        r'https://www.worldfootball.net/report/fa-cup-2013-2014-2-runde-cambridge-united-sheffield-united/',
        r'https://www.worldfootball.net/report/fa-cup-2011-2012-1-runde-sheffield-united-oxford-united/',
        r'https://www.worldfootball.net/report/league-one-2016-2017-scunthorpe-united-sheffield-united/'
    ]
    urls=testurls

    team = 'Sheffield United'
    year = list(range(2008,2020))
    urls=[]
    for i in range(len(year)):
        urls=urls+get_fixture_urls(team, str(year[i]))
    for i in range(len(urls)):
        a=football_match(urls[i])
        if i==0:
            # df = a.to_pandas_all()
            df2 = a.to_pandas_players()
        else:
            # df = a.to_pandas_all(df)
            df2 = a.to_pandas_players(df2)

    df2.to_csv(team+' '+str(min(year))+'-'+str(max(year))+'.csv',encoding='utf-8-sig')
    # df2.to_csv('test.csv', encoding='utf-8-sig')
