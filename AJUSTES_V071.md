# Ajustes da versão 0.7.1

## Interferências e cálculo

Avisos de concordância dos perfis, contato entre peças e acesso de porcas/ferramentas não interrompem as equações quando existem os dados e os ligamentos necessários. O cálculo mantém as dimensões nominais e não faz alívios automaticamente. A mesma classificação é usada para os avisos de montagem identificados nas duas talas e nas end plates.

As entradas que inviabilizam as equações ou saem do domínio mecânico permanecem bloqueadas: dimensões não positivas, valores não finitos, furos sem ligamento, material incompatível, arranjos não implementados e demais limites exigidos pelo modelo. Os requisitos normativos de espaçamento, borda e soldagem não foram dispensados. Um aviso de ferramenta que compartilha a mesma condição com uma borda mínima é separado: o limite da borda continua sendo obrigatório.

Se os componentes calculados passam, mas há interferências, o resultado é `CÁLCULO ATENDE · CONFERIR INTERFERÊNCIAS`. Uma resistência excedida continua produzindo `NÃO ATENDE`. Os avisos são exibidos em amarelo, permitem a geração do Word e aparecem nas premissas finais. Se o ajuste de fabricação alterar furos, seção resistente ou comprimento útil de solda, os dados devem ser atualizados e recalculados.

## Complemento até as mesas

Opção exclusiva da single plate na alma da viga de apoio. O contorno vai da face inferior da mesa superior à face superior da mesa inferior, com largura e alívio de canto ajustáveis, na mesma espessura da chapa. O filete às mesas é uma especificação de detalhamento.

O motor usa a mesma chapa retangular nominal de altura hₚ, os mesmos parafusos, as mesmas excentricidades e a mesma solda à alma que usaria sem o complemento. Não se acrescentam verificações, área resistente, comprimento de solda ou redução de excentricidade pelo complemento. Não são chamadas as rotinas históricas de grupo de soldas entre mesas, compacidade do complemento ou enrijecedor oposto.

A estabilidade do complemento e a redistribuição de esforços por ele não são avaliadas. Essa premissa está ao final da página e da memória. O enrijecedor oposto permanece indisponível. O JSON conserva a geometria solicitada; a simplificação do cálculo não reescreve o projeto como uma chapa retangular.

## Reprodução do projeto recebido

W150×13,0 em W250×22,3; chapa USI-CIVIL 300 de 5/16”; dois parafusos de 5/8”; p = 60 mm; bordas = 30 mm; a = 90 mm; g = 60 mm; z = 14 mm; solda de 3 mm. Ações de entrada preservadas: V = 8139,5195 N e N = 18632,635 N. Conferência mínima de 45 kN mantida conforme a opção salva no projeto.

O projeto produz 24 verificações. O resultado é `NÃO ATENDE`: há falha no contato/rasgamento da alma da viga, na solda, na hierarquia contra punção e nos critérios de ductilidade/desenvolvimento da solda. As interferências passam a ser avisos e não escondem esses resultados. O registro numérico completo está em `registro_v071.json`.

O segundo exemplo acrescenta apenas o complemento, com largura ilustrativa de 45 mm. As 24 verificações, solicitações e resistências são idênticas às do primeiro. Ambos os Word registram os avisos e as premissas ao final.
