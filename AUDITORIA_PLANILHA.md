# Revisão da planilha recebida

Arquivo analisado: `01-Liga-o-Rotulada-Viga-at-Alma-de-Coluna.xlsx`. Leitura das fórmulas, resultados armazenados e figuras; o original foi preservado. A nova ligação segue a descrição confirmada pelo usuário: duas talas apenas parafusadas à nervura e à alma da viga, sem contato direto viga–coluna.

A figura incorporada ilustra uma nervura enrijecida, mas não representa explicitamente as duas talas descritas. Por isso ela não foi copiada como desenho do novo modelo.

## Pontos que impedem usar o resultado armazenado como validação

| Local | Achado | Tratamento no app |
|---|---|---|
| Ligação_por_Contato, B17 | Usa max(V,N)/(n linhas × n colunas) | Resultante vetorial por parafuso, incluindo o momento de excentricidade |
| Ligação_por_Contato, G16 | Coeficientes 0,40/0,50 da edição de 2008 | 0,45/0,56 e dois planos de corte, conforme detalhe com duas talas |
| B10 e G19 da mesma folha | Distância centro–borda utilizada diretamente na expressão do ligamento livre | Deduzir metade do diâmetro do furo e conferir o espaço livre entre furos |
| G28:G33 | Áreas de bloco sem correspondência completa com os caminhos da nova emenda; Anv e Ant repetidas | Caminhos U e L definidos pela geometria; ramo limitante e esforços combinados |
| Listas de materiais | Fórmulas contêm vínculos externos `[1]` | Catálogo local, produto e faixa de espessura explícitos |
| Resumo na folha principal | Parte dos resultados de parafusos permanece preenchida com outro diâmetro/quantidade | Resultado único derivado das entradas atuais; exportação invalidada ao alterá-las |
| Compressão e estabilização | Não demonstram o comportamento do conjunto com talas sob N negativo | Avaliações locais de compressão e pendência explícita do mecanismo acoplado |

Com V=45 kN e N=70 kN, dois parafusos têm resultante direta de **41,608 kN por parafuso**, antes de qualquer excentricidade. O uso de max(V,N)/2 fornece 35 kN. Não se trata de diferença de arredondamento. N é axial na viga e provoca corte transversal nos parafusos desta emenda; não é tração no eixo dos parafusos.

Os dados armazenados indicam W150×13 e HP250×62, passo aproximado de 37,33 mm e altura conectada de 112 mm. Para o diâmetro de 5/8 pol. usado na adaptação, o passo mínimo adotado é 42,86 mm. A altura também invade a folga de montagem adotada junto às concordâncias da viga. Uma das combinações de chapa/filete conflita com o limite de borda sem execução reforçada. O preset **Geometria inicial da planilha · revisar** mostra essas incompatibilidades e não gera memória resistente enquanto elas persistirem.

As talas e algumas medidas ausentes foram complementadas apenas para representar a topologia solicitada. Assim, esse preset não é reprodução integral ou validação numérica da planilha original.

## Verificação do software entregue

147 testes passaram, incluindo 113 testes preservados das single plates e 34 novos casos. Os novos cobrem equilíbrio por soma de forças e momentos, corte duplo independente, resultante N/V, sinais de compressão, calços nos limites de 6,3 e 19 mm, contato da peça mais fina, área efetiva das talas, curva de instabilidade, rejeição de interferências e atualização dos relatórios.

Os testes verificam a implementação das equações declaradas; não demonstram por ensaio ou análise não linear a estabilidade e a capacidade de rotação desta montagem. As 30 avaliações calculadas não são “100% do nó”. O app e o Word mantêm a pendência técnica junto ao resultado.
