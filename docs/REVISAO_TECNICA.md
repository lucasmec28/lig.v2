# Revisão técnica da versão 0.3

Esta atualização implementa verificações antes pendentes. Não conclui todos os modelos solicitados: a tração fora do plano da alma do apoio e a chapa soldada entre mesas, com ou sem enrijecedor oposto, continuam sem aprovação estrutural automática.

## O que foi resolvido

- Grupo elástico bidimensional com uma ou duas colunas de parafusos; verificação explícita de equilíbrio.
- Espessura máxima da chapa para ductilidade, usando o CIR do grupo sob momento puro quando a dispensa geométrica não se aplica.
- Redução da resistência por pega longa, conforme NBR 8800, 6.3.7.
- Recortes superior e duplo: seção remanescente, seção líquida, flexão, estabilidade local, ruptura, interação conservadora N/V/M e ruptura em bloco da alma. A contenção lateral na raiz do recorte deve ser confirmada.
- Instabilidade por corte da alma sem recorte, com kv = 5,34 da norma atual. Na área local adota-se h·tw, conservador em relação à área d·tw da barra.
- Solda mesa–alma de pilar soldado: novo campo para o filete duplo real e verificação da transmissão local ao metal de solda e à alma. Zero significa não informado.
- Desenvolvimento da chapa pela solda: formulação geral em função de fy e fw, preservando o mínimo 5t/8. USI-CIVIL 350 passa a ter cálculo explícito.
- Alternativa rigorosa de punção do SCI para corte puro; não aplicada indevidamente a N e V simultâneos.
- Aviso de borda mostra a − g, o limite em mm e o ajuste de a que permite preservar g.

## A folga g de 10 mm

A folga g mede a face do apoio até a extremidade da viga. A borda horizontal da alma é a − g, e não g. A borda livre da chapa é outra cota, eₕ.

Na print: a = 120 mm; g = 40 mm; tw = 6,5 mm. A borda resulta em 80 mm, maior que min(12tw; 150) = 78 mm. Com g = 10 mm, a deve ser no máximo 88 mm para esse limite; a = 75 mm fornece borda de 65 mm. As demais exigências continuam sendo verificadas.

Em viga–viga com mesas no mesmo nível, g = 10 mm geralmente exige recorte para eliminar a interferência com a mesa do apoio. O exemplo novo usa a = 75 mm e recorte superior de 80 × 25 mm. Esses valores não são impostos a todo projeto.

## Prioridade normativa

As resistências brasileiras usam a ABNT NBR 8800:2024, versão corrigida 2025 fornecida. No cisalhamento de parafusos, usa-se 0,45 com a rosca no plano de corte e 0,56 quando excluída, conforme o caso; para A307 usa-se 0,45 independentemente da posição da rosca. O valor antigo 0,40 não é usado no dimensionamento atual.

Referências AISC/SCI complementam mecanismos e modelos que a implementação identifica. Não são misturados fatores de ações nem aplicados fatores globais a resultados LRFD prontos. Exemplos históricos mantêm seus dados apenas para conferência identificada.

## Situação dos casos

| Caso | Situação na v0.3 |
|---|---|
| Chapa retangular na mesa de pilar laminado; N e V | Verificações locais implementadas, dentro das hipóteses registradas |
| Chapa retangular na mesa de pilar soldado; N e V | Acrescentadas solda mesa–alma e metal-base; informar a solda real |
| Chapa retangular na alma de viga; V puro | Verificações locais implementadas, inclusive recorte com contenção confirmada |
| Chapa retangular na alma de viga; N > 0 e V | Flexão fora do plano da alma do apoio ainda pendente |
| Duas colunas de parafusos em chapa retangular | Grupo e caminhos completos calculados; mesmas limitações do apoio |
| Chapa soldada à alma e às duas mesas do apoio | Apenas pré-detalhamento, sem resistência calculada |
| Enrijecedor oposto | Geometria; não recebe ganho automático de resistência |

A análise global das barras, da contenção e dos seus elementos de ligação permanece no projeto estrutural. A versão não dimensiona fadiga, atrito, ações cíclicas, incêndio ou compressão axial na single plate.

## O que ainda exige trabalho

**Alma do apoio sob N:** definir e validar o modelo de flexão fora do plano e sua interação com o estado de tensões do apoio. Resistência à punção, corte local e capacidade de amarração acidental não substituem automaticamente esse cálculo para N e V simultâneos.

**Chapa entre mesas:** validar distribuição de esforços na região de transição, soldas à alma e às mesas, estabilidade, efeito do enrijecedor oposto e capacidade de rotação. A literatura registra que estender a chapa às mesas não garante aumento da resistência à instabilidade. Não se deve usar a fórmula da chapa retangular sem justificar suas condições de contorno.

Essas duas pendências são de desenvolvimento e validação do modelo. A documentação enviada já permitiu as demais implementações; não é necessário pedir novamente todos os materiais.

## Dados reais necessários para usar a ligação no pilar

Confirmar a designação e dimensões do perfil, o filete contínuo mesa–alma, seu eletrodo e a contenção real da viga. O catálogo contém CS600×281; isso não confirma que o pilar informado como CVS600×281 seja essa seção. O exemplo exportado adota explicitamente CS600×281 e filete de 6 mm para demonstração.
