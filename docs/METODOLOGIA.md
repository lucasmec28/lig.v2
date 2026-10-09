# Metodologia de cálculo da versão 0.3

## Base e unidades

NBR 8800:2024, versão corrigida 2025, prevalece sobre valores divergentes de exemplos antigos. AISC Manual 16 e Companion P901-23W e SCI P358 são complementos identificados. O catálogo de fontes está em fontes.json. Não são redistribuídos manuais de terceiros.

Internamente: N, mm e MPa; interface e resultados: kgf, kgf·m e mm. 1 kgf = 9,80665 N. Os esforços de entrada já são de cálculo. Não há majoração adicional de ações. A conferência independente do mínimo de 45 kN da NBR 6.1.5.2 mantém a direção da resultante e aparece separadamente; zero não define direção.

Uma viga, encontro a 90°, uma ou duas colunas de furos padrão alinhados, corte simples, tração axial e soldagem de oficina. Sem atrito, fadiga, ação cíclica, incêndio, compressão ou múltiplos casos.

## Geometria

- a: face de solda ao primeiro eixo de parafusos; g: face do apoio à ponta da viga; borda na viga = a − g.
- s: passo entre colunas; e = a + (ncol−1)s/2: face ao centro do grupo.
- z: topo da mesa da viga apoiada ao topo da aba parafusada, antes do recorte.
- hp = 2ev + (n−1)p; largura = a + (ncol−1)s + eh.
- N atua no eixo da viga; eN = d/2 − (z+hp/2). Inclui-se |N·eN|.
- Furos: tabela 14 da NBR; desconto líquido acrescido de 2 mm, exceto furação com broca informada.
- Distâncias às bordas e espaçamentos: 6.3.9 a 6.3.12, condição pintada/não corrosiva cadastrada. A exceção da tabela 16 usa a resistência conservadora à pressão de contato calculada.
- Folga g = 10 mm é uma sugestão de fabricação, não uma dispensa normativa. Interferências com mesas, raios, recortes, filetes e montagem continuam sendo verificadas.

## Esforços e parafusos

M = |V|e + |N·eN|. É uma envoltória de momento local; não representa uma ligação de engaste. Coordenadas do grupo em relação ao centro: J = Σ(xi²+yi²). Fxi = N/nb − M·yi/J; Fyi = V/nb + M·xi/J. O equilíbrio de forças e momento é testado.

FRd = kpega α Ab fub/γa2, com α = 0,45 ou 0,56 conforme 6.3.3.2; γa2 = 1,35. kpega = 1 − 0,01·max(0; pega−5db)/1,5, conforme 6.3.7. Não se toma a dispensa por protensão. Valores não positivos bloqueiam o cálculo.

Pressão de contato: min(1,2lc·t·fu; 2,4db·t·fu)/γa2. Adota-se o menor ligamento livre a furos ou bordas para qualquer direção de força, conservador. Não se usa automaticamente o aumento de resistência que admite grande deformação dos furos.

## Chapa e alma

Escoamento e ruptura por corte e tração: NBR 6.5, γa1 = 1,10 e γa2 = 1,35. A seção líquida vertical deduz n furos, inclusive com duas colunas: uma seção não cruza simultaneamente os dois alinhamentos horizontais.

Flexão e estabilidade da chapa: AISC F11 conforme P901 II.A-17B/19B, Cb = 1,84 e Lb = e; adota Cb = 1,0 quando existe momento adicional por N excêntrico. Mn é limitado ao momento plástico. Para duas colunas, e maior que a é mantido como opção conservadora. Ruptura por flexão: fuZn/γa2; Zn integra exatamente a seção com furos.

Interação N/V/M: AISC Manual 12-2/12-3, com resistências brasileiras explícitas. A excentricidade transversal de sobreposição é contabilizada quando a contenção não é confirmada, mas isso não aprova a estabilidade global sem contenção.

Bloco L sob V/N e U sob N: NBR 6.5.6 e interação AISC 12-1. Para o caminho completo com duas colunas, a distância até a borda inclui s, e o ramo horizontal líquido deduz 1,5 dh, contra 0,5 dh na coluna única. São avaliados também caminhos parciais por coluna. O quadro identifica caminhos completos e parciais. Furos alinhados e bordas superior/inferior da chapa simétricas; não há furos oblongos ou arranjos escalonados.

Alma apoiada: resistência local V/N, bloco U, mecanismo local de flexão/corte SCI e, quando há recorte, bloco L até cada borda livre recortada. Para duas colunas, a interação SCI da alma usa o braço até a última coluna. Soma linear de N nessa interação é uma adaptação conservadora declarada.

Alma sem recorte: instabilidade ao corte conforme NBR 5.4.3.1, kv = 5,34, sem crédito por enrijecedores transversais. λp = 1,10√(kvE/fy), λr = 1,37√(kvE/fy). Cv = 1, λp/λ ou 1,24(λp/λ)² nos respectivos intervalos. Para resistência local usa-se área h·tw, menor que d·tw.

## Ductilidade e soldas

Dispensa geométrica conforme AISC Parte 10: uma coluna requer que chapa ou alma satisfaça o limite de espessura convencional; duas colunas requerem ambas. Exige bordas horizontais de chapa e alma ≥ 2db. Fora da dispensa, calcula-se C′ = Σri[1−exp(−3,4ri/rmax)]^0,55, CIR centrado sob momento puro.

Mmax = Rn,par C′ e tmax = 6Mmax/(fy hp²). Usa-se resistência nominal brasileira com redução de pega. Não se aplica o aumento americano 1/0,90 do P901, nem o antigo 1,25: adaptação conservadora da hierarquia. A307 permanece sem validação de ductilidade para este sistema.

Dois filetes verticais: qmax = √[(N/(2h)+3M/h²)²+(V/(2h))²]. qRd = 0,6fw·w/(√2γw2), γw2 = 1,35. Sem aumento direcional de resistência. A mesma envoltória completa é usada como limite conservador na solda e no grupo.

Desenvolvimento da chapa: w ≥ max(5tp/8; √3·tp·fy/(2fw)), conforme a dedução nominal de Muir e Hewitt (2009), p.71, preservando o mínimo de detalhamento do procedimento AISC. A checagem sob esforços de cálculo continua pela NBR. Essa formulação permite calcular, por exemplo, USI-CIVIL 350 em vez de mantê-lo automaticamente como pendência.

Metal-base da chapa junto à solda: resultante por unidade de comprimento contra resistência conservadora ao corte. No pilar soldado, o filete mesa–alma deve ser informado; dois filetes contínuos, mesmo eletrodo da ligação, recebem conservadoramente N, V e M em comprimento hp. Verifica-se também o metal-base da alma. A solda global do pilar não é dimensionada.

## Recortes

Seção remanescente calculada pela integração de retângulos, sem crédito pelos raios. Desconta-se a projeção dos furos na seção crítica mesmo quando ela aumenta o conservadorismo. Para uma mesa recortada, usa-se o modelo do Manual Parte 9/P901 II.A-6: f=2c/d para c≤d ou min(3;1+c/d); k=2,2(h/c)^1,65 para c≤h ou 2,2h/c; k1=max(1,61;fk); λ=h/tw; λp=0,475√(k1E/fy).

Mn=Mp se λ≤λp; Mn=Mp−(Mp−My)(λ/λp−1) se λp<λ≤2λp; Mn=0,903Ek1S/λ² se λ>2λp. Para recorte duplo com mesmo comprimento nas mesas, usa-se F11/P901 II.A-7, Cb=1,84 para V puro, ou 1,0 quando existe momento adicional de N excêntrico, Lb=c e redução líquida min(Sn/Sg; Zn/Zg).

Mc = |V|max(g+c; xúltimo) + |N|max(|d/2−yc,g|; |d/2−yc,n|). MRd=Mn/γa1. Na interação adota-se N/NRd + Mc/MRd + V/VRd ≤ 1, opção linear conservadora. Para a resistência de corte recortada adota-se kv=1,2 (modelo de seção T, NBR 5.4.3.3), também limitando conservadoramente o recorte duplo, sem contribuição da mesa na área de corte. A ruptura líquida também limita VRd. A ruptura por flexão e o bloco L são verificações adicionais.

A aplicação exige contenção lateral na raiz do recorte, c≤2d, profundidades≤d/2, h/tw≤260 e, para recorte simples, hp≥h/2. Casos fora desse domínio permanecem incompletos. O modelo de recorte não é uma análise global de viga sem travamento.

## Apoio e limites

Corte e ruptura locais do apoio são calculados. Hierarquia contra punção SCI P358 p.128: limite conservador tp≤ts fu,s/(fy,pγa2). Para V puro também se calcula tp≤ts²fu,s hp²/(6Veγa2), **sem raiz quadrada**, e aceita-se a alternativa aplicável menos restritiva. Não se estende a segunda expressão a N e V simultâneos. Ela não substitui a flexão fora do plano da alma do apoio.

Pilar: flexão local da mesa por N quando aplicável e escoamento local da alma conforme NBR 5.7. Usam-se os casos próximos à extremidade e k=tf como opções conservadoras. A chapa deve estar alinhada à alma.

**Continuam sem modelo completo:** tração N na alma da viga de apoio; chapa estendida e soldada às mesas; enrijecedor oposto; estabilidade global sem contenção; compressão axial. Para chapa entre mesas o motor retorna lista resistente vazia. Não é permitido aprovar essas variantes por remover os avisos.

Os fatores de hierarquia/ductilidade são condições do método, separados dos índices de resistência sob carga. O estado geral considera ambos e também as pendências; um índice resistente baixo não apaga uma condição não atendida.
