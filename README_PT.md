# Pacote de funções para manipulação de dados de Ensaios de Tração

## Conteúdo

- [Descrição](#Descrição)
- [read_testdata](#read_testdata)
- [to_tension](#to_tension)
- [linearize_diag](#linearize_diag)
- [cut_end](#cut_end)
- [correct_diag](#correct_diag)
- [get_info](#get_info)
- [plot_sample](#plot_sample)
- [plot_group](#plot_group)
- [Autor](#Autor)
- [Copyright and license](#copyright-and-license)


## Descrição

Esse código foi desenvolvido por Gabriel Valverde Zanata da Silva, ex aluno da Escola Politécnica da Universidade de São Paulo, para facilitar a manipulação e análise de dados de ensaios da máquina universal de ensaios Shimadzu. 

O objetivo principal deste código é ler, manipular, corrigir e plotar corretamente diagramas Tensão x Deformação, não havendo garantia de que funcionará para outros tipos de ensaio ou outras maquinas universais de ensaios.

Além disso, este é um projeto open source desenvolvido de maneira individual com o intuito de auxiliar alunos e pesquisadores em suas atividades acadêmicas/de pesquisa, portanto, se algo não funcionar correamente, não devem ser esperadas atualizações/correções de bugs, apesar de o feedback ser muito bem-vindo através dos conais de comunicação do autor.


Para que o código possa funcionar adequadamente é necessário prestar atenção na formatação dos dados originais. As funções do pacote esperam um formato específico que deve ser idêntico ao do dataset "Tracao_acos.csv" disponível neste repositório.
Espera-se que esta seja a formatação padrão de dados oriundos da Shimadzu. Caso a formatação seja diferente, será necessário alterar as funções do pacote.


O uso, alteração, e reprodução do material desta biblioteca são livres, contanto que a fonte e o autor sejam mencionados.


## read_testdata

A função read_testdata tem como intuito realizar a leitura da base de dados gerada pela máquina universal de ensaios de forma simplificada, eliminando toda a etapa de tratamento que seira necessária para realizar a carga e leitura de maneira manual.

Os argumentos esperados são:
- file - aquivo da base de dados
- enconding - codificação do arquivo (por padrão: ANSI)

```code
read_testdata (file, encoding="ANSI")
```
É importante que a formatação e organização da base de dados seja exatamente como demonstrada na imagem de exemplo abaixo, ou seja, é estritamente necessário que as colunas e linhas possuam as mesmas nomenclaturas e ordem de aparição do exemplo abaixo. Do contrário será necessário realizar a carga e leitura da base de dados (e todo o tratamento necessário) de maneira manual via código.

<a>
    <img src="https://github.com/GabrielVZanata/pyTensileTest/blob/main/formatodataset.png" alt="Formato necessário para o dataset" width=400 height=200>
  </a>


## to_tension

A função to_tension permite obter a tensão real aplicada sobre a amostra, calculando com base na força aplicada pela máquina e na bitola (diâmetro) efetiva da amostra.

Os argumentos esperados são:
- df - o Dataframe contendo os dados de força e deslocamento (no formato do df retornado através da função read_testdata)
- diam - lista contendo os diâmetros de cada amostra, na ordem em que aparecem no Dataframe.

```code
to_tension(df,diam)
```

## linearize_diag

A função linearize_diag identifica o trecho mais linear para correção do trecho inicial (elástico linear) dos diagramas, que, geralmente, é gerado de forma imprecisa durante os ensaios. Esta função deve ser utilizada em conjunto com a função correct_diag.

Os argumento esperados são:
- df - o Dataframe contendo os dados de tensão e deslocamento (no formato do df retornado através da função read_testdata)
- min_rsq - o valor mínimo de R² que o algoritmo deve buscar. Note que, o valor de R² varia de 0 a 1, sendo mais linear a medida que se aproxima de 1. Porém, se definido um valor muito alto a função pode não encontrar um trecho tão linear, o que causará erros.
- int_size - o tamanho dos intervalos a serem analizados em quantidade de instantes. Por padrão a função analisará os dados em trechos contendo 300 instantes. Quanto maior esse intervalo mais intensa será a linearização. 
Se o algoritmo não encontrar um trecho com o R² e tamanho de intervalo definidos, estes argumentos devem ser alterados (reduzidos) para evitar erros. 

```code
linearize_diag (df, min_rsq=0.9996, int_size=300)
```

## cut_end

A função cut_end realiza a remoção dos trechos medidos e plotados pela máquina de ensaios após a ruptura da amostra.

Os argumentos esperados são:
- df - o Dataframe contendo os dados de tensão e deslocamento (no formato do df retornado através da função read_testdata)

```code
cut_end(df)
```

  
## correct_diag

A função correct_diag aplica as funções to_tension, linearize_diag, cut_end para corrigir completamente os diagramas alterando as medidas de força para tensão, linearizando os trechos iniciais, corrigindo a deformação e removendo os dados após a ruptura.

Os argumentos esperados são:
- df - o Dataframe contendo os dados de tensão e deslocamento (no formato do df retornado através da função read_testdata)
- min_rsq - o valor mínimo de R² que o algoritmo deve buscar. Note que, o valor de R² varia de 0 a 1, sendo mais linear a medida que se aproxima de 1. Porém, se definido um valor muito alto a função pode não encontrar um trecho tão linear, o que causará erros.
- int_size - o tamanho dos intervalos a serem analizados em quantidade de instantes. Por padrão a função analisará os dados em trechos contendo 300 instantes. Quanto maior esse intervalo mais intensa será a linearização. 
Se o algoritmo não encontrar um trecho com o R² e tamanho de intervalo definidos, estes argumentos devem ser alterados (reduzidos) para evitar erros. 
- correct_force - Se TRUE aplicará a funsão to_tension ao dataframe e esperará receber o parâmetro diam.
- diam - lista contendo os diâmetros de cada amostra, na ordem em que aparecem no Dataframe.

```code
correct_diag(df, cut=False, min_rsq = 0.9996, int_size=300, correct_force=False, diam=[])
```
  <a>
    <img src="https://github.com/GabrielVZanata/pyTensileTest/blob/main/5_1N.png" alt="Diagrama não corrigido" width=400 height=300>
  </a>
  <a>
    <img src="https://github.com/GabrielVZanata/pyTensileTest/blob/main/5_1.png" alt="Diagrama corrigido" width=400 height=300>
  </a>
  
## get_info

A função get_info permite obter a tensão máxima e a deformação na tensão máxima.
Os argumentos esperados são:
- df - o Dataframe contendo os dados de tensão e deslocamento (no formato do df retornado através da função read_testdata)
- numbar - número de aparição da amostra desejada (iniciada em 0),por exemplo: para analisar a 8ª amostra do dataframe, deve-se utilizar numbar=7. 
- parse - True para retornar o resultado em formato de Dataframe, False para retornar em formato de lista.

```code
get_info(df, numbar=0, parse=False)
```

## plot_sample

A função plot_sample plota o diagrama tensão x deformação para uma amostra de maneira individual.

Os argumento esperados são:
- df - o Dataframe contendo os dados de tensão e deslocamento (no formato do df retornado através da função read_testdata)
- numbar - número de aparição da amostra desejada (iniciada em 0),por exemplo: para plotar a 8ª amostra do dataframe, deve-se utilizar numbar=7. 
- obs - Uma string com observação a ser acrescentada ao título do plot.
- save - True para salvar o plot em disco.
- folder - Diretório onde o plot deve ser salvo.
- info - True para acrescentar a tensão máxima e deslocamento na tensão máxima ao plot.

```code
plot_sample(df, numbar=0, obs="", save=False, folder="", info=False)
```
  <a>
    <img src="https://github.com/GabrielVZanata/pyTensileTest/blob/main/5_1.png" alt="Plot individual" width=400 height=300>
  </a>

  
## plot_group

A função plot_gorup plota o diagrama tensão x deformação para um grupo de amostras selecionadas.

Os argumento esperados são:
- df - o Dataframe contendo os dados de tensão e deslocamento (no formato do df retornado através da função read_testdata)
- lista - lista com os números de aparição das amostras desejadas (iniciada em 0),por exemplo: para plotar as 2ª, 3ª ,8ª e 10ª amostras do dataframe, deve-se utilizar lista=[1,2,7,9]. 
- obs - Uma string com observação a ser acrescentada ao título do plot.
- save - True para salvar o plot em disco.
- folder - Diretório onde o plot deve ser salvo.
- group_name - String para definir o nome do grupo de amostras a ser apresentado no título do plot.

```code
plot_group (df, lista, obs="", group_name="", save=False, folder="")
```
  <a>
    <img src="https://github.com/GabrielVZanata/pyTensileTest/blob/main/Amostras de 16mm.png" alt="Plot grupo" width=400 height=300>
  </a>

## Autor

**Gabriel Valverde Zanata da Silva**

- <https://github.com/GabrielVZanata>
- <https://www.linkedin.com/in/gabriel-valverde-62141a227/>


## Copyright and license

Code and documentation copyright 2023 Gabriel Valverde Zanata da Silva. Code released under the [MIT License](https://reponame/blob/master/LICENSE).
