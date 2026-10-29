# Critérios de mineração e seleção

## Objetivo e unidade de coleta

O objetivo é coletar cenários com contribuições das duas branches para permitir investigações posteriores. A unidade é o **par arquivo–merge**: um caminho de arquivo associado a uma junção específica. Um mesmo caminho pode aparecer em vários merges. Um cenário selecionado não significa que exista defeito.

## Escolha dos repositórios

### Underscore: projeto do piloto JavaScript

Repositório: https://github.com/jashkenas/underscore

Escolhemos o projeto porque contém JavaScript, possui histórico acessível com merges antigos e permite recuperar base, pais e versão integrada. Esses fatores permitiram verificar a coleta em um lote pequeno.

A escolha foi por conveniência. Não aplicamos ranking quantitativo de popularidade, sorteio entre projetos ou avaliação de representatividade. Não estabelecemos se o projeto integra a lista original dos 50 projetos do artigo da Amanda.

### jsFSTMerge: exploração auxiliar

Repositório: https://github.com/AlbertoTrindade/jsFSTMerge

Foi escolhido por ser uma ferramenta de merge para JavaScript desenvolvida na UFPE e relacionada ao tema. Sua implementação é principalmente Java. A exploração encontrou 11 pares candidatos `.java` e nenhum `.js`, segundo o coletor exploratório. Portanto, ele não integra o lote JavaScript processado pelo MiningFramework oficial.

## Recorte temporal da exploração

No Underscore, consideramos merges com **data de calendário do committer até 31/12/2014, inclusive**, entre os ancestrais alcançáveis do HEAD congelado.

O motivo foi reduzir possíveis problemas com recursos de linguagem mais modernos em etapas futuras. O corte não garante compatibilidade de sintaxe e não foi apresentado como o limite temporal exato utilizado pela Amanda.

HEAD congelado: `5c1e5f686f8500af9c9d15614ed60289d6d35d6b`.

Dos 829 merges alcançáveis desse HEAD, 320 ficaram depois do recorte e 509 entraram na inspeção. Não enumeramos todas as branches e pull requests do servidor.

## Filtros do coletor Git/Python

O script `scripts/minerar_merges.py` aplicou estes passos:

1. Exigir histórico completo, sem clone raso.
2. Enumerar merges do HEAD com `git log --merges --reverse --topo-order`.
3. Aplicar o recorte de data quando definido.
4. Exigir exatamente dois pais.
5. Exigir um único ancestral comum retornado por `git merge-base --all`.
6. Excluir casos em que o ancestral coincide com um dos pais.
7. Comparar base→Left e base→Right e intersectar os caminhos alterados, sem detecção de renomeação.
8. Selecionar a extensão `.js` no Underscore.
9. Registrar se o caminho existe nas quatro versões: base, Left, Right e merge.

Resultado: 184 pares candidatos em 146 merges; 181 têm as quatro versões. Os três restantes permanecem sinalizados na tabela como versões ausentes.

Dos 509 merges, 260 foram excluídos porque um pai era ancestral do outro, 1 não tinha ancestral comum único e 102 não apresentaram arquivo comum da extensão selecionada. Os outros 146 forneceram candidatos.

Esse filtro considera caminhos alterados e pode incluir adições/remoções. Ele não é idêntico ao filtro de status `M` utilizado pelo módulo oficial.

## Seleção dos cinco merges do piloto oficial

Na exploração, o script exportou os **cinco primeiros pares completos disponíveis** na ordem do log topológico reverso, com os caminhos candidatos ordenados por nome dentro de cada merge. Nesse resultado específico, esses cinco pares pertenciam a cinco merges distintos.

Os SHAs desses merges e de seus pais foram transferidos para `experimentos/miningframework/commits_piloto.csv`, a lista explícita de entrada da execução oficial.

- A seleção foi por conveniência, seguindo uma ordem determinística.
- Não foi um sorteio de merges nem uma amostra representativa.
- `--random-seed 1` da ferramenta oficial embaralhou a ordem de processamento da lista. Isso não tornou aleatória a escolha dos cinco merges.
- O merge `a2aab7c69968` já estava na lista do piloto. Ele não foi inicialmente escolhido por um resultado favorável de análise.
- A lista já contém merges anteriores a 2015. Não aplicamos novamente uma opção de data na invocação oficial.

| Merge completo | Arquivos produzidos pelo coletor oficial |
| --- | --- |
| `2b9a011e070b01cf1e6957333fcb425a638c0465` | `underscore.js` |
| `8c15ae153aae4eb4537121fae9fc3a3bef84ded7` | `underscore.js` |
| `a2aab7c6996835d453972b22999b80dbfe125db5` | `underscore.js`, `test/utility.js` |
| `b5f111e8d4b3bbe9ece4ebac39f91d10ea11b7db` | `test/utility.js` |
| `e863fbf285f75063a982332d55926e5cc85f1626` | `underscore.js` |

## Filtro e coleta da ferramenta oficial

Executamos o módulo `DynamicAnalysisJsModifiedLinesDetectionModule`, no commit `7a9503f0e3af110fb0028fb02753d4c4a627266e` do MiningFramework.

O módulo utiliza:

- `MutuallyModifiedFilesCommitFilter`: exige ao menos um caminho da extensão indicada com status `M` em ambas as comparações base→pai.
- `ModifiedFilesLinesPerFileCollector`: coleta os arquivos alterados em comum e as linhas de adição, remoção e mudança de cada pai.
- `StatisticsCollector`: registra as estatísticas auxiliares da ferramenta.

A extensão fornecida foi `.js`. Os seis registros produzidos foram conferidos no histórico, incluindo a condição de modificação dos dois pais. A saída original permanece em `resultados/miningframework/saida_oficial/data/results.csv`.

As linhas dessa tabela se referem às comparações com os pais. A tabela não é um mapa pronto de autoria das linhas da versão integrada.

## Critérios que ainda não aplicamos

Não exigimos evidência prévia de defeito, alterações em linhas executáveis, capacidade de execução isolada do arquivo, testes utilizáveis, cobertura das contribuições ou representatividade estatística.

Por exemplo, o merge `2b9a011e070b` contém, em uma das contribuições, uma alteração apenas em comentário no arquivo selecionado. Ele satisfaz o filtro textual, mas ilustra por que a coleta é somente uma pré-seleção.

## Decisões a alinhar com o orientador

- Definir o universo de projetos e justificar sua entrada.
- Decidir se a coleta definitiva deve excluir comentários, formatação e código não executável.
- Definir tamanho da amostra e eventual método de sorteio.
- Tratar renomeações, remoções e múltiplos ancestrais sem descartes silenciosos.
- Preservar decisões e exclusões por cenário.

A auditoria reproduzível dos seis registros está em `scripts/auditar_criterios_mineracao.py`. Ela confirma critérios verificáveis, sem tornar o lote representativo.
