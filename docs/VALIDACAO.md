# Verificação da implementação v0.3

Os testes automatizados verificam a implementação e as regressões. Não equivalem a uma certificação do programa nem resolvem estados limite que permanecem fora de seu domínio.

## Comparações publicadas

Onze comparações estão em benchmarks.json e na aba Validação do app. Abrangem os sete componentes da versão anterior e quatro novos: C′ sob momento puro dos exemplos II.A-19A/19B; momento nominal do recorte simples II.A-6; momento nominal do recorte duplo II.A-7.

- II.A-19A: C′ calculado 26,0315 in, referência 26,0 in.
- II.A-19B: C′ calculado 38,6693 in, referência 38,7 in.
- II.A-6: seção T remanescente integrada sem raios, Z=32,2355 in³ e S=17,8623 in³. Momento nominal 1.232,67 kip·in, referência arredondada 1.230 kip·in; reação LRFD cerca de 116,8 kip, referência 116 kip.
- II.A-7: momento nominal aproximadamente 420,33 kip·in, referência 421 kip·in; reação LRFD 37,83 kip, referência 37,9 kip.

As comparações conservam as unidades e os coeficientes da publicação para reproduzir a referência. O dimensionamento da interface usa a NBR atual, com diferenças identificadas; não se exige igualdade entre resultados obtidos sob bases normativas diferentes.

## Casos de aplicação completos do motor

Os projetos JSON incluídos permitem repetir o cálculo, abrir os resultados e gerar Word. O registro automatizado lista todos os índices e pendências, preservando os esforços de entrada e o mínimo de 45 kN separado.

- Mesa de pilar CS600×281 com filetes mesa–alma de 6 mm e contenção adotados para demonstração: pode atender ao escopo local calculado. Esses dados não confirmam o pilar real do usuário.
- Viga–viga com g=10 mm e recorte superior: as verificações implementadas atendem ao exemplo, mas a alma do apoio sob N>0 continua pendente.
- O mesmo caso com V puro e contenção confirmada não possui essa pendência e é coberto pelos testes do motor.
- Duas colunas em chapa retangular na mesa de pilar: cálculo bidimensional e caminhos completos/parciais de bloco.
- Teste original enviado: preserva V=11 kN e N=5 kgf. A v0.3 identifica falhas nas condições de punção e ductilidade para os materiais e bordas informados; não muda silenciosamente a geometria para aprová-lo.

Esses ensaios integrados cobrem o fluxo do aplicativo; não são apresentados como comparação integral independente de todas as parcelas de uma ligação brasileira completa. As comparações publicadas são de componentes e modelos locais.

## Cobertura de testes

Equilíbrio do grupo em dois sentidos de V, área e módulos da seção recortada, fronteiras de pega longa e esbeltez, coeficiente 0,45 atual, domínio dos aços, importação JSON, invalidação de Word após alterações, geometria de g, quantidade de colunas, recortes, cargas insuficientes/excessivas e ausência de aprovação automática das variantes ainda pendentes.

Os relatórios finais são renderizados para conferência de todas as páginas. O catálogo contém 560 designações. As seções prioritárias foram confrontadas com os catálogos fornecidos; não se declara conferência independente de todas as 560 entradas.
