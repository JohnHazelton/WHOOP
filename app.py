# Pre-processing:
import pandas as pd
import numpy as np

# Stats/Analytics:
from datetime import datetime
from datetime import timedelta
import pytz

# Visualization:
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash import Dash
#from dash import dcc
#from dash import html
import dash_core_components as dcc
import dash_html_components as html
#from jupyter_dash import JupyterDash
#from dash.dependencies import Input, Output
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']





############################# LOAD DATA ##########################
###### (change path when testing locally vs in production) #######

#Local path:
local_path = 'C:/Users/John/OneDrive/Documents/Professional/Coding/STRAVA/activity_data.csv'

#Pythonanywhere.com path:
pythonanywhere_path = '/home/johnhazelton/mysite/data/activity_data.csv'


activities = pd.read_csv(pythonanywhere_path)
#activities = pd.read_csv(local_path)


# Reduced feature set:
cols = ['upload_id', 'start_date_local', 'name', 'type', 'distance', 'moving_time', 
         'elapsed_time', 'average_speed', 'max_speed', 'average_heartrate', 
         'max_heartrate', 'average_cadence', 'total_elevation_gain'
       ]

activities = activities[cols]

#Convert Date column to datetime, split into columns for time, month, year:
activities['start_datetime'] = pd.to_datetime(activities['start_date_local'])
activities['time'] = activities['start_datetime'].dt.time
activities['year'] = pd.to_datetime(activities['start_datetime']).dt.year
activities['month'] = pd.to_datetime(activities['start_datetime']).dt.month
activities['week'] = pd.to_datetime(activities['start_datetime']).dt.isocalendar().week
activities['date'] = activities['start_datetime'].dt.date
activities = activities.set_index('start_datetime')

# Convert distances, times, & speeds to miles, minutes, and pace (min/mile)
activities['distance'] = activities['distance'] / 1609
activities['moving_time'] = activities['moving_time'] / 60
activities['average_pace'] = activities['moving_time'] / activities['distance']

# Convert months to categorical 
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
for i in range(len(activities)):
  activities.month.iloc[i] = months[activities.month.iloc[i] - 1]

activities.month = activities.month.astype('category').cat.set_categories(months)



######################### STATS & CALCULATIONS ###################
runs = activities[activities.type == 'Run']
runs_per_week = runs.groupby('week').size()

mileage = activities[activities.type == 'Run']
mileage_per_week = runs.groupby('week').sum()['distance']

lifts = activities[activities.type == 'WeightTraining']
lifts_per_week = lifts.groupby('week').size()


# Calculate this week's totals, averages, etc.
# Initialize variables:
last_runs = 0
current_runs = 0

last_mileage = 0
current_mileage = 0

last_lifts = 0
current_lifts = 0

last_calories = 0
current_calories = 0

for i in activities.index:
  start_current_week = datetime.now(pytz.UTC) - timedelta(datetime.today().weekday())
  start_last_week = start_current_week - timedelta(7)

  if (i >= start_current_week):
    if (activities.type[i] == 'Run'):
      current_runs += 1
      current_mileage += activities.distance[i]
    elif (activities.type[i] == 'WeightTraining'):
      current_lifts += 1
  elif (i >= start_last_week):
    if (activities.type[i] == 'Run'):
      last_runs += 1
      last_mileage += activities.distance[i]
    elif (activities.type[i] == 'WeightTraining'):
      last_lifts += 1
  else:
    break


## THIS WEEK'S STATS & MOVEMENT FROM LAST WEEK:
change_runs = last_runs - current_runs
change_runs_text = str(change_runs) + ' (' + str(round(100*(abs(change_runs)/last_runs),2)) + '%)'

change_mileage = last_mileage - current_mileage
change_mileage_text = str(round(change_mileage,2)) + ' (' + str(round(100*(abs(change_mileage)/last_mileage),2)) + '%)'

change_lifts = last_lifts - current_lifts
change_lifts_text = str(change_lifts) + ' (' + str(round(100*(abs(change_lifts)/last_lifts),2)) + '%)'


## TOTALS FOR THE YEAR SO FAR:
total_runs = len(runs[runs.index.strftime("%Y") == '2022'])
total_mileage = runs[runs.index.strftime("%Y") == '2022']['distance'].sum()
total_lifts = len(lifts[lifts.index.strftime("%Y") == '2022'])



########### CREATE PLOTLY DASHBOARD ###############

# Add styling for graphs:
colors = {
    'background': ['rgba(0,0,0,0)', '#FFFFFF'],
    'text': ['grey', '#FFFFFF']
}
fonts = {
    'primary': 'Viga'
}


intro = 'This is a dashboard displaying my personal workout, sleep, and recovery stats from the past year.'

stats_colors = {
  'positive': 'green',
  'negative': 'red',
  'neutral': 'grey'
}

if change_runs > 0 :
  change_runs_text = '+' + change_runs_text
  change_runs_color = stats_colors['positive']
elif change_runs < 0 :
  change_runs_color = stats_colors['negative']
else:
  change_runs_color = stats_colors['neutral']


if change_mileage > 0 :
  change_mileage_text = '+' + change_mileage_text
  change_mileage_color = stats_colors['positive']
elif change_mileage < 0 :
  change_mileage_color = stats_colors['negative']
else:
  change_mileage_color = stats_colors['neutral']


if change_lifts > 0 :
  change_lifts_text = '+' + change_lifts_text
  change_lifts_color = stats_colors['positive']
elif change_lifts < 0 :
  change_lifts_color = stats_colors['negative']
else:
  change_lifts_color = stats_colors['neutral']


## PLOT: CHANGE IN MILEAGE OVER THE WEEKS
mileage_plot = px.line(mileage_per_week.tail(5), height=75, width=125)

mileage_plot.update_layout(
    paper_bgcolor = colors['background'][0],
    plot_bgcolor = colors['background'][0],
    yaxis_title=None,
    xaxis_title=None,
    yaxis=None,
    grid=None,
    showlegend=False,
    font_color = colors['text'][1],
    margin=dict(l=12, r=12, t=12, b=12)
)

mileage_plot.update_xaxes(showticklabels=False)
mileage_plot.update_yaxes(showticklabels=False)


## PLOT: CHANGE IN RUNS OVER THE WEEKS
runs_plot = px.line(runs_per_week.tail(5), height=75, width=125)

runs_plot.update_layout(
    paper_bgcolor = colors['background'][0],
    plot_bgcolor = colors['background'][0],
    yaxis_title=None,
    xaxis_title=None,
    yaxis=None,
    grid=None,
    showlegend=False,
    font_color = colors['text'][1],
    margin=dict(l=12, r=12, t=12, b=12)
)

runs_plot.update_xaxes(showticklabels=False)
runs_plot.update_yaxes(showticklabels=False)


## PLOT: CHANGE IN LIFTS OVER THE WEEKS
lifts_plot = px.line(lifts_per_week.tail(5), height=75, width=125)

lifts_plot.update_layout(
    paper_bgcolor = colors['background'][0],
    plot_bgcolor = colors['background'][0],
    yaxis_title=None,
    xaxis_title=None,
    yaxis=None,
    grid=None,
    showlegend=False,
    font_color = colors['text'][1],
    margin=dict(l=12, r=12, t=12, b=12)
)

lifts_plot.update_xaxes(showticklabels=False)
lifts_plot.update_yaxes(showticklabels=False)



## PLOT BAR GRAPH OF FREQUENCY COUNTS FOR EACH ACTIVITY BY MONTH
xtab = pd.crosstab(activities.month, activities.type)

barplot = px.bar(xtab, color='type', barmode='group', height=400, width=600, 
                labels={'month':'Month', 'value':'# of Sessions'})

barplot.update_layout(
    paper_bgcolor = colors['background'][0],
    plot_bgcolor = colors['background'][0],
    #font_family = fonts['primary']
    font_color = colors['text'][0]
)



intro = 'This is a dashboard displaying my personal workout, sleep, and recovery stats from the past year.'

external_stylesheets = ['https://fonts.googleapis.com/css?family=Viga:400']


app = Dash(__name__, external_stylesheets=external_stylesheets)

app.css.config.serve_locally = True

app.layout = html.Div(
    [
        html.Div(
            children=[
            html.H1(
                className='title-text', 
                children=['Health']),
            html.H1(
                className='title-text', id='title', 
                children=['Dashboard']),
        ]),
        
        html.H3('Follow John\'s fitness progress this year!'),
        html.H3('(This site is currently going through some cosmetic changes. Check back later for updates)'),

        #html.Div(
        #    children=[
        #    #html.Div('Plotly Dash', className="app-header--title")
        #    html.H1('Workout Log'),
        #    dcc.Markdown(children = intro)
        #], style={'textAlign':'center', 'color':'white'}),

        html.Div(
            className="plot-container", id="weekly-stats",
            children=[
            html.Div(
                className="stat-container",
                children=[
                html.P('Runs'),
                html.P(className="weekly-stat", children=[round(current_runs,2)]),
                html.P(className='weekly-stat-change', children=[
                    change_runs_text], style={'color':change_runs_color})
                ]
            ),
            html.Div(
                className="stat-container-graph",
                children=[
                dcc.Graph(figure=runs_plot)
            ]),


            html.Div(
                className="stat-container",
                children=[
                html.P('Mileage'),
                html.P(className="weekly-stat", children=[round(current_mileage,2)]),
                html.P(className='weekly-stat-change', children=[
                    change_mileage_text], style={'color':change_mileage_color})
                ]
            ),
            html.Div(
                className="stat-container-graph",
                children=[
                dcc.Graph(figure=mileage_plot)
            ]),


            html.Div(
                className="stat-container",
                children=[
                html.P('Lifts'),
                html.P(className="weekly-stat", children=[current_lifts]),
                html.P(className='weekly-stat-change', children=[
                    change_lifts_text], style={'color':change_lifts_color})
            ]),
            html.Div(
                className="stat-container-graph",
                children=[
                dcc.Graph(figure=lifts_plot)
            ]),
        ]),

        html.Div(
            className="plot-container",
            children=[
            dcc.Graph(figure=barplot, style={'font-family':'Viga'}),
        ], style={'width':'600px', 'height':'400px', 'margin-left':'auto', 'margin-right':'auto'}),     

        html.Div(
            className="plot-container",
            children=[
            html.P('Runs'),
            html.P(total_runs),
            html.P('Lifts'),
            html.P(total_lifts),
            html.P('Miles'),
            html.P(total_mileage),

        ], style={'width':'300px', 'height':'400px', 'margin-left':'auto', 'margin-right':'auto'})  
    ]
)


if __name__ == '__main__': 
    app.run_server()







