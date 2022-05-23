import requests
import pandas as pd
import json
import time


import dash
import dash_auth
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output, State

USERNAME_PASSWORD_PAIRS = [
    ['francisconetomaq', 'ENG.mec.52.25'],
    ['teste123', '123456789']
]

app = dash.Dash()
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server



options = [
    {'label':'Salinas/MG','value':'Salinas'},
    {'label':'Lavras/MG','value':'Lavras'},
    {'label':'Varginha/MG','value':'Varginha'}
]
options2 = [
    {'label':'Sim','value':'1'},
    {'label':'Não','value':'0'}
]
app.layout = html.Div([
    html.H2(
        children='Dashboard de monitoramento em tempo real - Covid-19.'
    ),
    html.H6(
        children= 'Disponível apenas para três cidades (Salinas/MG, Varginha/MG e Lavras/MG)'
    ),

    html.H6(
        children='Aparentemente, a API usada não está mais atualizando os dados.'
    ),
    html.H6(
        children= 'API usada: https://brasil.io/home/'
    ),
    html.Div([
        html.H5(
            children= 'Selecione a cidade que deseja buscar os dados:'
        ),
        dcc.Dropdown(
            id = 'entrada-cidade',
            value='Salinas',
            multi =False,
            options = options

        ),
        html.H5(
            children='Selecione se deseja dados acumulados:'
        ),
        dcc.Dropdown(
            id='entrada-acumulado',
            value= '1',
            multi=False,
            options=options2

        ),
        html.Br(),
        html.Button(
            id = 'submit-button',
            children='Buscar Dados',
            n_clicks= 0
        )
        
    ]),html.Div(
      html.H5(
          id = 'resultado-selecao'
      )
    ),
    html.Div([
        dcc.Graph(
            id = 'my_graph'
        ),
        dcc.Graph(
            id = 'my_graph2'
        ),
        dcc.Graph(
            id = 'my_graph3'
        ),
        dcc.Graph(
            id = 'my_graph4'
        )
    ])
], style={'textAlign': 'center'})


@app.callback([Output('my_graph', 'figure'),
               Output('my_graph2','figure'),
               Output('my_graph3','figure'),
               Output('my_graph4','figure'),
               Output('resultado-selecao','children')],
                [Input('submit-button', 'n_clicks')],
                [State('entrada-cidade', 'value'),
                 State('entrada-acumulado', 'value')])
def update_graph(n_clicks, cidade, acumulo):
    time.sleep(2)
    # o token foi retirado intencionalmente.
    myToken = ''
    myUrl = f'https://api.brasil.io/v1/dataset/covid19/caso/data/?city={cidade}'
    head = {'Authorization': 'token {}'.format(myToken)}
    response = requests.get(myUrl, headers=head)

    dados = response.json()
    dados_str = json.dumps(dados)
    dados_dict = json.loads(dados_str)

    dia = []
    casos_confirmados = []
    mortes = []
    taxa_morte = []
    confirmado_por_100k = []
    populacao_estimada = dados_dict["results"][0]["estimated_population"]

    for i in range(len(dados_dict["results"])):
        casos_confirmados.append(dados_dict["results"][i]['confirmed'])
        mortes.append(dados_dict["results"][i]['deaths'])
        dia.append(dados_dict["results"][i]['date'])
        confirmado_por_100k.append(dados_dict["results"][i]['confirmed_per_100k_inhabitants'])
        taxa_morte.append(dados_dict["results"][i]['death_rate'])

    dados_gerais = [dia,
                    casos_confirmados,
                    mortes,
                    confirmado_por_100k,
                    taxa_morte]
    df = pd.DataFrame(dados_gerais).transpose()
    print(df)
    colunas = [
        'Data',
        'Casos Confirmados - Acumulado',
        'Mortes - Acumulado',
        'Casos Confirmados por 100 mil habitantes - Acumulado',
        'Taxa de mortes'
    ]
    df.columns = [
        'Data',
        'Casos Confirmados - Acumulado',
        'Mortes - Acumulado',
        'Casos Confirmados por 100 mil habitantes - Acumulado',
        'Taxa de mortes'
    ]
    df['Data'] = pd.to_datetime(df['Data'],
                                format='%Y-%m-%d')

    for i in range(1, len(colunas)):
        if i in [1, 2]:
            df[f'{colunas[i]}'] = df[f'{colunas[i]}'].astype(int)
        else:
            df[f'{colunas[i]}'] = df[f'{colunas[i]}'].astype(float)
    df = df.sort_values(by='Data')
    df['Casos confirmados'] = df['Casos Confirmados - Acumulado'].diff(1)
    df['Mortes'] = df['Mortes - Acumulado'].diff(1)
    df = df.fillna(0)
    df = df.reset_index(drop=True)
    if acumulo == '0':
        figura_01 = px.line(
            df,
            x = 'Data',
            y = 'Casos confirmados',
            title= f'Casos confirmados no município de {cidade}'
        )
        figura_02 = px.line(
            df,
            x = 'Data',
            y = 'Mortes',
            title= f'Mortes confirmadas no município de {cidade}'
        )
    else:
        figura_01 = px.line(
            df,
            x = 'Data',
            y = 'Casos Confirmados - Acumulado',
            title= f'Casos confirmados no município de {cidade} - Acumulado'
        )
        figura_02 = px.line(
            df,
            x = 'Data',
            y = 'Mortes - Acumulado',
            title= f'Mortes confirmadas no município de {cidade} - Acumulado'
        )
    figura_03 = px.line(
        df,
        x='Data',
        y='Casos Confirmados por 100 mil habitantes - Acumulado',
        title=f'Casos confirmados por 100 mil habitantes em {cidade} - Acumulado'
    )
    figura_04 = px.line(
        df,
        x='Data',
        y='Taxa de mortes',
        title=f'Taxa de mortes em {cidade} - Acumulado - Razão mortes e casos confirmados.'
    )
    resultado = f'A cidade selecionada foi {cidade}. A população estimada é de {populacao_estimada} habitantes.'
    return figura_01, figura_02, figura_03, figura_04, resultado

if __name__ == '__main__':
    app.run_server(debug=False)