# End plates na mesa de coluna

Versão 0.7.0. Modelo plano; N em tração é positivo. V e N são forças; M atua no eixo forte. Unidades internas N, mm e MPa. Referência normativa principal: ABNT NBR 8800:2024, versão corrigida 2025, arquivo fornecido pelo usuário.

## Rigidez e âmbito

A NBR 6.1.2.1 distingue rigidez rotacional da mera resistência. O limite rígido Si ≥ 25EI/L e a condição Kv/Kp ≥ 0,1 de 6.1.2.2 dependem da estrutura. Esta versão adota a alternativa simplificada de 6.1.2.3 para detalhes usuais, a critério do responsável técnico. Não informa um valor de Si que não foi calculado.

Na engastada, o complemento construtivo é o AISC DG39, §3.2 e §5.1.1: configuração 4E não enrijecida e critério de chapa espessa, com γr=1. O app exige:

`tp ≥ sqrt[1,10 Meq max(1,10; 1/0,90)/(fy Yp)]`.

A mesa da coluna recebe a mesma verificação com tfc, fyc e Yc. A presença do fator 1/0,90 impede que a troca dos coeficientes torne a espessura menor que o mínimo do procedimento original. Não há conversão indiscriminada de capacidades LRFD para NBR. A resistência do mecanismo é fy t² Y/γa1 e a condição de chapa espessa é verificada separadamente.

DG39 tabela 5-10, com `s=sqrt(bp g)/2`, `pi=min(pfi;s)`, `h1=d−tf/2+pfo`, `h2=d−1,5tf−pfi`:

`Yp=(bp/2)[h1/pfo+h2(1/pi+1/s)−1/2]+(2/g)h2(s+pi)`.

DG39 eq.3-44, coluna contínua sem enrijecedores, `sc=sqrt(bfc g)/2`, `c=pfo+tf+pfi`:

`Yc=(bfc/2)(h1+h2)/sc+(2/g)[h2(3c/4+sc)+h1(c/4+sc)+c²/2]+g/2`.

A chapa estendida só acima não é extrapolada para o momento inverso, que exigiria o modelo flush do lado inferior. Para M negativo, selecionar extensão acima e abaixo. Se a espessura falhar, o app reprova a hipótese de chapa espessa; não aprova silenciosamente uma chapa fina sem calcular alavanca.

Na rotulada, o detalhamento complementar é SCI P358 (2014), 4.7, Check 1, incluindo gabarito e limites de espessura. O aço é limitado a fy ≤ 275 MPa. As resistências usam a NBR. Para tração permanente/combinada, não se usam capacidades de amarração acidental do SCI como se fossem de uma combinação normal. Exige-se chapa rígida contra alavanca sob a ação dada pela NBR 6.3.5.3, sem inferir daí rigidez rotacional do nó.

## Distribuição de ações

4E: `Meq=|M|+max(N;0)(d−tf)/2`; dois parafusos em cada uma das duas linhas tracionadas; `Ft=Meq/[2(h1+h2)]`. Despreza-se o alívio de tração causado por N negativo, formando envelope conservador. A compressão de contato usada é `max(0;4Ft−N)`. A força por parafuso em corte é `|V|/n_total`, inclusive nos parafusos tracionados. A superposição do axial é limitada ao domínio do DG39 §3.5: `|N|(d−tf) ≤ |M|`.

Rotulada: `Ft=max(N;0)/n_total`. A tração é atribuída à alma para conferir solda e metal-base, sem ganho das mesas. A compressão é transmitida pelo contato chapa–mesa da coluna. Não há solda direta viga–coluna.

Mínimo de 45 kN: escala-se somente o vetor N/V. A entrada e a conferência mínima são calculadas; M permanece igual ao informado. Se o novo N ultrapassar o domínio do 4E, não são emitidas capacidades desse modelo. NBR 6.1.5.3 trata de recomendação para ligações de barras axiais; não se criou um mínimo de momento com base nessa cláusula.

## Parafusos, chapas e soldas

- NBR 6.3.2.2 e 6.3.3.1: `Abe=0,75Ab`, `Ft,Rd=Abe fub/γa2`.
- NBR 6.3.3.2: `Fv,Rd=kpega α Ab fub/γa2`, α=0,45 com rosca ou 0,56 sem rosca. Um plano de corte. Coeficiente de pega herdado e testado do módulo local.
- NBR 6.3.3.4: interação **quadrática**, `(Ft/Ft,Rd)²+(Fv/Fv,Rd)² ≤ 1`. Não se confundem as alternativas da tabela 12 com exigências adicionais à equação quadrática.
- NBR 6.3.3.3: contato/rasgamento com deformação de furo limitada: `min(1,2 lc t fu;2,4 db t fu)/γa2`.
- NBR 6.3.5.3: `tmin=sqrt[4(b−db/2)Ft,0,Sd γa1/(p fu)]`. Para a rotulada, b vai do eixo do furo à face da alma; p resulta das faixas tributárias de 6.3.5.2. Usa-se a menor faixa em todos os parafusos, conservadoramente. A verificação abrange chapa e mesa da coluna.
- NBR 6.5.6: os blocos da chapa são percorridos nos dois sentidos de V e para todos os subconjuntos que terminam nas bordas superior/inferior; Ct=0,5. A demanda de cada bloco é proporcional ao número de parafusos contidos.
- Rotulada: dois filetes na alma recebem integralmente a resultante N/V, sem crédito aos filetes nas mesas. Comprimento útil reduzido em 2w. Verifica-se também o metal-base. Reforço da borda deve ser executado quando selecionado.
- Engastada: juntas de penetração total nas duas mesas e na alma, eletrodo compatível; gargantas limitadas às menores espessuras ligadas. Combinação elástica conservadora dos máximos de tensão normal e cisalhamento com o menor fy do metal-base. Verifica-se separadamente o cisalhamento da alma da viga.

## Coluna e montagem

A mesa da coluna deve atender à espessura necessária contra alavanca. Escoamento local e enrugamento da alma seguem NBR 5.7.3 e 5.7.4 com hipóteses conservadoras de carga pontual na engastada, caso de extremidade e k=tf, sem ganho da concordância ou do espalhamento.

O painel na engastada usa 5.4.3 e 5.7.7, sem contribuição das mesas. Usa-se hc twc, menor que dc twc, e Cv da alma sem enrijecedores. Adota-se `Ncol,Sd ≤ 0,4 Ag,col fy,col`; não é uma verificação da força axial global da coluna. A demanda conservadora não desconta o cortante favorável da coluna. Não há crédito a uma viga oposta.

Os espaçamentos mínimo e máximo, bordas, furos padrão e interferências com mesas, almas, concordâncias, soldas e ferramenta são conferidos. Limites máximos são aplicados à região em contato da chapa com a coluna; prolongamentos da coluna contínua fora dessa região não são tratados como bordas livres de uma emenda sobreposta. A proteção contra corrosão é premissa do limite 24t/300 mm. Parafusos com protensão inicial; não há crédito ao atrito.

Nenhuma das famílias é modelo sísmico ou de fadiga. Análise global, segunda ordem, estabilidade global dos membros e compatibilização dos vínculos não são substituídas por essas contas locais.

## Conferências reproduzíveis

`tests/test_end_plate.py` compara Yp e tp com o exemplo 5.3-1 do DG39: Yp≈186 in e tp≈0,589 in, além de refazer a conta em mm. Há substituição independente de Yc, chapa rígida e interação da NBR, testes de sinais e domínio e regressão da interface. As verificações não representam reprodução integral de todos os estados-limite desse exemplo ou validação experimental.
