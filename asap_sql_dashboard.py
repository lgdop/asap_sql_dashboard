#!/usr/local/bin/python2.7
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from app import app, server
from dotenv import load_dotenv
import os
import re
import dash_auth
import dash_table as dt
import pandas as pd
from bson import json_util
import cx_Oracle
import sqlalchemy
from sqlalchemy import create_engine
import sys
from pprint import pprint
from pymongo import MongoClient
import json

load_dotenv(dotenv_path='/config/asap.env')

asap_env_list=['DEV1', 'DEd1', 'DEj1', 'DEu1', 'DEp3', 'DEj4', 'DEu4', 'DEp4', 'NLj4', 'NLu4', 'NLo4', 'NLp4', 'PLj3', 'PLu3', 'PLo3', 'PLp3', 'HUj2', 'HUu2', 'HUo2', 'HUp2', 'CZj4', 'CZu4', 'CZo4', 'CZp4', 'SKj2', 'SKu2', 'SKo2', 'SKp2', 'ROj2', 'ROu2', 'ROp2', 'CHj3', 'CHu3', 'CHo3', 'CHp3', 'ATj1', 'ATu1', 'ATo1', 'ATp1', 'CZj3', 'CZu2', 'CZp2', 'CHj4', 'CHu4', 'CHo4', 'CHp4', 'ATu4', 'ATo4', 'ATp4','ROj1', 'ROu1', 'ROp1','IEj3','IEu3','IEo3','IEp3']

def update_mongo(selected_environment):
    con=MongoClient("mongodb://"+os.environ['asap_user']+":"+os.environ['asap_pwd']+"@mongodb:27017/libertyglobal-oss-asap?ssl=false")
    db=con['libertyglobal-oss-asap']
    coll=db['Environment']
    table_names=coll.find_one({'_id':selected_environment[:2].upper()})
    db_details=coll.find_one({'_id':'DB'})
    env_db_details=db_details[selected_environment]
    tables=[]
    table_data_dict={}
    print "in update_mongo_function"
    for table_name in table_names['SARM']:
        print table_name
        engine=create_engine('oracle://'+env_db_details['sarm_user']+':'+env_db_details['sarm_user']+'@'+env_db_details['dbname'])
        try:
            print table_name
            current_to_backup_diff=pd.read_sql('select * from '+table_name+' MINUS select * from '+table_name+'_BKP',engine)
            backup_to_current_diff=pd.read_sql('select * from '+table_name+'_BKP MINUS select * from '+table_name,engine)
            if not backup_to_current_diff.empty:
                table_data_dict[table_name]=current_to_backup_diff.to_dict('records')
                table_data_dict[table_name+'_BKP']=backup_to_current_diff.to_dict('records')
                tables.append(table_name)
        except Exception as e:
            print e
    for table_name in table_names['CTRL']:
        engine=create_engine('oracle://'+env_db_details['ctrl_user']+':'+env_db_details['ctrl_user']+'@'+env_db_details['dbname'])
        try:
            print table_name
            current_to_backup_diff=pd.read_sql('select * from '+table_name+' MINUS select * from '+table_name+'_BKP',engine)
            backup_to_current_diff=pd.read_sql('select * from '+table_name+'_BKP MINUS select * from '+table_name,engine)
            if not backup_to_current_diff.empty:
                table_data_dict[table_name]=current_to_backup_diff.to_dict('records')
                table_data_dict[table_name+'_BKP']=backup_to_current_diff.to_dict('records')
                tables.append(table_name)
        except Exception as e:
            print e
    table_data_dict['table_names']=tables
    print tables
    json_data=json.dumps(table_data_dict,default=json_util.default)
    fp=open('./p_data.json','w')
    fp.write(json_data)
    fp.close()
    try:
        db.create_collection('sql_diff')
        col=db['sql_diff']
    except:
        col=db['sql_diff']
        col.delete_many({'_id':selected_environment})
    col.insert_one({'_id':selected_environment})
    col.update_one({'_id':selected_environment},{'$set':table_data_dict})
    return

app.layout = html.Div([
    #Including local stylesheet
    html.Link(href='/static/cdc_layout_style.css', rel='stylesheet'),
    html.Div([
        html.Img(
        src='/img/Accenture-logo-red.png',
        style={
            'height' : '100%',
            'width' : '12%',
            'display':'inline-block',
            'float':'left',
            'padding-right':'20px'
        }
       ),
        html.Div([
             html.H1(children='ASAP SQL TABLE REVISION',style={'textAlign': 'center','color': '#000000'})
           ],style={'padding-left':'240px','display':'inline-block','float':'left'}),
    #html.Br(),
        html.Img(
        src='/img/logo-client-liberty-color.jpg',
        style={
            'height' : '80%',
            'width' : '11%',
            'display':'inline-block',
            'float':'right',
            'padding-right':'20px'
        }
       )],className='head-conatiner'),
    html.Div([
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Table(
        # Header
        children=[
            html.Thead(
                html.Tr([
                    html.Th(html.Div([
                                     html.B(html.Div('Environment : ', className='env_name',style={'color':'#597E16','fontSize': 20,'display':'inline-block','float':'left','padding-right':'10px'})),
         ]), style={'padding-top':'10px', 'padding-bottom':'10px','color':'#1A5276'}),
                    html.Th(html.Div([
                                     html.Div(dcc.Dropdown(id='environments-dropdown',
                                                           options=[{'label': k, 'value': k} for k in asap_env_list],
                                                           placeholder='Select the environment'),
                                               style={'display':'inline-block','float':'right','width':'200px'})
         ]), style={'padding-top':'10px', 'padding-bottom':'10px','padding-right': '100px','color':'#1A5276'})
                    ])
                ),
        ],style={
                'margin-left': 'auto',
                'margin-right': 'auto',
                'padding-left': '50px',
                'padding-right': '50px',
                'textAlign': 'left',
                }),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(id="new_layout"),
    html.Br(),
    html.Br()
    ],className='main-container')])

table_layout=html.Div([
                html.Div(id="display_content",style={'display':'inline-block','float':'left'},children=[html.Div("Please wait while the page is loading...",id="temp_id",style={'padding-left':'550px','color':'#CD7F32','textAlign':'center','fontSize':20})]),
                html.Div(id="selected_content_display",style={'display':'inline-block','float':'right','padding-right':'350px'}),
            ])

@app.callback(Output("new_layout", "children"), [Input("environments-dropdown", "value")])
def load_new_layout(env):
    if env is not None:
        return table_layout

@app.callback(Output("display_content", "children"),[Input("temp_id","children")], [State("environments-dropdown", "value")])
def display_modified_table_names(temp_id,selected_environment):
    update_mongo(selected_environment)
    con=MongoClient("mongodb://"+os.environ['asap_user']+":"+os.environ['asap_pwd']+"@mongodb:27017/libertyglobal-oss-asap?ssl=false")
    db=con['libertyglobal-oss-asap']
    diff_coll=db['sql_diff']
    get_table_names=diff_coll.find_one({'_id':selected_environment})
    tables=get_table_names['table_names']
    df=pd.DataFrame({'Tables Modified':tables})
    return dt.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict("rows"),
                        is_focused=True,
                        style_cell={'textAlign': 'center','backgroundColor':'#F0FFF0'},
                        row_selectable="single",
                        selected_rows=[],
                        content_style='fit',
                        style_header={
                        'backgroundColor': '#3CB371',
                        'fontWeight': 'bold',
                        'color': 'white',
                        'fontSize':20
                        })

@app.callback(
    Output('selected_content_display','children'),
    [Input('table', 'selected_rows'),Input('table','data')],
    [State("environments-dropdown", "value")])
def display_table_difference(selected_row_indices,rows,selected_environment):
    con=MongoClient("mongodb://"+os.environ['asap_user']+":"+os.environ['asap_pwd']+"@mongodb:27017/libertyglobal-oss-asap?ssl=false")
    db=con['libertyglobal-oss-asap']
    print rows[selected_row_indices[0]].values()[0]
    diff_coll=db['sql_diff']
    processed_data=diff_coll.find_one({'_id':selected_environment})
    backup_to_current_diff=pd.DataFrame.from_dict(processed_data[rows[selected_row_indices[0]].values()[0]+'_BKP'])
    current_to_backup_diff=pd.DataFrame.from_dict(processed_data[rows[selected_row_indices[0]].values()[0]])
    return html.Div([
            html.B(html.Div(rows[selected_row_indices[0]].values()[0]+'_BKP')),
            html.Br(),
            dt.DataTable(
                id='table_bkp',
                columns=[{"name": i, "id": i} for i in backup_to_current_diff.columns],
                data=backup_to_current_diff.to_dict("rows"),
                style_cell={'textAlign': 'center','backgroundColor':'#F0FFF0','minWidth': '80px', 'maxWidth': '1000px'},
                row_selectable="multi",
                is_focused=True,
                selected_rows=[],
                style_table={
                        'overflowX': 'scroll',
                        'maxHeight': '300px',
                        'overflowY': 'scroll'
                    },
                n_fixed_columns=1,
                style_data={'whiteSpace': 'normal'},
                css=[{
                     'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                style_header={
                    'backgroundColor': '#3CB371',
                    'fontWeight': 'bold',
                    'color': 'white'
                }),
            html.Br(),
            html.Div(id='insert_button',style={'padding-left':'400px'}),
            html.Br(),
            html.B(html.Div(rows[selected_row_indices[0]].values()[0])),
            html.Br(),
            dt.DataTable(
                id='table_current',
                columns=[{"name": i, "id": i} for i in current_to_backup_diff.columns],
                data=current_to_backup_diff.to_dict("rows"),
                style_cell={'textAlign': 'center','backgroundColor':'#F0FFF0','minWidth': '80px', 'maxWidth': '1000px',},
                style_table={
                        'overflowX': 'scroll',
                        'maxHeight': '300px',
                        'overflowY': 'scroll'
                    },
                n_fixed_columns=1,
                is_focused=True,
                style_data={'whiteSpace': 'normal'},
                row_selectable="multi",
                #selected_rows=[],
                css=[{
                     'selector': '.dash-cell div.dash-cell-value',
                     'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                style_header={
                    'backgroundColor': '#3CB371',
                    'fontWeight': 'bold',
                    'color': 'white'
                }),
            html.Br(),
            html.Br()],id='intermediate_result',style={'color':'#BA4A00'})

@app.callback(
    Output('insert_button','children'),
    [Input('table_bkp', 'data'),
     Input('table_bkp', 'selected_rows')])
def display_insert_button(rows,selected_row_indices):
    if len(selected_row_indices)>0:
        return html.Button(id='insert',
                           children = 'Insert',
                           style={'color':'#597E16','width':'85px',})

@app.callback(
    Output('intermediate_result','children'),
    [Input('insert','n_clicks')],
    [State('table_bkp','selected_rows'),State('table_bkp', 'data'),State('environments-dropdown', 'value'),State('table', 'selected_rows'),State('table','data')])
def display_on_click(n_clicks,selected_row_indices,rows,selected_environment,selected_table_name_index,table_names_list):
    if len(selected_row_indices)>0:
        con=MongoClient("mongodb://"+os.environ['asap_user']+":"+os.environ['asap_pwd']+"@mongodb:27017/libertyglobal-oss-asap?ssl=false")
        db=con['libertyglobal-oss-asap']
        coll=db['Environment']
        table_names=coll.find_one({'_id':selected_environment[:2].upper()})
        db_details=coll.find_one({'_id':'DB'})
        env_db_details=db_details[selected_environment]
        print str(selected_row_indices)
        if table_names_list[selected_table_name_index[0]].values()[0] in table_names['SARM']:
            engine=create_engine('oracle://'+env_db_details['sarm_user']+':'+env_db_details['sarm_user']+'@'+env_db_details['dbname'])
        else:
            engine=create_engine('oracle://'+env_db_details['ctrl_user']+':'+env_db_details['ctrl_user']+'@'+env_db_details['dbname'])
        data_dict=[]
        for row_index in selected_row_indices:
            data_dict.append(rows[row_index])
            df=pd.DataFrame.from_dict(data_dict)
        try:
            df.to_sql((table_names_list[selected_table_name_index[0]].values()[0]).lower(),engine,if_exists='append',index=False)
            diff_coll=db['sql_diff']
            mongo_data=diff_coll.find_one({'_id':selected_environment})
            final_table_data_list=[]
            table_data=mongo_data[table_names_list[selected_table_name_index[0]].values()[0]]
            for selected_dict in data_dict:
                selected_dict=str(selected_dict)
                for table_data_dict in table_data:
                    str_dict=str(table_data_dict)
                    if not selected_dict==str_dict:
                        final_table_data_list.append(table_data_dict)
            diff_coll.update_one({'_id':selected_environment},{'$set':{table_names_list[selected_table_name_index[0]].values()[0]:final_table_data_list}})
        except Exception as e:
            return str(e)
        return html.B('Inserted "{}" row(s) to table "{}"' .format(len(selected_row_indices),table_names_list[selected_table_name_index[0]].values()[0]), style={'fontSize':20,'color':'#32CD32'})

if __name__ == '__main__':
    server.run(debug=True)

