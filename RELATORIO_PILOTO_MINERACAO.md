# Resultado do piloto de mineração de merges

Atualização: o bloqueio do MiningFramework foi posteriormente resolvido e houve execução com o módulo oficial e com Jalangi2. Ver `FERRAMENTAS_OFICIAIS_EXECUTADAS.md`. As contagens abaixo continuam descrevendo o primeiro piloto Git/Python, preservado como registro separado.

Data: 29/10/2026. Contexto: preparação da replicação e extensão do estudo de Amanda Moraes, Paulo Borba e Léuson Da Silva (SBLP 2024).

## Resultado principal

Foi executada uma mineração real e local do histórico Git de dois projetos. A coleta produziu tabelas com SHAs de merge, pais, ancestral comum e arquivos modificados pelas duas contribuições. Dez amostras foram exportadas com quatro versões e cinco diffs por amostra.

| Medida | jsFSTMerge | Underscore |
| --- | ---: | ---: |
| Merges alcançáveis do HEAD congelado | 13 | 829 |
| Merges dentro do recorte | 13 | 509 |
| Merges com um pai ancestral do outro, excluídos | 5 | 260 |
| Merges sem ancestral comum único, excluídos | 0 | 1 |
| Merges sem arquivo comum das extensões selecionadas | 2 | 102 |
| Merges com arquivos candidatos | 6 | 146 |
| Pares arquivo–merge candidatos | 11 | 184 |
| Candidatos com as quatro versões presentes | 10 | 181 |
| Amostras exportadas | 5 | 5 |

jsFSTMerge: coleta sem filtro de data, extensões `.java` e `.js`. Os 11 candidatos encontrados são Java; nenhum candidato JavaScript foi encontrado nesse histórico com os critérios adotados.

Underscore: extensão `.js`, data de committer até 31/12/2014, inclusive. Dos 829 merges, 320 ficaram fora do recorte. Esse corte conservador é uma decisão do piloto, não uma reprodução afirmada do limite temporal exato da Amanda.

Um candidato é um **par arquivo–merge**, não um conflito confirmado. Arquivos diferentes do mesmo merge não são observações necessariamente independentes.

## Relação dos projetos com a pesquisa

O jsFSTMerge é uma ferramenta de merge semiestruturado de JavaScript desenvolvida na UFPE. Seu README atribui o desenvolvimento a Alberto Trindade Tavares e informa que ela se baseia no jFSTMerge de Guilherme Cavalcanti. O histórico foi minerado como projeto associado ao tema e ao grupo, sem atribuir sua autoria individual a Paulo Borba.

Como a implementação do jsFSTMerge é majoritariamente Java e não forneceu candidatos `.js`, foi feita uma segunda coleta no Underscore para obter material JavaScript para a próxima etapa. Underscore não é um repositório do Paulo. Ainda não foi verificado se ele integra a lista original dos 50 projetos; esta é uma nova coleta, cuja independência em relação à amostra original não está estabelecida.

## Método executado

1. Clonar os históricos completos, sem `--depth`.
2. Congelar o HEAD de referência de cada coleta e enumerar todos os merges alcançáveis dele.
3. Aplicar o recorte de data quando definido, usando a data local de calendário armazenada no timestamp do committer.
4. Manter somente merges de dois pais e com um único ancestral comum retornado por `git merge-base --all`.
5. Excluir casos em que o ancestral coincide com um dos pais.
6. Comparar base→Left e base→Right, sem detecção de renomeação, e intersectar os caminhos alterados.
7. Selecionar as extensões previstas e conferir se o caminho existe em base, Left, Right e merge.
8. Exportar as cinco primeiras amostras disponíveis na ordem topológica reversa usada pelo comando. Trata-se de seleção por conveniência para inspeção, não amostragem representativa.

As tabelas mantêm candidatos com versões ausentes sinalizados; esses registros não foram exportados como quádruplas completas. O uso de caminhos exatos e a desativação da detecção de renomeação são simplificações a revisar antes de uma coleta definitiva.

## Ferramentas e rastreabilidade

| Item | Referência congelada |
| --- | --- |
| MiningFramework inspecionado | `spgroup/miningframework`, commit `7a9503f0e3af110fb0028fb02753d4c4a627266e` |
| jsFSTMerge | `AlbertoTrindade/jsFSTMerge`, HEAD `f85afb916754e3fc05636db6dfa2dd652c6508fe` |
| Underscore | `jashkenas/underscore`, HEAD `5c1e5f686f8500af9c9d15614ed60289d6d35d6b` |
| Coletor executado | `scripts/minerar_merges.py`, Python com biblioteca padrão e Git |
| Git | `2.55.0.windows.5` |

O MiningFramework foi baixado e seu módulo `DynamicAnalysisJsModifiedLinesDetectionModule` foi identificado. Ele combina `MutuallyModifiedFilesCommitFilter`, `ModifiedFilesLinesPerFileCollector` e `StatisticsCollector`. A execução do framework não chegou a iniciar a mineração: o Gradle apresentou falha ao carregar recursos de JAR em caminho contendo `Convidado!`, com `NoSuchFileException` para `C:\Users\Convidado`. Uma tentativa com caminho curto também falhou no daemon.

**A coleta apresentada foi executada pelo script Git/Python, e não pelo MiningFramework.** O script realiza a seleção básica de arquivos modificados nas duas contribuições e acrescenta verificações de pais e ancestral. Não foi demonstrada equivalência integral entre sua saída e a do framework, nem com o coletor usado no artigo.

O endereço do Nightmare consultado não pôde ser clonado: o servidor retornou `Repository not found`. Isso motivou a escolha dos projetos acima.

## Material exportado e validação

Cada pasta de amostra contém:

- `base`, `left`, `right` e `merge`, na extensão do arquivo original;
- diffs base→Left, base→Right, base→merge, Left→merge e Right→merge;
- `metadata.json` com SHAs completos, caminho original e checksums SHA-256 das quatro versões.

O verificador conferiu as 10 amostras exportadas e suas 40 versões: ordem dos pais, ancestral comum único, igualdade byte a byte com `git show` e checksums. As cinco versões integradas JavaScript passaram em `node --check`. Esses testes não demonstram compatibilidade com Jalangi2 ou ausência/presença de conflitos semânticos.

Exemplo concreto no Underscore:

- Merge: `2b9a011e070b01cf1e6957333fcb425a638c0465`.
- Left: `f997a17c8965c9cfa9a19e932666348695712332`.
- Right: `df2742de1767c0ded3cf37dd88d094c7d59bc882`.
- Base: `4a83fcdd260f61f253f3349740ee304074867aff`.
- Arquivo: `underscore.js`.

A inspeção do diff base→Left dessa primeira amostra mostrou alteração apenas em comentário. Isso ilustra por que o filtro por arquivo comum é somente uma pré-seleção: ainda será necessário verificar linhas executáveis, preservar sua origem na versão integrada e exercitar as contribuições.

## Inventário complementar do repositório do grupo

Também foi obtido e normalizado o catálogo `semantic-conflicts/sample-semantic-conflicts.csv` de `spgroup/mergedataset`, blob `e617e0955c12c1563f0112c0bcd750aeeb86e089`.

- 95 registros;
- 72 pares distintos projeto–commit;
- 41 URLs de projetos distintas;
- campo `Locally Observable Interference`: 17 `Yes`, 74 `No` e 4 `-`.

Esses valores são um inventário dos rótulos publicados, não resultados de uma nova detecção. `Locally Observable Interference` não deve ser reinterpretado automaticamente como rótulo geral de conflito semântico ou de OA. O catálogo é voltado a classes/artefatos Java, portanto não substitui diretamente o dataset JavaScript do artigo.

## O que já pode ser apresentado na reunião

“Implementei e executei um piloto de mineração. No projeto de merge jsFSTMerge, encontrei 11 pares de arquivo e merge candidatos, todos Java. Para avançar no tema JavaScript, coletei o histórico do Underscore até o fim de 2014: 184 pares candidatos em 146 merges, com 181 quádruplas disponíveis. Exportei cinco amostras de cada projeto e conferi sua integridade. Ainda falta produzir o mapa de linhas para branches e executar o detector OA. A tentativa com o MiningFramework encontrou uma limitação do ambiente; o piloto usa Git/Python, e preciso alinhar essa adaptação metodológica.”

## Próximo marco

Selecionar uma amostra JavaScript com mudanças executáveis das duas contribuições, gerar e revisar seu mapa de origem nas linhas do merge e executar uma análise Jalangi2. Em paralelo, recuperar a implementação OA original ou alinhar uma reimplementação independente. Nenhum alerta OA ou conflito semântico novo foi confirmado neste piloto.

Os resultados em CSV e JSON, amostras e scripts estão nesta pasta de trabalho. Instruções em `COMO_REPRODUZIR_MINERACAO.md`.
