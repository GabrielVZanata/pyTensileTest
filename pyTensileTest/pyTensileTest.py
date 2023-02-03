#Importando as bibliotecas necessárias
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv

#Ignorando warnings para diminuir a poluição do terminal
import warnings
warnings.filterwarnings('ignore')

# Função para ler arquivo csv direto da Shimadzu
def read_testdata (file,encoding="ANSI"):
    
    # Otendo nomes individuais das amostras ensaiadas
    samples_csv = open(file,"r", encoding=encoding)
    for row in csv.reader(samples_csv, delimiter = ','):
        samples = []
        for i in row:
            if i != '':
                i = i.replace(' ','')
                samples.append(i)
        break

    # Obtendo apenas as colunas de força e deformação do dataset referentes a cada uma das amostras    
    dfpuro = pd.read_csv(file, header=1, skiprows=[2] ,encoding=encoding, sep=",", decimal=",", dtype=np.float64)

    qtt_sample = len(samples)
    columns = []

    for i in range(0,qtt_sample):   # Este código espera encontrar as colunas de força e deslocamento respectivamente na posição 1 e 3 de cada amostra
                                    # Portanto, esse laço deve ser alterado se a formatação do arquivo da shimadzu for diferente da esperada pelo código.
        if i == 0:
            force = dfpuro.columns[1]
            deformation = dfpuro.columns[3]
        else:
            force = dfpuro.columns[1]+ "." + str(i)
            deformation = dfpuro.columns[3]+ "." + str(i)

        columns.append(force)
        columns.append(deformation)

    df = dfpuro.loc[:,columns]
    
    # Inserindo a nomeclatura das amostras no nome das colunas, para que saiam no plot
    dfcolumns = []
    for i in samples:
        dfcolumns.append(i + "_F")
        dfcolumns.append(i + "_D")

    df.columns = dfcolumns
    
    return df

#Função para conversão de força para tensão
def to_tension(df,diam):

    df_t = df.copy()

    #Cálculo de áreas de cada barra
    areas = []
    for x in diam:
        area = (x**2)*np.pi/4
        areas.append(area)
    areas = np.array(areas)
    #print(areas)

    #Conversão dos valores de força do DataFrame para tensão 
    df_aux = df.iloc[:,::2] * 1000 / (areas)

    #Substituindo os valores de força do DataFrame para tensão
    df_t.iloc[:,::2] = df_aux.iloc[:,:]

    return df_t

# Função de identificação do trecho linear e coeficientes da equação da reta
def linearize_diag (df, min_rsq=0.9996, int_size=300):
    s = len(df.columns)
    lista_1 = []
    lista_2 = []

    rsq_min = min_rsq   # R2 mínimo a ser buscado - quanto mais próximo de 1.0 mais linear o trecho 
                        # mas o programa pode não encontrar trecho tão linear, gerando erros. Não exagere.

    # Loop para buscar e registrar o trecho mais linear (maior R²) para cada par Tensão x Deformação
    for i in range(0,s,2):
        y = i
        x = y + 1
        t = len(df.iloc[:,x])
        R2  = False

        med = df.count()
        med = med.tolist()
        w1 = med[x]

        while w1 > 0 and not R2:
            w1 = w1 - 50                # Passo de busca ao longo do data frame
            w2 = w1 + int_size          # Tamanho do trecho a ser estudado (ALTERAR caso não obtenha o resultado desejado no plot)
            deform = df.iloc[w1:w2,x]
            tens = df.iloc[w1:w2,y]

            corr_matrix = np.corrcoef(deform, tens)
            corr = corr_matrix[0,1]
            R_sq = corr**2

            if R_sq >= rsq_min:          

                #print(df.columns[y], "R² = ", R_sq, "w1:w2 = ", w1, ":", w2)
                y0 = df.iloc[w1,y]
                x0 = df.iloc[w1,x]
                y1 = df.iloc[w2,y]
                x1 = df.iloc[w2,x]

                x_un = [x0,x1]
                y_un = [y0,y1]
                coeff = np.polyfit(x_un, y_un, 1)

                if coeff[1] < 0:        # Garantir que o trecho pré escoamento seja ajustado
                    red = -coeff[1]/coeff[0]
                    lista_2.append(red)
                    lista_1.append(w1)
                    lista_1.append(w2)
                    R2 = True


                
                
            
        #if not R2:
            #print(df.columns[y], "R² = Não Encontrado")
 
    return [lista_1,lista_2]

# Função para correção completa do diagrama, utiliza a função linearize e pode utilizar a função cut_end
def correct_diag(df, cut=False, min_rsq = 0.9996, int_size=300, correct_force=False, diam=[]):

    if correct_force:
        df_aux = to_tension(df, diam)
    else:
        df_aux = df.copy()

    df_corr = df_aux.copy()

    lista_lin = linearize_diag(df, min_rsq, int_size)[0]
    lista_coefs = linearize_diag(df, min_rsq, int_size)[1]

    s = len(df.columns)
    lista_corrigida = []

    # Corrige a curva, subtrai coeficientes
    df_aux = df.iloc[:,1::2] - lista_coefs

    df_corr.iloc[:,1::2] = df_aux.iloc[:,:]

    for i in range(0,s,2):
        y = i
        x = y + 1

        fim_F = df_corr.iloc[(lista_lin[i+1]-1):,y]
        fim_D = df_corr.iloc[(lista_lin[i+1]-1):,x]

        fim_F = fim_F.tolist()
        fim_D = fim_D.tolist()

        fim_D[0] = 0
        fim_F[0] = 0

        lista_corrigida.append(fim_F)
        lista_corrigida.append(fim_D) 
    
    cols = df.columns
    df_corr = pd.DataFrame(lista_corrigida).transpose()
    df_corr.columns = cols

    # Cortando o resíduo final do diagrama, necessário chamar nos argumentos
    if cut:
        df_corr = cut_end(df_corr)

    return df_corr

# Função para remoção do resíduo gráfico após o rompimento
def cut_end(df):
    df_cut = df.copy()
    s = len(df.columns)
    c = 0.85        # Parâmetro de corte em % de queda, alterar conforme desejado

    for i in range(0,s,2):
        y = i
        x = y + 1

        t = df_cut.iloc[:,i].count()
        r_indx = df_cut.loc[df_cut.iloc[:,i] == df_cut.iloc[:,i].max()].index[0]
        w1 = r_indx
        cut = False

        while w1 < t and not cut:
            w1 = w1 + 1
            w2 = w1 + 1

            d1 = df_cut.iloc[w1,y]
            d2 = df_cut.iloc[w2,y]
            
            if d2 < c*d1:        
                df_cut.iloc[w1:,y] = np.nan
                df_cut.iloc[w1:,x] = np.nan
                cut = True
    
    return df_cut

# Função para retornar a força máxima e a deformação na força máxima de uma determinada amostra
def get_info(df, numbar=0, parse=False):
    barras = list(df.columns)
    lista = []

    ny = numbar*2
    nx = ny + 1
    
    max_i = df.loc[df.iloc[:,ny] == df.iloc[:,ny].max()].index[0]
    max_x = round(df.iloc[max_i,nx],2)
    max_y = round(df.iloc[max_i,ny],2)
    lista.append(max_x)
    lista.append(max_y)

    if parse:
        lista = pd.DataFrame(lista).transpose()
        lista.columns = ["Def_FMax","Fmax"]
            
    return lista    

# Função para plotar barras individualmente recebe (dataframe, 
# índice da barra desejada (0 a 11), observação a ser adicionada ao título)
def plot_sample(df, numbar=0, obs="", save=False, folder="", info=False):
    plt.style.use('_mpl-gallery')
    barras = list(df.columns)
    ny = numbar*2
    nx = ny + 1

    plot_title = "Diagrama Tensão x Deformação - Amostra " + barras[ny][0:-2]
    fig_title = str(folder) + barras[ny][0:-2]
    if obs != "":
        plot_title = plot_title + " " + obs
        fig_title = fig_title + obs[1]
    
    max_i = df.loc[df.iloc[:,ny] == df.iloc[:,ny].max()].index[0]
    max_x = round(df.iloc[max_i,nx],2)
    max_y = round(df.iloc[max_i,ny],2)
    
    #Plotando
    g = df.plot(x=barras[nx], y=barras[ny], xlabel="Deformação (mm)", \
                ylabel="Tensão (MPa)", title=plot_title, figsize=(6,3), legend=None).get_figure()

    if info:
        max_x_text = str(max_x) + " mm"
        max_y_text = str(max_y) + " MPa"
        plt.axline([max_x,max_y], [max_x,0], color = "Red", linestyle = '--', linewidth = 1, alpha=0.6)
        plt.axline([max_x,max_y], [0,max_y], color = "Red", linestyle = '--', linewidth = 1, alpha=0.6)
        plt.annotate(max_x_text,[max_x+0.1,max_y*0.5], color = "Red")
        plt.annotate(max_y_text,[max_x*0.5,max_y+5], color = "Red")
        
    if save:
        #Salvando gráfico já nomeado
        g.savefig(fig_title, bbox_inches="tight")

#Função para mapeamento do espectro RGB
def get_cmap(n, name='hsv'):
    return plt.cm.get_cmap(name, n)

# Função para plotar grupos de amostras na mesma figura, recebe(dataframe, lista com os índices das amostras a serem plotadas,
# observação com o nome do grupo de amostras, corr True para corrigidas e False para não corrigidas )
def plot_group (df, lista, obs="", group_name="", save=False, folder=""):

    plt.style.use('_mpl-gallery')
    fig = plt.figure(figsize=(7,5))
    ax = fig.add_subplot(111)
    barras = list(df.columns)  

    
    plot_title = "Diagrama Tensão x Deformação - " + group_name
    fig_title = str(folder) + str(group_name)
    if obs != "":
        plot_title = plot_title + " " + obs
        fig_title = fig_title + obs[1]    
    
    plt.title(plot_title)
    plt.xlabel("Deformação (mm)")
    plt.ylabel("Tensão (MPa)")

    loop = lista
    color = get_cmap(12)
    legend = []
    cor = []
    while len(cor) < len(barras)//2:
        for i in range(len(barras)//2):
            if i % 2 == 0:
                cor.append(i)
            else:
                cor.append(len(barras)//2-i)
            
    
    for x in loop:
        ny = x*2
        nx = ny + 1
        xa = barras[nx]
        ya = barras[ny]
        leg = ya[0:-2]
        legend.append(leg)
        ax.plot(df[xa], df[ya], c=color(cor[x]))
        
    ax.legend(legend)
    
    if save:
        #Salvando gráfico já nomeado
        fig.savefig(fig_title, bbox_inches="tight")
    plt.show()


