# LRO Ligações 0.7.0

Desenvolvido por LRO Soluções de engenharia LTDA.

[LinkedIn de Lucas Oliveira](https://www.linkedin.com/in/lucas-oliveira-722723149/?isSelfProfile=true)

Aplicativo Streamlit para ligações de perfis I, com desenho proporcional, verificação geométrica, memória Word editável e projetos JSON. Forças em **kgf**, momentos em **kgf·m**, dimensões em **mm**. Diâmetros e espessuras têm opções em polegadas. As ações inseridas já são de cálculo.

## Atualizar e abrir

1. Pare o app no terminal com **Ctrl+C**.
2. Extraia este pacote em uma **pasta nova**, preservando seus projetos JSON e a versão anterior.
3. Abra o terminal na pasta que contém `app.py`, ative seu ambiente Python 3.12 e execute:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Para uma instalação nova no Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Para reabrir depois, basta o último comando. Não precisa reinstalar as bibliotecas em cada uso. Fechar apenas a aba do navegador não encerra o processo do aplicativo.

O pacote não altera automaticamente o app hospedado. Para Streamlit Cloud, atualize também as pastas `lro/` e `data/`, mantendo a estrutura; não envie `.venv`.

## Famílias disponíveis

| Seleção | Ações de entrada | Arranjo |
|---|---|---|
| Single plate | V e N de tração | Chapa soldada à mesa da coluna ou alma da viga de apoio; viga apoiada parafusada |
| Alma de coluna com duas talas | V e N com sinal | Talas independentes, nervura e quatro horizontais soldados à coluna |
| End plate rotulada | V e N com sinal | Chapa de altura total, sobra inicial de 5 mm, parafusos entre mesas |
| End plate engastada | M, V e N com sinal | Modelo 4E sem nervuras, extensão acima e abaixo ou somente acima |

N positivo é tração; N negativo é compressão. Na end plate engastada, M positivo traciona a mesa superior. A ligação com extensão somente acima aceita esse sentido de momento; para o sentido inverso, use extensão também abaixo.

## O que mudou nesta versão

- O resultado de atendimento passou a ser **ATENDE ÀS VERIFICAÇÕES REALIZADAS**. As premissas e exclusões ficam no final da tela e no final do Word. Falhas resistentes, geometrias inválidas e condições reais fora do domínio continuam sendo indicadas.
- As end plates verificam parafusos sob tração, cisalhamento e interação elíptica; contato nos furos; blocos da chapa; soldas e metal-base; alma da viga; mesa e alma da coluna. A engastada inclui o painel da coluna sob as premissas declaradas.
- A rotulada compara a espessura com os limites de flexibilidade do detalhamento e com a espessura necessária para não omitir efeito alavanca sob N.
- A engastada calcula a espessura mínima da chapa e da mesa da coluna pelo procedimento de chapa espessa do DG39. Adota-se o comportamento usual pela NBR 6.1.2.3, dentro do domínio do modelo. Não se calcula uma curva momento–rotação ou uma mola Si para a análise global.
- Os projetos antigos de single plate e duas talas continuam aceitos. As end plates usam um tipo JSON próprio. Ao carregar um exemplo ou projeto de end plate, o tipo exibido acompanha o arquivo.

## Domínio das end plates

A end plate engastada usa a geometria **4E** do Design Guide 39, com dois parafusos por linha e sem enrijecedores. Os intervalos ensaiados do guia, incluindo a margem de 10%, são conferidos. Exige-se momento dominante: `|N|(d−tf) ≤ |M|`. Aço da chapa com fy até 345 MPa. Não se extrapola o procedimento para axial dominante, chapa enrijecida, múltiplas colunas de parafusos ou outros padrões de furação.

A rotulada usa gabarito de 90–140 mm e chapa com fy até 275 MPa, inicialmente A36. O limite adotado é 10 mm para vigas até 457 mm de altura e 12 mm para vigas maiores. Os demais aços continuam no catálogo; escolher material fora desse domínio produz indicação para revisar a escolha.

A conferência normativa mínima de 45 kN atua sobre a resultante N/V, com direção e sentido preservados. **O momento externo não é multiplicado por esse fator.** Não se aplica automaticamente um suposto mínimo de momento de 50% da resistência da viga.

Nas end plates engastadas, as juntas **viga–chapa** são CJP nas duas mesas e na alma, com metal de adição compatível. Na rotulada são filetes contínuos. Em ambas, **chapa–coluna é parafusada**.

A coluna é contínua, sem extremidade ou emenda próxima; não há outra viga ou cargas locais concorrentes no nó. O painel usa a hipótese `Ncol,Sd ≤ 0,4 Ag,col fy,col` e não desconta cortante favorável da coluna. As verificações globais dos membros e a compatibilização com o modelo estrutural permanecem no projeto.

## Exemplos e documentação

`examples/` contém projetos JSON, desenhos SVG e sete memórias Word atualizadas. Os três exemplos de end plate usam W410×38,8 chegando à mesa de CS600×281. Os esforços são exemplos de uso, não um dimensionamento aprovado para uma obra.

- `docs/END_PLATES_METODOLOGIA.md`: equações, hipóteses, limites e fontes das novas famílias.
- `docs/registro_end_plates.json`: resultados numéricos reproduzíveis dos exemplos.
- `docs/DUAS_TALAS_METODOLOGIA.md`: modelo local da nervura e talas.
- `docs/REVISAO_TECNICA.md` e `docs/METODOLOGIA.md`: histórico técnico das single plates.

Nas duas talas, estabilidade acoplada e capacidade de rotação do conjunto continuam fora das verificações de componentes; a nota está nas premissas. Nas single plates, a interação fora do plano da alma da viga de apoio sob N+V ou N excêntrico continua excluída. A alteração de apresentação não atribui resistência a esses mecanismos.

## Testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```

Incluem regressão das famílias anteriores, comparação numérica com o exemplo 5.3-1 do DG39, substituição independente das equações da NBR, conversão de unidades, sinais, domínio, interação nos parafusos, importação e exportação. São testes de software e conferências analíticas identificadas, não validação experimental do conjunto.
