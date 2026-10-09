# Verificação da versão 0.5.1

> Registro técnico histórico. A versão 0.7.1 permite calcular com avisos de montagem e restaura o complemento entre mesas apenas no detalhamento, sem verificações extras nem crédito resistente. As referências ao bloqueio dessa opção descrevem o comportamento anterior. Consulte AJUSTES_V071.md.

113 testes de software aprovados. 13 comparações pontuais com referências aprovadas; ver benchmarks.json. Os dados de cada exemplo e cada verificação estão em registro_validacao.json. Testes não autorizam configurações excluídas ou mecanismos pendentes.

Os testes da revisão 0.5.1 conferem a nota única no Word, a exclusão dos cálculos isolados sob carregamento combinado, a preservação do modelo de N centrado, as prioridades de falha e os elementos visíveis da interface.

Os demais testes incluem integração independente de p(y), resultantes T/C, transferência |V|tf, expressão de enrugamento NBR com solução manual de 300 kN, migração da hipótese de contenção, penetração total e rejeição da variante retirada. A lógica não foi alterada para apagar a reprovação do exemplo didático W310→W150.

Executar, da pasta que contém app.py: python -m pytest -q
