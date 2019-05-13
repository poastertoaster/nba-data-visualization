import pandas as pd
import numpy as np
import nba_api
import requests
from matplotlib import pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import playerprofilev2

colors = {
	'Atlanta Hawks': ['#e03a3e', '#C1D32F'],
	'Boston Celtics': ['#007A33', '#BA9653'],
	'Brooklyn Nets': ['#000000', '#FFFFFF'],
	'Charlotte Hornets': ['#00788C', '#1d1160'],
	'Chicago Bulls': ['#CE1141', '#000000'],
	'Cleveland Cavaliers': ['#6F263D', '#FFB81C'],
	'Dallas Mavericks': ['#002B5e', '#B8C4CA'],
	'Denver Nuggets': ['#0E2240', '#FEC524'],
	'Detroit Pistons': ['#C8102E', '#006BB6'],
	'Golden State Warriors': ['#006BB6', '#FDB927'],
	'Houston Rockets': ['#CE1141', '#C4CED4'],
	'Indiana Pacers': ['#FDBB30', '#002D62'],
	'Los Angeles Clippers': ['#c8102E', '#1d428a'],
	'Los Angeles Lakers': ['#FDB927', '#552583'],
	'Memphis Grizzlies': ['#5D76A9', '#12173F'],
	'Miami Heat': ['#98002E', '#F9A01B'],
	'Milwaukee Bucks': ['#00471B', '#EEE1C6'],
	'Minnesota Timberwolves': ['#236192', '#0C2340'],
	'New Orleans Pelicans': ['#0C2340', '#C8102E'],
	'New York Knicks': ['#006BB6', '#F58426'],
	'Oklahoma City Thunder': ['#007ac1', '#ef3b24'],
	'Orlando Magic': ['#0077c0', '#C4ced4'],
	'Philadelphia 76ers': ['#006bb6', '#c4ced4'],
	'Phoenix Suns': ['#1d1160', '#e56020'],
	'Portland Trail Blazers': ['#E03A3E', '#000000'],
	'Sacramento Kings': ['#5a2d81', '#FFFFFF'],
	'San Antonio Spurs': ['#000000', '#c4ced4'],
	'Toronto Raptors': ['#ce1141', '#000000'],
	'Utah Jazz': ['#002B5C', '#F9A01B'],
	'Washington Wizards': ['#e31837', '#002B5C']
}

#Get the roster of the team
allTeams = teams.get_teams()
for team in allTeams:
	print(' --------------------------\n', team['full_name'], 'started.\n', '--------------------------')
	rosterData = commonteamroster.CommonTeamRoster(season='2018-19', team_id=team['id'])
	roster = rosterData.common_team_roster.get_data_frame()

	#Set the appearance of the chart
	plt.figure(1, figsize=(14, 8))
	axScatter = plt.axes()
	axScatter.figure.set_facecolor(colors[team['full_name']][0])
	axScatter.set_facecolor((1,1,1,0.8))
	axScatter.tick_params(color=colors[team['full_name']][1], labelcolor=colors[team['full_name']][1])
	for spine in axScatter.spines.values():
		spine.set_edgecolor(colors[team['full_name']][1])

	#Go through each player on the roster
	for index, x in roster.iterrows():
		#Get the player's stats
		profile = playerprofilev2.PlayerProfileV2(per_mode36='PerGame', player_id=x.PLAYER_ID)
		stats = profile.season_totals_regular_season.get_data_frame()

		#Get the player's headshot
		headshotTeam = requests.get(f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{x.TeamID}/2018/260x190/{x.PLAYER_ID}.png')
		if headshotTeam.status_code != 403:
			headshot = plt.imread(f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{x.TeamID}/2018/260x190/{x.PLAYER_ID}.png', format='png')
		else:
			headshotLatest = requests.get(f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{x.PLAYER_ID}.png')
			if headshotLatest.status_code != 403:
				headshot = plt.imread(f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{x.PLAYER_ID}.png', format='png')
			else:
				headshot = plt.imread(f'https://stats.nba.com/media/img/league/nba-headshot-fallback.png')
		headshots = OffsetImage(headshot, zoom=0.2, interpolation='quadric')
		
		#Get stats for only this season and plot the player
		seasonStats = stats[stats.SEASON_ID == '2018-19']
		if(len(seasonStats) != 0):
			print(x.PLAYER, 'loaded.')
			headshotPlot = AnnotationBbox(headshots, (seasonStats.iloc[len(seasonStats)-1].MIN, seasonStats.iloc[len(seasonStats)-1].PTS), frameon=False)
			axScatter.add_artist(headshotPlot)
		else:
			print(x.PLAYER, 'did not play this season.')

	axScatter.set_xlim((0, 40))
	axScatter.set_ylim((0, 40))
	axScatter.set_xlabel('Minutes per game', color=colors[team['full_name']][1]).set_weight('bold')
	axScatter.set_ylabel('Points per game', color=colors[team['full_name']][1]).set_weight('bold')
	axScatter.set_title(team['full_name'], color=colors[team['full_name']][1]).set_weight('bold')

	plt.savefig(f"{team['full_name']}", facecolor=colors[team['full_name']][0])
	plt.clf()