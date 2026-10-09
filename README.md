# LRO Ligações — versão 0.6.0

Desenvolvido por LRO Soluções de engenharia LTDA.

[LinkedIn — Lucas Oliveira](https://www.linkedin.com/in/lucas-oliveira-722723149/?isSelfProfile=true)

Agora há duas famílias no seletor lateral: **Single plate** e **Alma de coluna · duas talas**. Forças em kgf, momentos derivados em kgf·m e dimensões em mm. Entradas já majoradas; o mínimo resistente de 45 kN é conferido separadamente.

## Nova ligação à alma da coluna

A viga e a nervura são unidas por duas talas independentes, somente parafusadas. A nervura é soldada ao conjunto da coluna, que tem quatro horizontais: dois níveis, frente e verso. Não há solda direta da viga ou das talas na coluna.

- Cortante vertical e axial com sinal: positivo para tração, negativo para compressão. Sem momento externo; as excentricidades locais são calculadas.
- Uma coluna de parafusos por lado, com grupos iguais. Cada grupo transmite a resultante integral; cada tala recebe metade. Parafusos em corte duplo.
- Folga `g` entre a ponta da nervura e a viga, inicialmente 10 mm. `u` mede a projeção da nervura além da mesa da coluna.
- Calços simétricos na peça central mais fina; as reduções normativas por enchimento abrangem corte dos parafusos e contato. Alternativa de pequena diferença de montagem limitada a 1 mm, explicitamente sem caráter de tolerância normativa.
- Desenho proporcional, alertas geométricos, 30 verificações de componentes, projetos JSON próprios e memória Word com equações editáveis.

**Limitação desta versão:** a estabilidade acoplada e a capacidade de rotação do conjunto nervura–enrijecedores–coluna não estão validadas para esta configuração com duas talas. A função dos horizontais como contenção, incluindo rigidez e forças fora do plano, permanece nessa pendência. Por isso o app apresenta **VERIFICAÇÃO INCOMPLETA** mesmo se todos os componentes calculados atenderem. Não há aprovação integral deste novo nó.

Os exemplos `Duas_talas_tracao` e `Duas_talas_compressao` usam W360×39 → HP250×62 e V=11 kN, N=±2 kN. São exemplos de uso do modelo local, não detalhes homologados. Ambos têm maior índice calculado de aproximadamente 0,611, governado pelos horizontais sob a conferência mínima. O exemplo adaptado da planilha recebida mantém sua geometria inicial e acusa incompatibilidades; não foi ajustado silenciosamente para passar.

Documentação: `docs/DUAS_TALAS_METODOLOGIA.md` explica o modelo; `docs/AUDITORIA_PLANILHA.md` registra a revisão do arquivo recebido. As duas memórias novas têm seis páginas no modo compacto. O modo detalhado acrescenta as substituições dos demais componentes.

## Atualizar e abrir

1. Pare o aplicativo no terminal com **Ctrl+C**.
2. Extraia este pacote em uma **pasta nova** e preserve seus projetos JSON.
3. Abra o terminal na pasta que contém `app.py`. Ative seu ambiente Python 3.12 e execute:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Se ainda não houver ambiente: `python -m venv .venv`; no PowerShell, ative com `.venv\Scripts\Activate.ps1`. Para evitar problemas de política do PowerShell, também é possível executar diretamente `.venv\Scripts\python.exe -m pip install -r requirements.txt` e `.venv\Scripts\python.exe -m streamlit run app.py`.

A atualização é local; este pacote não altera seu app hospedado. Para hospedagem, atualize também `lro/`, `data/` e os demais arquivos do repositório, preservando a estrutura. Não envie `.venv`.

## Single plates mantidas da versão 0.5.1

Na revisão 0.5.1, a interação fora do plano da alma do apoio passa de pendência para exclusão explícita, conforme solicitado. A nota não atribui resistência ao mecanismo omitido.

- **Contenção eficaz da viga apoiada é fixa**, inclusive na importação de projetos antigos. Não há pergunta na tela nem cálculo de cortante horizontal/momento no eixo de menor inércia. N axial permanece como entrada.
- A solda da ligação é **single plate → apoio**. A viga apoiada é parafusada à chapa.
- Os perfis soldados têm juntas internas mesa–alma de **penetração total, com metal de adição compatível**, por hipótese; não se informa filete de fabricação.
- Para o pilar, admite-se impedido o deslocamento lateral relativo entre as mesas na região da ligação. Essa premissa é registrada e independe da penetração total. A estabilidade global continua no projeto estrutural.
- **Chapa/enrijecedores entre mesas foram retirados**. Há aviso curto; essa variante não é avaliada nem convertida automaticamente ao abrir arquivos antigos.
- Geometrias e esforços dos dois testes enviados foram preservados. As hipóteses acima são novas e ficam expressas no JSON e no Word.

## O que os exemplos mostram

| Exemplo | Resultado | Maior índice resistente |
|---|---|---:|
| W410×38,8 → CS600×281, g=10 mm | Atende ao escopo local e às premissas declaradas | 0,454 |
| W360×39 → W410×38,8, g=80 mm | Atende às verificações realizadas; interação da alma excluída | 0,669 |

**Nota de escopo:** Não é verificada a interação fora do plano da alma da viga de apoio sob N+V ou N excêntrico. O app e o Word indicam essa exclusão junto ao resultado. O atendimento refere-se somente aos itens calculados. Os cálculos isolados de plastificação e punção sob N, e o campo de distância longitudinal, ficam restritos à tração centrada sem cortante. Outras falhas e pendências continuam sendo sinalizadas.

O perfil utilizado nos arquivos enviados é **CS 600×281**, não CVS. O catálogo ou a seção personalizada permite escolher outro perfil real; não existe equivalência automática entre essas designações.

## Arquivos e verificação

`examples/` contém os projetos, desenhos SVG e memórias Word. As memórias com sufixo `v05` são exemplos históricos das single plates, cujo motor não foi alterado nesta revisão. O arquivo `Teste_usuario_v03_original.json` preserva a entrada original para conferir a migração. `docs/REVISAO_TECNICA.md` e `docs/METODOLOGIA.md` documentam as single plates; os documentos `DUAS_TALAS_*` descrevem a nova família.

**147 testes de software aprovados**, dos quais 113 já pertenciam às single plates. Mantidas as 13 comparações pontuais anteriores; os novos testes incluem equilíbrio independente, corte duplo, combinação N/V, calços, curva de compressão e interface. Não são validação experimental integral do nó. O exemplo didático single plate W310→W150 mantém sua reprovação pelo critério conservador de escoamento localizado no pilar (índice 1,010).

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Nas single plates, projetos dos esquemas 1–3 são aceitos e exportados no esquema 4; a antiga variante entre mesas continua recusada. A ligação com talas possui tipo JSON próprio, `column_web_double_cover`, esquema 1. Escolha a família correta antes de importar. O estado exibido inclui limites de modelo além dos índices de resistência.
