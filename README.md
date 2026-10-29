# Replicação de detecção de conflitos semânticos em JavaScript

Trabalho de preparação de replicação e extensão do artigo **Semantic conflict detection via dynamic analysis**, Amanda Moraes, Paulo Borba e Léuson Da Silva, SBLP 2024. [Artigo / DOI](https://doi.org/10.5753/sblp.2024.3471).

Estado em 29/10/2026: fluxo experimental executado com MiningFramework e Jalangi2 oficiais, um mapeador de linhas e um analisador OA independente experimental. O pacote original da Amanda não foi recuperado; a equivalência com ele não foi demonstrada. A extensão com dataflow ainda não foi implementada.

## Resultados verificados

| Etapa | Resultado |
| --- | --- |
| Lote com MiningFramework oficial | 5 merges, 6 pares arquivo–merge JavaScript |
| Repetição do lote | Mesmos pares e conjuntos de linhas por branch |
| Controles sintéticos próprios | 44 controles aprovados |
| Aplicação do analisador independente | 4 execuções válidas sem alerta; 2 erros de contexto de testes |
| Coleta exploratória anterior, Git/Python | 509 merges no recorte, 184 pares candidatos em 146 merges; 181 quádruplas disponíveis |

Os 509 merges não foram minerados pelo MiningFramework nesta execução. Os 44 controles não são a suíte original de 69 casos. Zero alertas no piloto não comprova ausência de conflitos. Não há estimativa empírica de recall, acurácia ou superioridade sobre o artigo.

## Comece por aqui

- [Comparação pronta para apresentação, com dados e evidências](docs/COMPARACAO_ESTUDO_E_PILOTO.md)
- [Reimplementação OA: resultados e limites](RESULTADO_OA.md)
- [Ferramentas oficiais e adaptações do ambiente](FERRAMENTAS_OFICIAIS_EXECUTADAS.md)
- [Domínio e decisões do analisador](analisador_oa/README.md)
- [Plano de replicação](PLANO_DE_REPLICACAO.md)

## Código e dados

| Caminho | Conteúdo |
| --- | --- |
| `analisador_oa/` | Análise OA independente e verificação de fontes |
| `scripts/` | Mineração, mapeamento, execução, controles e geração dos resumos |
| `experimentos/miningframework/` | Lista de projetos e cinco merges do piloto oficial |
| `experimentos/oa_controles/` | Fontes dos controles sintéticos |
| `dados/apresentacao/` | CSVs e números verificados para os slides |
| `resultados/miningframework/saida_oficial/` | Saída preservada do coletor oficial |
| `resultados/oa_validacao/` | Resultados dos controles sintéticos |
| `resultados/oa_coleta/` | Mapas, fontes anotadas, configurações e eventos por amostra |
| `resultados/underscore_pre2015/` | Coleta exploratória Git/Python, separada do piloto oficial |
| `dados/mergedataset/` | Inventário complementar do catálogo público do grupo |

Os registros de execução preservam caminhos absolutos da máquina para auditoria. Para executar em outra máquina, regenere configurações e mapas com os scripts; os caminhos antigos não devem ser reutilizados como configuração local.

## Execução

Requisitos do protótipo: Python 3, Git, Node.js e Jalangi2. A execução verificada usou Node `v24.14.1` e Jalangi2 no commit `bc879287b1678de6e3c423f5debe63207559525b`.

```powershell
git clone https://github.com/Samsung/jalangi2.git ferramentas/jalangi2
git -C ferramentas/jalangi2 checkout --detach bc879287b1678de6e3c423f5debe63207559525b
```

Instale as dependências dentro de `ferramentas/jalangi2` com `npm.cmd install --omit=dev --ignore-scripts --no-audit --no-fund`. O lockfile da execução está preservado em `resultados/jalangi2/package-lock.executado.json`.

Da raiz:

```powershell
python scripts/testar_oa.py
python scripts/gerar_resumo_pesquisa.py
```

Para reaplicar a análise aos arquivos reais é necessário obter o histórico completo do Underscore em `repositorios/underscore`. Ver [instruções da coleta](COMO_REPRODUZIR_MINERACAO.md); depois execute `python scripts/aplicar_oa_coleta.py`.

O MiningFramework foi executado no commit `7a9503f0e3af110fb0028fb02753d4c4a627266e`. Seu ambiente foi provisionado fora do caminho com `!`, em `C:\Users\Public\codex-merge-pilot`. O wrapper `scripts/executar_miningframework.ps1` pressupõe esse ambiente já provisionado; não é um instalador portátil. O relatório das ferramentas e o patch de compatibilidade documentam a preparação necessária.

## Limites e próximos marcos

- Recuperar a suíte e o analisador originais ou uma referência independente para confrontar o protótipo.
- Revisar manualmente os mapas; o alinhamento textual do Git não é prova de autoria semântica.
- Melhorar a exercitação das duas contribuições, preservando separadamente execução direta e drivers/testes.
- Ampliar a coleta com o módulo oficial e avaliar a necessidade de novos modelos de linguagem.
- Definir com o orientador o desenho e a avaliação da extensão com dataflow.

Clones de ferramentas, caches e arquivos de instrumentação regeneráveis não fazem parte do versionamento. Fontes e avisos de terceiros estão descritos em [THIRD_PARTY.md](THIRD_PARTY.md).
