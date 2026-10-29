# Comparação para apresentação: artigo da Amanda e trabalho atual

Atualizado em 29/10/2026. Números do piloto lidos dos arquivos de resultados; números do artigo transcritos da leitura do PDF. Fonte bibliográfica: Moraes, Borba e Da Silva, SBLP 2024, [Semantic conflict detection via dynamic analysis](https://doi.org/10.5753/sblp.2024.3471).

## Mensagem central

Foi possível construir e executar um fluxo experimental sem o pacote original: MiningFramework oficial, arquivos históricos, mapas de linhas e Jalangi2 com um analisador OA independente. O resultado é um protótipo validado em controles próprios; a reprodução integral e a extensão com dataflow ainda não estão concluídas.

## Comparação de escopo e resultados

| Indicador | Artigo da Amanda | Trabalho atual | Como interpretar |
| --- | --- | --- | --- |
| Escopo | Estudo publicado em 2024 | Replicacao metodologica em preparacao; piloto experimental | Nao e uma reproducao integral concluida |
| Projetos na avaliacao empirica | 50 | 1: Underscore no lote oficial | Coleta exploratoria incluiu tambem jsFSTMerge; nao confundir escopos |
| Pares arquivo-merge avaliados/tentados | 452 | 6 | Amostras e criterios nao identicos |
| Execucoes bem-sucedidas | 159 | 4 | Original: 35,18%; piloto: 66,67%; nao indica superioridade |
| Erros de execucao | 293 | 2 | Piloto: arquivos de teste sem contexto, $ is not defined |
| Alertas OA observados | 1 | 0 | Zero alerta nao comprova ausencia de conflito |
| Validacao controlada | 69 casos avaliaveis, derivados de 71; 14 adaptados e 55 sem adaptacao conceitual | 44 controles sinteticos aprovados | Suites distintas: nao comparar como precisao ou acuracia |
| Analisador OA | Implementacao original da Amanda | Reimplementacao independente experimental v0.2 | Equivalencia com o original nao demonstrada |
| Ferramentas | MiningFramework e Jalangi2 | MiningFramework oficial e Jalangi2 oficial; analisador proprio | Versoes do piloto fixadas; versoes originais nao recuperadas |
| Mapas de origem | Mapas associados ao dataset original | 6 mapas conservadores gerados a partir do Git | Exigem revisao; nao sao os mapas originais |
| Desempenho | Experimento de overhead publicado | Benchmark comparavel ainda nao realizado | Tempos de verificacao locais nao equivalem ao benchmark |
| Extensao com dataflow | Fora do nucleo OA aqui reproduzido | Ainda nao implementada; desenho a alinhar com orientador | Propagacao do contexto de chamadas nao e uma analise geral de dataflow |

No artigo, a Figura 5 informa 452 amostras, 159 execuções bem-sucedidas e 293 erros. A indicação textual de 65% para os 159 casos é inconsistente; 159/452 corresponde a aproximadamente 35,18%. A comparação acima usa as contagens, não esse percentual textual.

## O que foi feito, com evidências

| Entrega | Estado | Arquivo de evidência, a partir da raiz do repositório |
| --- | --- | --- |
| Levantamento do método, resultados e limitações | Documentado | `PLANO_DE_REPLICACAO.md` |
| Mineração exploratória com Git/Python | Executada: 509 merges no recorte, 184 pares candidatos em 146 merges | `resultados/underscore_pre2015/resumo.json` |
| Verificação de quádruplas da coleta exploratória | 181 pares com quatro versões disponíveis; cinco exportados | `resultados/underscore_pre2015/arquivos_candidatos.csv` |
| Mineração com a ferramenta oficial | Executada: cinco merges, seis registros | `resultados/miningframework/saida_oficial/data/results.csv` |
| Repetição do lote oficial | Mesmos seis pares e mesmos conjuntos de linhas por branch | `resultados/miningframework/reproducibilidade.json` |
| Jalangi2 oficial | Instalado e executado em controles e arquivos reais | `resultados/jalangi2/resumo.json` |
| Mapas de linhas da versão integrada | Seis mapas gerados; autoria textual conservadora, revisão pendente | `resultados/oa_coleta/*/line_to_branch_map.json` |
| Analisador OA independente | Protótipo v0.2 executado | `analisador_oa/analysis.js` |
| Validação própria | 44 controles aprovados | `resultados/oa_validacao/resumo.json` |
| Aplicação OA ao lote oficial | Quatro sucessos sem alerta e dois erros | `resultados/oa_coleta/resultados.csv` |
| Recuperação e validação com o pacote original | Pendente | `analisador_oa/README.md` descreve o limite |
| Ampliação com MiningFramework além do piloto | Pendente | Os 509 merges pertencem à coleta Git/Python anterior |
| Extensão com dataflow | Pendente, desenho a alinhar | Não há implementação dessa extensão neste repositório |

## Composição dos 44 controles

- positivos: 16.
- negativos: 17.
- avisos de limites: 5.
- rejeicoes de fontes: 3.
- outros controles de mapeamento integridade: 3.

Esses grupos incluem verificações de rejeição e de análise parcial. “44 aprovados” significa que os resultados esperados desses controles foram satisfeitos, não 100% de precisão do detector em software real. Os controles não substituem a suíte original de 69 casos.

## Resultado empírico do piloto

| Merge | Arquivo | Resultado | Alertas | Linhas com eventos L / R |
| --- | --- | --- | ---: | ---: |
| `a2aab7c69968` | `test/utility.js` | Erro de execução | — | 0 / 0 |
| `a2aab7c69968` | `underscore.js` | Sucesso | 0 | 1 / 24 |
| `b5f111e8d4b3` | `test/utility.js` | Erro de execução | — | 0 / 0 |
| `8c15ae153aae` | `underscore.js` | Sucesso | 0 | 0 / 0 |
| `e863fbf285f7` | `underscore.js` | Sucesso | 0 | 0 / 10 |
| `2b9a011e070b` | `underscore.js` | Sucesso | 0 | 0 / 0 |

As linhas com eventos refletem escritas e invocações rastreadas; não representam cobertura completa de linhas ou caminhos. Somente uma das quatro execuções válidas registrou eventos de ambas as origens. As duas falhas dependem de contexto de testes ausente (`$ is not defined`).

## Sugestão de três slides

1. **Aprofundamento e implementação:** método compreendido; MiningFramework e Jalangi2 oficiais executados; mapeamento e núcleo OA independentes implementados. Mostrar o fluxo e a distinção em relação ao pacote original.
2. **Dados obtidos:** cinco merges oficiais → seis arquivos → quatro sucessos e dois erros; 44 controles próprios aprovados. Mostrar o caso positivo sintético como demonstração de funcionamento, identificado como sintético.
3. **Limites e próximos passos:** sem equivalência demonstrada; baixa exercitação das duas contribuições; revisão dos mapas e validação independente; ampliar coleta oficial; definir extensão com dataflow.

## Texto para apresentar ao professor

“Aprofundei o estudo do algoritmo e avancei do entendimento para um fluxo executável. Configurei as ferramentas oficiais, executei uma mineração piloto de cinco merges e obtive seis arquivos candidatos. Preparei os mapas na versão integrada e implementei um núcleo OA independente, com 44 controles próprios aprovados. No piloto, quatro arquivos executaram sem alertas e dois falharam por falta de contexto de testes. Ainda não considero isso uma reprodução integral: preciso confrontar a implementação com o pacote original e melhorar a exercitação das contribuições antes de avaliar a extensão com dataflow.”

As planilhas CSV para montar os slides estão em `dados/apresentacao/`. Esse material não afirma descoberta de um conflito real nem novidade científica já estabelecida.
