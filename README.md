# Mineração de cenários de merge em JavaScript

Este repositório reúne **a mineração de repositórios, os critérios de seleção e os resultados da coleta**. O objetivo atual é preparar cenários rastreáveis para pesquisa de integração de software.

## Resultados da mineração

| Etapa | Projeto | Resultado |
| --- | --- | --- |
| Piloto com MiningFramework oficial | Underscore | 5 merges selecionados, 6 pares arquivo–merge |
| Repetição do piloto oficial | Underscore | Mesmos pares e conjuntos de linhas por branch |
| Exploração anterior com Git/Python | Underscore | 509 merges no recorte, 184 pares candidatos em 146 merges |
| Quatro versões disponíveis na exploração | Underscore | 181 pares com base, Left, Right e merge |
| Exploração auxiliar | jsFSTMerge | 13 merges examinados, 11 pares candidatos Java em 6 merges |

**Os 509 merges pertencem à exploração Git/Python. O MiningFramework oficial processou o lote de cinco merges.** Seus seis registros correspondem a versões de dois caminhos: `underscore.js` e `test/utility.js`.

O lote é uma seleção por conveniência para verificar a coleta. Não é uma amostra aleatória ou representativa e não foi selecionado pela presença conhecida de defeitos.

## Arquivos prontos para análise por outro pesquisador

- **[Pacote de cenários](cenarios/piloto_oficial/README.md):** cinco merges do piloto oficial, com base, Left, Right e merge dos seis arquivos selecionados.
- **[Download do pacote ZIP](entrega/cenarios_merge_piloto.zip):** inclui 24 versões de código, 30 diffs por arquivo e 15 patches de contexto do projeto, além de critérios e metadados.
- **[Índice dos arquivos e SHAs](cenarios/piloto_oficial/indice.csv):** localiza cada par arquivo–merge.

Seu colega pode clonar este repositório ou extrair o ZIP e começar a comparar os arquivos. Não precisa instalar o MiningFramework para essa análise manual. Na pasta do pacote, `python verificar_pacote.py` confere sua integridade sem Git ou dependências externas.

As quatro pastas de cada cenário contêm somente os arquivos selecionados. Os patches do projeto completo fornecem contexto adicional. Para executar todo o projeto histórico, é necessário recuperar seu checkout e as dependências apropriadas.

## Critérios e evidências

- [Critérios de mineração](CRITERIOS_DE_MINERACAO.md): escolha dos projetos, recorte temporal, filtros e seleção do lote.
- [Relatório do piloto](RELATORIO_PILOTO_MINERACAO.md): resultados e rastreabilidade.
- [Como reproduzir](COMO_REPRODUZIR_MINERACAO.md): ambiente e comandos.

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `scripts/minerar_merges.py` | Coletor exploratório Git/Python |
| `scripts/executar_miningframework.ps1` | Wrapper do módulo oficial no ambiente provisionado |
| `scripts/auditar_criterios_mineracao.py` | Conferência dos critérios nos seis registros oficiais |
| `scripts/verificar_amostras.py` | Integridade das quádruplas e checagem de sintaxe de JavaScript |
| `scripts/exportar_cenarios_piloto.py` | Exportação dos seis registros oficiais como código, diffs, metadados e ZIP |
| `scripts/verificar_pacote_mineracao.py` | Verificação offline do pacote entregue |
| `experimentos/miningframework/` | Projeto e SHAs fornecidos ao framework |
| `resultados/miningframework/` | Saídas oficiais, logs, repetição e auditoria |
| `resultados/underscore_pre2015/` | Tabelas e amostras da exploração anterior |
| `resultados/jsfstmerge/` | Tabelas da exploração auxiliar Java |
| `cenarios/piloto_oficial/` | Quatro versões e mudanças de todos os registros do piloto oficial |
| `entrega/cenarios_merge_piloto.zip` | Pacote portátil para outro pesquisador |

## Reprodução rápida

Com o histórico completo do Underscore em `repositorios/underscore`, confira o lote preservado:

```powershell
python scripts/auditar_criterios_mineracao.py
```

Para repetir a mineração oficial no ambiente já provisionado nesta máquina:

```powershell
.\scripts\executar_miningframework.ps1
```

O wrapper pressupõe a instalação da ferramenta e do Gradle em `C:\Users\Public\codex-merge-pilot`. Ele não é um instalador portátil. Veja as instruções detalhadas para o ambiente e as adaptações de build.

## Ferramenta e estudo de referência

- [MiningFramework do grupo](https://github.com/spgroup/miningframework), commit `7a9503f0e3af110fb0028fb02753d4c4a627266e`.
- Módulo: `injectors.DynamicAnalysisJsModifiedLinesDetectionModule`.
- Moraes, Borba e Da Silva, *Semantic conflict detection via dynamic analysis*, SBLP 2024. [DOI](https://doi.org/10.5753/sblp.2024.3471).

A coleta atual não reproduz integralmente a amostra do artigo. Ela documenta os passos executados e as decisões do piloto. Fontes e licenças estão em [THIRD_PARTY.md](THIRD_PARTY.md).
