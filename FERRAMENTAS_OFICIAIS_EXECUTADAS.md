# MiningFramework e Jalangi2 executados

Data: 29/10/2026. As duas ferramentas foram instaladas e executadas nesta máquina. O MiningFramework coletou seis registros JavaScript de cinco merges; os seis arquivos integrados foram submetidos ao Jalangi2.

## 1. Mineração com a ferramenta do grupo

Repositório: https://github.com/spgroup/miningframework

Commit: `7a9503f0e3af110fb0028fb02753d4c4a627266e`.

Configuração original utilizada:

`injectors.DynamicAnalysisJsModifiedLinesDetectionModule`

Esse módulo executa o filtro de arquivos modificados por ambos os pais, o coletor `ModifiedFilesLinesPerFileCollector` e o coletor de estatísticas. O conjunto de entrada contém cinco merges do Underscore, com os SHAs dos dois pais fornecidos à opção suportada `--project-commit-hashes-file`.

O lote foi escolhido entre as amostras do piloto anterior para validar a ferramenta; não é uma amostra aleatória ou uma nova execução de todo o dataset.

Resultado observado no log: **`#### MINING FINISHED ####` e `BUILD SUCCESSFUL in 1m 11s`**.

| Merge | Arquivos coletados |
| --- | --- |
| `a2aab7c6996835d453972b22999b80dbfe125db5` | `test/utility.js`, `underscore.js` |
| `b5f111e8d4b3bbe9ece4ebac39f91d10ea11b7db` | `test/utility.js` |
| `8c15ae153aae4eb4537121fae9fc3a3bef84ded7` | `underscore.js` |
| `e863fbf285f75063a982332d55926e5cc85f1626` | `underscore.js` |
| `2b9a011e070b01cf1e6957333fcb425a638c0465` | `underscore.js` |

Os seis registros estão em `resultados/miningframework/saida_oficial/data/results.csv`. O CSV original do coletor inclui adições, remoções e alterações associadas a cada pai. Os números de linha precisam ser mapeados e revisados na versão integrada antes de servir como entrada de um detector OA; não foram automaticamente reinterpretados como linhas do merge.

O conjunto possui cinco merges e seis pares arquivo–merge, não seis conflitos.

## 2. Ajustes necessários no ambiente

A ferramenta executou em `C:\Users\Public\codex-merge-pilot\miningframework` para evitar a falha de carregamento de JAR causada pelo caractere `!` em `Convidado!`.

A pasta temporária do Java também foi definida como `C:\Users\Public\codex-merge-pilot\tmp`, pois o caminho temporário longo deste ambiente causou `Invalid argument: connect` durante a criação dos sockets locais usados pelo Gradle. A execução funcionou com o caminho curto.

Foram necessárias duas alterações em `build.gradle` da cópia de execução:

1. Usar a API `application { mainClass = ... }` compatível com o Gradle 8.13 configurado pelo repositório.
2. Usar o Java 21 disponível na máquina em vez de exigir um toolchain Java 17 ausente.

O código de mineração não foi alterado. O diff está em `resultados/miningframework/compatibilidade-build.patch`. A cópia original do repositório em `ferramentas/miningframework` foi preservada.

Ambiente observado: Gradle 8.13, Groovy 3.0.23 e Eclipse Adoptium Java 21.0.8.9. Isso não estabelece equivalência com as versões utilizadas no artigo em 2024.

## 3. Jalangi2 oficial

Repositório: https://github.com/Samsung/jalangi2

Commit: `bc879287b1678de6e3c423f5debe63207559525b`; versão declarada no pacote: `0.2.6`. Node.js: `v24.14.1`.

As dependências foram instaladas com:

```powershell
npm.cmd install --omit=dev --ignore-scripts --no-audit --no-fund
```

O lockfile resultante foi preservado em `resultados/jalangi2/package-lock.executado.json`. A execução confirmou compatibilidade para os casos deste piloto, não para toda a suíte ou toda a linguagem JavaScript.

Análise utilizada, fornecida pelo próprio Jalangi2:

`src/js/sample_analyses/tutorial/BranchCoverage.js`

Comando base:

```powershell
node ferramentas/jalangi2/src/js/commands/jalangi.js --inlineIID --inlineSource --analysis ferramentas/jalangi2/src/js/sample_analyses/tutorial/BranchCoverage.js caminho/do/arquivo.js
```

## 4. Integração entre a mineração oficial e Jalangi2

O script `scripts/integrar_miningframework_jalangi2.py` lê o CSV real do MiningFramework, recupera cada arquivo no commit integrado e executa tanto a versão normal quanto a versão instrumentada. Python apenas organiza essas execuções; a mineração foi feita pelo MiningFramework e a instrumentação/análise pelo Jalangi2.

| Resultado | Node normal | Jalangi2 |
| --- | ---: | ---: |
| Arquivos tentados | 6 | 6 |
| Execuções com código de saída zero | 4 | 4 |
| Erros de execução | 2 | 2 |

As duas falhas são arquivos `test/utility.js` que dependem de contexto de testes/browser não fornecido pela execução isolada; o erro observado é `ReferenceError: $ is not defined`. O piloto não instalou um ambiente de browser nem todas as dependências históricas do projeto. Essas falhas estão registradas como erros, nunca como ausência de conflito.

Detalhes em `resultados/integracao_oficial/execucoes.csv` e `resumo.json`, com stdout e stderr por arquivo e modo.

## 5. Verificação adicional de exercitação

Foi executado um exemplo de controle que produz `EXEMPLO_OK LRLRLRLRLR`; a análise oficial registrou o laço e os dois resultados da condição de paridade.

Também foi executado um driver explícito sobre o `underscore.js` do merge `8c15ae153aae4eb4537121fae9fc3a3bef84ded7`, verificando `map([1,2,3]) -> [2,4,6]` e iteração sobre um objeto. O driver passou com Node normal e com Jalangi2, produzindo `UNDERSCORE_DRIVER_OK [2,4,6]`.

Na execução direta, a análise relatou condições em dois intervalos distintos do arquivo; com o driver, em sete intervalos distintos. Foram oito entradas brutas no segundo caso, pois dois IIDs distintos correspondem ao mesmo intervalo de código. Isso é evidência limitada de exercitação adicional, não percentual de cobertura nem resultado de detecção de conflitos.

O driver é uma entrada adicional escrita para a validação e deve permanecer separado da execução direta usada como referência.

## 6. Como repetir nesta máquina

Da pasta raiz do projeto, para repetir o MiningFramework no ambiente já provisionado:

```powershell
.\scripts\executar_miningframework.ps1
```

O script cria um nome de execução novo e um alias novo para o clone, preservando saídas e clones anteriores. A ferramenta é executada na pasta sem `!`; o resultado é copiado de volta para uma subpasta de `resultados/miningframework`.

Para repetir a validação do Jalangi2:

```powershell
python scripts/executar_jalangi2.py
```

Para repetir a integração usando o CSV do primeiro lote oficial preservado:

```powershell
python scripts/integrar_miningframework_jalangi2.py
```

Esses dois scripts regravam os logs derivados de suas respectivas validações, mantendo o CSV original e as amostras de origem. O Python utilizado nesta execução está em `C:\Users\Convidado!\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

## 7. Limite atual e próximo passo

O MiningFramework e o Jalangi2 estão operacionais. Foi executada a análise oficial de cobertura do Jalangi2, **não o analisador de overriding assignments da Amanda**, que não foi recuperado. Nenhum conflito OA foi confirmado por este piloto.

Atualização posterior: o mapeamento e uma reimplementação independente experimental foram implementados e executados. Ver `RESULTADO_OA.md` para 44 controles e a aplicação aos seis arquivos. A ferramenta original da Amanda continua indisponível; a equivalência com ela não foi demonstrada. Para ampliar a coleta, o módulo oficial já está funcional; o lote de cinco merges permanece uma validação inicial do fluxo.
