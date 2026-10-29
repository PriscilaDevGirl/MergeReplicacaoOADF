# Relatório da mineração piloto

## Escopo

Este relatório documenta a coleta de cenários de merge e seus critérios. Há duas etapas: uma exploração com Git/Python e um lote de validação com o MiningFramework oficial.

| Medida | Underscore, Git/Python | Underscore, MiningFramework oficial |
| --- | ---: | ---: |
| Merges alcançáveis do HEAD congelado | 829 | Não usado como universo desta execução |
| Merges no recorte até 31/12/2014 | 509 | Lista explícita de 5 merges |
| Merges com candidatos | 146 | 5 |
| Pares arquivo–merge | 184 | 6 |
| Pares com quatro versões disponíveis | 181 | 6, conferidos pela auditoria |
| Caminhos distintos do lote oficial | Não é a unidade resumida | 2 |

A exploração exportou cinco pares completos para inspeção, correspondentes a cinco merges distintos. O lote oficial recebeu esses merges por lista explícita. Um deles produziu dois arquivos, totalizando seis registros.

Os caminhos oficiais são `underscore.js` e `test/utility.js`. A unidade é a versão de um arquivo em um merge, não o nome do arquivo isolado.

## Exploração auxiliar

O histórico do jsFSTMerge foi examinado com Git/Python: 13 merges, 6 merges candidatos e 11 pares de arquivos Java, dos quais 10 com as quatro versões disponíveis. Ele não forneceu candidatos JavaScript com os critérios usados e não integra o lote oficial.

## Referências congeladas

| Item | Referência |
| --- | --- |
| Underscore | `https://github.com/jashkenas/underscore` |
| HEAD do Underscore | `5c1e5f686f8500af9c9d15614ed60289d6d35d6b` |
| jsFSTMerge | `https://github.com/AlbertoTrindade/jsFSTMerge` |
| HEAD do jsFSTMerge | `f85afb916754e3fc05636db6dfa2dd652c6508fe` |
| MiningFramework | `https://github.com/spgroup/miningframework` |
| Commit da ferramenta | `7a9503f0e3af110fb0028fb02753d4c4a627266e` |
| Módulo | `injectors.DynamicAnalysisJsModifiedLinesDetectionModule` |

## Execução oficial e repetição

O log `resultados/miningframework/framework-tmp-curto.log` registra `MINING FINISHED` e `BUILD SUCCESSFUL`. O arquivo `saida_oficial/data/results.csv` contém os seis registros originais.

A execução foi repetida pelo wrapper. Desconsiderando o alias do projeto e a ordem dos conjuntos, foram obtidos os mesmos pares e conjuntos de linhas por branch. Evidências: `resultados/miningframework/reproducibilidade.json` e a pasta `verificacao-cli`.

O código de mineração do framework não foi alterado. A cópia de execução recebeu duas adaptações de build: a API `application.mainClass` do Gradle 8.13 e o toolchain Java 21 instalado. O patch permanece no repositório.

Foi necessário usar um caminho sem `!` e uma pasta temporária curta para o Java. O ambiente foi provisionado em `C:\Users\Public\codex-merge-pilot`.

## Interpretação

O lote foi escolhido por conveniência para verificar a coleta. Não foi demonstrada equivalência com a amostra original do estudo. A seleção não exigiu alterações em linhas executáveis nem execução isolada dos arquivos.

A mineração identifica candidatos para investigação, sem confirmar defeitos. Veja `CRITERIOS_DE_MINERACAO.md` e `COMO_REPRODUZIR_MINERACAO.md`.

## Pacote para análise por outro pesquisador

Todos os seis pares do lote oficial foram exportados em `cenarios/piloto_oficial/`, agrupados pelos cinco SHAs de merge. São 24 versões de código: base, Left, Right e merge para cada par.

O pacote inclui 30 diffs dos arquivos selecionados, 15 patches de contexto do projeto completo, metadados com SHAs e checksums, índice CSV e verificador offline. O ZIP em `entrega/cenarios_merge_piloto.zip` contém o mesmo material, com critérios e licença do Underscore.

Essa exportação não é nova mineração e não contém snapshots completos dos projetos. Ela facilita a inspeção dos arquivos efetivamente coletados pela ferramenta oficial.
