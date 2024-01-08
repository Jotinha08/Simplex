import tkinter as tk
from tkinter import ttk

class Application(tk.Tk):
    # INICIALIZACAO DAS VARIAVEIS DO PROGRAMA
    iteracoes = 0
    z = 0
    var = 0
    w = 0
    user_entry = []
    restri_entry = []
    sinais = []
    independentes = []

    linha_z = []
    matriz_simplex = []
    num_independentes = []
    var_bases = []
    var_artificiais = []
    linha_w = []
    vet_sinais = []
    ilimitada = False

    func_ops = None
    tipo = None
    quantidade_caixa = None

    def resolver(self): # FUNÇÃO QUE PEGA OS VALORES DIGITADOS PELO USUÁRIO QUANDO CLICAR NO BOTÃO RESOLVER
        open('resolucao_simplex.txt', 'w').close() #EXCLUIR O ARQUIVO DAS MATRIZES SIMPLEX
        
        # INICIALIZACAO DAS VARIAVEIS
        self.tipo = self.func_ops.get()
        self.linha_z = []
        self.matriz_simplex = []
        self.num_independentes = []
        self.var_bases = []
        self.var_artificiais = []
        self.linha_w = []
        self.vet_sinais = []
        self.iteracoes = 0
        self.w = 0
        self.ilimitada = False

        # CRIACAO DO BOTAO RESOLVER
        self.frame_respostas.destroy()
        self.frame_respostas = ttk.Frame(self)
        self.frame_respostas.grid(column=0, row=1)
        resolver = ttk.Button(self.frame_respostas, text='Resolver', command=self.resolver)
        resolver.grid(column=0, row=0, padx=5, pady=5)
        
        # INVERTE O SINAL DA FUNCAO CASO SEJA DE MAXIMIZACAO
        for index in range(self.var):
            self.linha_z.append(float(self.user_entry[index].get()) if self.tipo =='Minimização' else -float(self.user_entry[index].get()))
            self.vet_sinais.append(self.sinais[index].get())

        # LER OS VALORES DOS INDEPENDETES
        for i in range(self.var):
            valor_independente = float(self.independentes[i].get())
            a = []
            
            for j in range(self.var):
                a.append(float(self.restri_entry[i][j].get()) if valor_independente > 0 else -float(self.restri_entry[i][j].get()))

            self.matriz_simplex.append(a)

            # LEIO OS SINAIS ESCOLHIDOS PELO USUARIO
            if valor_independente < 0:
                if self.vet_sinais[i] == '<=':
                    self.vet_sinais[i] = '>='
                elif self.vet_sinais[i] == '>=':
                    self.vet_sinais[i] = '<='
                
            self.num_independentes.append(abs(valor_independente))

        self.num_independentes = self.num_independentes + [0]*2
        
        # FAÇO O APPEND NOS VETORES 
        for i, sinal in enumerate(self.vet_sinais):
            # OPERACAO DA FORMA PADRAO
            if sinal == '<=':
                self.matriz_simplex[i] = self.matriz_simplex[i]+[0]*(len(self.matriz_simplex[i-1])-self.var if i > 0 else 0)
                self.matriz_simplex[i].append(1)
                self.var_bases.append(len(self.matriz_simplex[i])-1)
            
            # CASO SEJA >=, DEIXAR NA FORMA PADRAO
            elif sinal == '>=':
                self.matriz_simplex[i] = self.matriz_simplex[i]+[0]*(len(self.matriz_simplex[i-1])-self.var if i > 0 else 0)
                self.matriz_simplex[i].append(-1)
                self.matriz_simplex[i].append(1)
                self.var_bases.append(len(self.matriz_simplex[i])-1)
                self.var_artificiais.append(self.var_bases[-1])

            # CASO SEJA =, DEIXAR NA FORMA PADRAO
            elif sinal == '=':
                self.matriz_simplex[i] = self.matriz_simplex[i]+[0]*(len(self.matriz_simplex[i-1])-self.var if i > 0 else 0)
                self.matriz_simplex[i].append(1)
                self.var_bases.append(len(self.matriz_simplex[i])-1)
                self.var_artificiais.append(self.var_bases[-1])

        # PADRONIZAR A MATRIZ
        tamanho_matriz = max(len(linha) for linha in self.matriz_simplex)
        self.matriz_simplex = [linha+[0]*(tamanho_matriz-len(linha)) for linha in self.matriz_simplex]
        self.linha_z = self.linha_z+[0]*(tamanho_matriz-len(self.linha_z))
        self.linha_w = self.linha_w+[0]*(len(self.linha_z))

        # GERAR A LINHA W DAS VARIAVEIS ARTIFICIAIS
        for i in range(len(self.var_bases)):
            if self.var_bases[i] in self.var_artificiais:
                for j in range(len(self.matriz_simplex[i])):
                    if j not in self.var_artificiais:
                        self.linha_w[j] = self.linha_w[j] - self.matriz_simplex[i][j]
                
                self.num_independentes[-1] = self.num_independentes[-1] - self.num_independentes[i]
                
        self.simplex() # CHAMADA DA FUNCAO QUE RESOLVE O SIMPLEX COM OS VALORES DIGITADOS

        # COMPARACAO DOS CASOS ESPECIAIS

        # PPL NAO POSSUI SOLUCAO
        if abs(self.w) > 0.0001:
            caso_tela = ttk.Label(self.frame_respostas, text=f'O problema não possui solução')
            caso_tela.grid(column=0, row=1, padx=5, pady=5)

        # PPL POSSUI SOLUCAO
        else:
            self.vetor_solucao = []
            for index in range(len(self.num_independentes)):
                if index not in self.var_bases:
                    self.vetor_solucao.append(0)
                else:
                    self.vetor_solucao.append(self.num_independentes[self.var_bases.index(index)])
            
            #SOLUCAO ILIMITADA
            if self.ilimitada == True:
                if self.z >= 0:
                    ilimi_tela = ttk.Label(self.frame_respostas, text=f'A solução do problema é ilimitada e tende a +∞')
                else:
                    ilimi_tela = ttk.Label(self.frame_respostas, text=f'A solução do problema é ilimitada e tende a -∞')
                
                ilimi_tela.grid(column=0, row=4, padx=5, pady=5)
            
            # SOLUCAO UNICA
            else:
                multi_solu = False
                for i in range(len(self.linha_z)):
                    if i in self.var_bases and abs(self.linha_z[i]) < 0.0001:
                        multi_solu =  True

                # MULTIPLAS SOLUCOES 
                if multi_solu:
                    multi_tela = ttk.Label(self.frame_respostas, text=f'Seu problema tem múltiplas soluções')
                    multi_tela.grid(column=0, row=5, padx=5, pady=5)
                
                z_tela = ttk.Label(self.frame_respostas, text=f'O Z da função é igual a {self.z}')
                z_tela.grid(column=0, row=1, padx=5, pady=5)

                num_it = ttk.Label(self.frame_respostas, text=f'O problema foi resolvido com {self.iteracoes} iterações')
                num_it.grid(column=0, row=2, padx=5, pady=5)

                vet_tela = ttk.Label(self.frame_respostas, text=f'Vetor solução: x* = {self.vetor_solucao}')
                vet_tela.grid(column=0, row=3, padx=5, pady=5)
        
    def simplex(self): # FUNCAO QUE RESOLVE O SIMPLEX
        # FASE 1
        self.arquivo() # PRINTA NO ARQUIVO TXT
        
        # VERIFICA SE TEM VARIAVEIS ARTIFICIAIS
        if self.var_artificiais:
            while True:
                self.iteracoes = self.iteracoes + 1
                menor_custo, index_menor = self.custo_negativo(self.linha_w) # VERIFICACAO DE QUAL VARIAVEL ENTRA NA BASE
                if menor_custo >= 0:
                    break

                menor_linha = float('inf')
                indice = -1
                
                for i in range(len(self.var_bases)): # VERIFICACAO DE QUAL VARIAVEL SAI DA BASE
                    if self.matriz_simplex[i][index_menor] > 0.0001 and self.num_independentes[i]/self.matriz_simplex[i][index_menor] < menor_linha:
                        menor_linha = self.num_independentes[i]/self.matriz_simplex[i][index_menor]
                        indice = i

                self.var_bases[indice] = index_menor
                divisor = self.matriz_simplex[indice][index_menor]

                for i in range(len(self.matriz_simplex[indice])): # DIVIDE TODA A LINHA PELO VALOR DA VARIAVEL QUE ENTRA
                    self.matriz_simplex[indice][i] = self.matriz_simplex[indice][i] / divisor

                self.num_independentes[indice] = self.num_independentes[indice] / divisor

                for i in range(len(self.matriz_simplex)): # PROCESSO DE PIVOTAMENTO
                    if i != indice:
                        pivot = -self.matriz_simplex[i][index_menor]
                        for j in range(len(self.matriz_simplex[i])):
                            self.matriz_simplex[i][j] = self.matriz_simplex[i][j] + pivot*self.matriz_simplex[indice][j]

                        self.num_independentes[i] = self.num_independentes[i] + pivot*self.num_independentes[indice]

                pivot_z = -self.linha_z[index_menor] # PIVOT DA LINHA Z
                pivot_w = -self.linha_w[index_menor] # PIVOT DA LINHA W

                for i in range(len(self.linha_w)): # OPERACOES DA LINHA W E LINHA Z
                    self.linha_z[i] = self.linha_z[i] + pivot_z*self.matriz_simplex[indice][i]
                    self.linha_w[i] = self.linha_w[i] + pivot_w*self.matriz_simplex[indice][i]
                
                self.num_independentes[-2] = self.num_independentes[-2] + pivot_z*self.num_independentes[indice]
                self.num_independentes[-1] = self.num_independentes[-1] + pivot_w*self.num_independentes[indice]

                self.arquivo() # PRINTA A ITERACAO NO ARQUIVO TXT
        
            self.w = self.num_independentes[-1]

            # VERIFICAR SE O W É MAIOR QUE 0 
            if abs(self.w) > 0.0001:
                return

        # FASE 2 / FASE SEM AS ARTIFICIAIS
        while True:
            self.iteracoes = self.iteracoes + 1
            menor_custo, index_menor = self.custo_negativo(self.linha_z) # VERIFICACAO DE QUAL VARIAVEL ENTRA NA BASE
            if menor_custo >= 0:
                break

            menor_linha = float('inf')
            indice = -1
            
            for i in range(len(self.var_bases)): # VERIFICACAO DE QUAL VARIAVEL SAI DA BASE
                if self.matriz_simplex[i][index_menor] > 0 and self.num_independentes[i]/self.matriz_simplex[i][index_menor] < menor_linha:
                    menor_linha = self.num_independentes[i]/self.matriz_simplex[i][index_menor]
                    indice = i

            # VERIFICA SE ELA É ILIMITADA
            if indice == -1:
                self.ilimitada =  True
                self.z = -self.num_independentes[-2] if self.tipo == 'Minimização' else self.num_independentes[-2]
                return
            

            self.var_bases[indice] = index_menor
            divisor = self.matriz_simplex[indice][index_menor]

            for i in range(len(self.matriz_simplex[indice])): # DIVIDE TODA A LINHA PELO VALOR DA VARIAVEL QUE ENTRA
                self.matriz_simplex[indice][i] = self.matriz_simplex[indice][i] / divisor

            self.num_independentes[indice] = self.num_independentes[indice] / divisor

            for i in range(len(self.matriz_simplex)): # PROCESSO DE PIVOTAMENTO
                if i != indice:
                    pivot = -self.matriz_simplex[i][index_menor]
                    for j in range(len(self.matriz_simplex[i])):
                        self.matriz_simplex[i][j] = self.matriz_simplex[i][j] + pivot*self.matriz_simplex[indice][j]

                    self.num_independentes[i] = self.num_independentes[i] + pivot*self.num_independentes[indice]

            pivot_z = -self.linha_z[index_menor] # OPERACAO COM A LINHA Z 

            for i in range(len(self.linha_w)):
                self.linha_z[i] = self.linha_z[i] + pivot_z*self.matriz_simplex[indice][i]
                
            self.num_independentes[-2] = self.num_independentes[-2] + pivot_z*self.num_independentes[indice]

            self.arquivo() # ESCREVE A ITERACAO NO TXT 

        self.z = -self.num_independentes[-2] if self.tipo == 'Minimização' else self.num_independentes[-2]
            
    def custo_negativo(self, linha): # FUNCAO QUE PEGA O MENOR CUSTO DA LINHA
        menor = float('inf')
        index = -1
        
        for i in range(len(linha)):
            if i in self.var_artificiais:
                continue

            if linha[i] < menor:
                menor = linha[i]
                index = i
        
        return menor, index
    
    def gerar_problema(self): # FUNCAO QUE GERA O LAYOUT PARA DIGITAR OS PROBLEMAS
        self.user_entry = []
        self.restri_entry = []
        self.sinais = []
        self.independentes = []
        self.linha_z = []
        self.matriz_simplex = []
        self.num_independentes = []
        self.var_bases = []
        self.var_artificiais = []
        self.linha_w = []
        self.vet_sinais = []

        self.frame_func.destroy()
        self.frame_func = ttk.Frame(self.frame_problema)
        self.frame_func.grid(column=0, row=2)

        self.frame_restricoes.destroy()
        self.frame_restricoes = ttk.Frame(self.frame_problema)
        self.frame_restricoes.grid(column=0, row=3)
        
        self.var = int(self.quantidade_caixa.get())

        resox = 300 + 75*self.var
        resoy = 300 + 75*self.var
        self.geometry(f"{resox}x{resoy}")
        
        func_ops_label = ttk.Label(self.frame_func, text='Escolha o tipo de problema')
        func_ops_label.grid(column=0, row=2, padx=5, pady=5, columnspan=2)
        self.func_ops = ttk.Combobox(self.frame_func, values=['Minimização', 'Maximização'], state='readonly')
        self.func_ops.grid(column=0, row=3, padx=5, pady=5)
        self.func_ops.current(0)
        
        z_label = ttk.Label(self.frame_func, text='Z = ')
        z_label.grid(column=1, row=3, padx=5, pady=5)

        problema = ttk.Label(self.frame_func, text='Digite os valores do seu problema')
        problema.grid(column=2, row=2, padx=5, pady=5, columnspan=6)

        for index in range(self.var):
            self.user_entry.append(ttk.Entry(self.frame_func, width=6))
            self.user_entry[index].grid(column=2+2*index, row=3, padx=5, pady=5)

            x_entry = ttk.Label(self.frame_func, text=f'X{index+1}')
            x_entry.grid(column=3+2*index, row=3, padx=5, pady=5)

        restricoes_label = ttk.Label(self.frame_restricoes, text='Agora digite as restrições do problema')
        restricoes_label.grid(column=0, row=0, columnspan=5)
        
        for i in range(self.var):
            x_entry = ttk.Label(self.frame_restricoes, text=f'X{i+1}')
            x_entry.grid(column=i, row=1, padx=5, pady=5)

        for i in range(self.var):
            restri_aux = [ttk.Entry(self.frame_restricoes, width=6) for _ in range(self.var)]
            self.restri_entry.append(restri_aux)
            
            for j in range(self.var):
                self.restri_entry[i][j].grid(column=j, row=i+2, padx=5, pady=5)
        
            self.sinais.append(ttk.Combobox(self.frame_restricoes, values=['<=', '>=', '='], state='readonly', width=6))
            self.sinais[i].grid(column=j+1, row=i+2, padx=5, pady=5)
            self.sinais[i].current(0)

            self.independentes.append(ttk.Entry(self.frame_restricoes, width=6))
            self.independentes[i].grid(column=j+2, row=i+2, padx=5, pady=5)

        resolver = ttk.Button(self.frame_respostas, text='Resolver', command=self.resolver)
        resolver.grid(column=0, row=0, padx=5, pady=5)

    def arquivo(self): # FUNCAO QUE CRIA E DIGITA AS MATRIZES DAS ITERACOES EM UM ARQUIVO TXT
        with open('resolucao_simplex.txt', 'a') as f:
        
            f.write(f'Iteração {self.iteracoes}\n\n')
        
            for i in range(len(self.matriz_simplex)):
                f.write(f'{self.matriz_simplex[i]} [{self.num_independentes[i]}]\n')

            f.write(f'\nLinha Z = {self.linha_z} [{self.num_independentes[-2]}]\n')
            f.write(f'Linha W = {self.linha_w} [{self.num_independentes[-1]}]\n\n')

            f.write('---------------------------------------------------\n\n')
    
    def __init__(self): # FUNCAO DA TELA DO TKINTER
        super().__init__()
        self.title('Simplex') 
        self.geometry("600x500") 

        #-----------------------------------------------------------

        self.frame_problema = ttk.Frame(self)
        self.frame_problema.grid(column=0, row=0)

        self.frame_func = ttk.Frame(self.frame_problema)
        self.frame_func.grid(column=0, row=2)

        self.frame_restricoes = ttk.Frame(self.frame_problema)
        self.frame_restricoes.grid(column=0, row=3)
        
        self.frame_respostas = ttk.Frame(self)
        self.frame_respostas.grid(column=0, row=1)

        self.frame_var = ttk.Frame(self.frame_problema)
        self.frame_var.grid(column=0, row=1)

        intro = ttk.Label(self.frame_problema, text="Digite o seu problema de otimização")
        intro.grid(column=0, row=0, padx=5, pady=5)

        quantidade_var = ttk.Label(self.frame_var, text="Quantidade de variáveis:")
        quantidade_var.grid(column=0, row=1, padx=5, pady=5)

        self.quantidade_caixa = ttk.Entry(self.frame_var, width=4)
        self.quantidade_caixa.grid(column=1, row=1, padx=5, pady=5)

        quantidade_botao = ttk.Button(self.frame_var, text='Inserir', command=self.gerar_problema)
        quantidade_botao.grid(column=2, row=1, padx=5, pady=5)

        self.mainloop()

Application()