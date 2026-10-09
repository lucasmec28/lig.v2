# Ligação à alma de coluna com duas talas

Versão 0.6.0. Modelo local por componentes; não é validação integral da configuração.

## Geometria e caminho das forças

A alma da viga, duas talas iguais e a nervura vertical são centradas. Os dois grupos têm uma coluna, mesmo número de linhas, passo e borda horizontal. Cada grupo recebe N e V integrais; as duas talas dividem as ações igualmente. A viga tem folga g em relação à ponta da nervura. Nem as talas nem a viga são soldadas à coluna.

A nervura tem altura H dentro da coluna e h na aba livre, igual à altura das talas. Quatro horizontais iguais ocupam dois níveis, uma chapa de cada lado da alma da coluna em cada nível. As duas do lado oposto são representadas, mas não têm resistência somada à dupla carregada.

Coordenada x a partir da face da alma da coluna, positiva para a viga:

| Posição | Coordenada |
|---|---|
| Ponta da mesa da coluna | b = (bf,col − tw,col)/2 |
| Ponta da nervura | b + u |
| Ponta da viga | b + u + g |
| Grupo na nervura | b + u − e |
| Grupo na viga | b + u + g + e |
| Rótula nominal adotada | b + u + g/2 |

Esta posição da rótula é uma hipótese de equilíbrio. Não comprova a capacidade de rotação. As talas medem `(4e+g) × h`, com `h=2ev+(n−1)p`. A condição `u≥2e+folga` mantém as talas inteiramente fora do envelope da coluna.

Em cada grupo, `Mg=V(e+g/2)`. O grupo elástico recebe `Fx,i=N/n−Mg yi/Σyi²` e `Fy,i=V/n`. O parafuso crítico é definido pela resultante vetorial, nunca pelo maior valor isolado entre N e V. O momento em cada extremidade da emenda tem sinal oposto, mas a máxima solicitação dos grupos simétricos é a mesma.

Na coluna, adota-se V transmitido pela solda vertical nervura–alma. Os horizontais frontais recebem `Hsup=N/2+Mcol/H` e `Hinf=N/2−Mcol/H`, com `Mcol=V(b+u+g/2)`. A soma é N, e o binário é Mcol. H livre é usado como braço conservador, inferior à distância entre os eixos dos horizontais. Para ações no eixo global da coluna, adicionar à excentricidade a distância da face ao eixo da alma e observar os sinais do modelo estrutural.

## Resistências e critérios

| Componente | Procedimento implementado |
|---|---|
| Parafusos | Corte duplo, α=0,45 com rosca ou 0,56 sem rosca, fub=830/1040 MPa, γa2=1,35; reduções por pega e enchimento |
| Contato | Menor ligamento livre entre bordas e entre furos; limites 1,2lc·t·fu e 2,4db·t·fu; talas somadas apenas por serem simétricas |
| Blocos | Caminho U axial e L vertical, Cts=0,5; interação linear de Σabs(Fx) e Σabs(Fy), abrangendo reversão local por momento |
| Seções brutas | Faixas retangulares; limite elástico com σeq=√[(abs(N)/Ag+abs(M)/Wg)²+3(1,5abs(V)/Ag)²] |
| Seções líquidas | An e Wn com furos deduzidos; Ae=min(An;0,85Ag) nas talas; somente a tensão de tração remanescente entra na ruptura axial |
| Compressão | Barra chata isolada, Q=1; curva χ de NBR 8800 item 5.3, inclusive para barras curtas; K e L declarados, sem ganho de solidarização entre talas |
| Flexão com instabilidade | Complemento AISC F11 para barra chata, Cb=1; resistência nominal dividida por γa1=1,10 |
| Interação | Envoltória linear abs(N)/NRd+abs(M)/MRd+abs(V)/VRd; hipótese explícita do modelo de componentes |
| Horizontais frontais | Faixa biapoiada entre mesas, H máximo no centro: M=abs(H)·s/4; corte abs(H)/2; largura b−2c; flexão no plano da chapa |
| Soldas | Filetes duplos contínuos; interfaces nervura–alma, nervura–horizontal, horizontal–mesa e horizontal–alma; metal-base das duas peças, sem duplicar sua espessura |
| Alma da coluna | Corte local em duas faixas de área H·tw; não substitui análise global da seção/painel da coluna |

Áreas dos blocos, por peça de espessura t: axial U: Agv=2et, Anv=2(e−dn/2)t, Ant=(n−1)(p−dn)t. Vertical L: lv=ev+(n−1)p, Agv=lv·t, Anv=[lv−(n−0,5)dn]t, Ant=(e−dn/2)t. Em ambos, R=min(0,6fu·Anv+0,5fu·Ant; 0,6fy·Agv+0,5fu·Ant)/γa2. A interação pelos módulos das forças é uma envoltória de implementação, não uma fórmula normativa específica desta ligação.

Comprimentos do modelo de barras chatas: talas, L=2e+g e K=1; aba livre da nervura, L=u+g/2 e K=2; trecho interno, L=b+u+g/2 e K=2; faixa conectada da alma da viga, L=e+g/2 e K=2. A área das talas é somada para resistência, mas a instabilidade é de cada chapa isolada.

Calços: duas chapas de metade da diferença de espessuras, na peça central mais fina e cobrindo toda a região parafusada. Não se soma sua espessura a Ag/An ou ao contato da peça. Para soma ts≤6,3 mm, sem redução; entre 6,3 e 19 mm, fator `1−0,0154(ts−6,3)` no corte e contato. Acima de 19 mm, a geometria é recusada. A alternativa sem calço admite até 1 mm como tolerância de detalhamento informada, não como dispensa da exigência de contato firme.

Geometria: passo mínimo/máximo, bordas mínimas/máximas, furos, concordâncias dos perfis, espaço para porca/ferramenta, afastamento da coluna, altura entre horizontais, alívios e filetes mínimos/máximos. Furos padrão; acréscimo de 2 mm para dedução líquida quando não marcada a execução com broca. A307 não está disponível nesta ligação.

As ações recebidas não são majoradas. Se a resultante for menor que 45 kN e o mínimo estiver ativo, há uma segunda conferência com as ações proporcionais. Zero N e zero V não geram resistência, pois não definem a direção do mínimo. Desativar o mínimo é modo de comparação e deixa pendência visível.

## Limitação que impede aprovação integral

**A estabilidade acoplada e a capacidade de rotação do conjunto nervura–enrijecedores–coluna não estão validadas para esta configuração com duas talas.**

Isso inclui a função de contenção dos horizontais: resistência, rigidez e forças fora do plano, suas soldas e participação do par oposto. Os cálculos no plano sob H não resolvem esse mecanismo. Não se atribuem forças fictícias de estabilização por simples percentual de N, nem se apresenta uma rigidez auxiliar como comprovação da estabilidade global do nó.

As verificações de componentes são úteis para revisão e desenvolvimento do detalhe, mas podem não governar o comportamento real da montagem. A aprovação da geometria não é validação do modelo de barras chatas, da rótula nominal ou da estabilidade do painel da nervura. O status é sempre **VERIFICAÇÃO INCOMPLETA** quando os componentes passam; falhas geométricas e resistentes têm prioridade sobre esse status.

Também não entram: análise global dos membros, forças de outras vigas no mesmo nó, fadiga, atrito, vibração, ações cíclicas, incêndio e corrosão. Contenção eficaz da viga e juntas internas dos perfis soldados com penetração total são premissas fixas. Furos alongados, grupos assimétricos, mesas recortadas e posições excêntricas em altura exigem outra configuração.

## Referências e rastreabilidade

- ABNT NBR 8800:2024, versão corrigida 2025, itens 5.3, 6.1.5, 6.2, 6.3 e 6.5. Catálogo oficial consultado em 09/10/2026: https://abntcatalogo.com.br/default.aspx. No exemplar fornecido, o sinal de L/r em 6.5.4-b é inconsistente com a distinção entre escoamento e instabilidade; aplica-se a curva χ inclusive nas barras curtas, sem dispensar a instabilidade.
- AISC 360-22, seção F11; AISC Design Examples v16.0, P901-23W, Parte II, emendas de alma. Apoiam componentes e equilíbrio de emenda; não fornecem validação integral automática para o nó aqui descrito.
- Fortney e Thornton (2016), *Analysis and Design of Stabilizer Plates in Single-Plate Shear Connections*, Engineering Journal 53(1), 1–28. https://doi.org/10.62913/engj.v53i1.1095.
- Sapkota, Rassati, Swanson e Dowswell (2024), *Behavior of Extended Single-Plate Shear Connections Subjected to Combined Shear and Compression Forces Using Finite Element Analysis*, Engineering Journal 61(4), 193–216. https://doi.org/10.62913/engj.v61i4.1332.

NBR governa resistências de cálculo; referências estrangeiras são complementos identificados. Não se transferem fatores LRFD ou resistências de um detalhe diferente por uma conversão global. Textos integrais e imagens das publicações não são redistribuídos com o app.
