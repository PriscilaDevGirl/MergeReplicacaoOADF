# Como reproduzir a mineração

## 1. Históricos completos

Na raiz do projeto, com Git e Python 3 disponíveis:

```powershell
git clone https://github.com/jashkenas/underscore.git repositorios/underscore
git -C repositorios/underscore checkout --detach 5c1e5f686f8500af9c9d15614ed60289d6d35d6b
```

Para repetir a exploração auxiliar:

```powershell
git clone https://github.com/AlbertoTrindade/jsFSTMerge.git repositorios/jsFSTMerge
git -C repositorios/jsFSTMerge checkout --detach f85afb916754e3fc05636db6dfa2dd652c6508fe
```

Os checkouts são para clones dedicados, sem trabalho em andamento. Não use histórico raso.

## 2. Exploração Git/Python

O coletor usa a biblioteca padrão Python. Escolha pastas de saída novas:

```powershell
python scripts/minerar_merges.py --repo repositorios/underscore --out resultados/repro_underscore_pre2015 --extensions .js --until 2014-12-31 --export-limit 5
python scripts/minerar_merges.py --repo repositorios/jsFSTMerge --out resultados/repro_jsfstmerge --extensions .java .js --export-limit 5
```

Saídas: `merges.csv`, `arquivos_candidatos.csv`, `resumo.json` e quádruplas/diffs em `amostras/`.

Contagens do Underscore: 509 merges no recorte, 184 pares candidatos em 146 merges e 181 pares com quatro versões. A data usa o calendário do timestamp do committer, inclusive.

## 3. MiningFramework oficial

Repositório: https://github.com/spgroup/miningframework

Commit: `7a9503f0e3af110fb0028fb02753d4c4a627266e`.

Módulo: `injectors.DynamicAnalysisJsModifiedLinesDetectionModule`.

Entradas: `experimentos/miningframework/projects.csv` e `commits_piloto.csv`.

Configuração executada a partir da cópia do framework:

```text
gradle run --args="--injector injectors.DynamicAnalysisJsModifiedLinesDetectionModule --extension .js --keep-projects --max-commits-per-project 5 --random-seed 1 --project-commit-hashes-file pilot-input/commits_piloto.csv pilot-input/projects.csv output-pilot"
```

O comando pressupõe entradas em `pilot-input`, saída nova e ferramenta já provisionada. O `random-seed` controla a ordem de processamento da lista fornecida.

### Ambiente validado nesta máquina

- Framework: `C:\Users\Public\codex-merge-pilot\miningframework`.
- Gradle 8.13: `C:\Users\Public\codex-merge-pilot\gradle-runtime`.
- Eclipse Adoptium Java 21.0.8.9 e Groovy 3.0.23.
- Pasta temporária curta: `C:\Users\Public\codex-merge-pilot\tmp`.
- Diff textual: `C:\Program Files\Git\usr\bin\diff.exe`, incluído no PATH da execução.

A cópia de execução recebeu `resultados/miningframework/compatibilidade-build.patch`. Para provisionar outra máquina, obtenha o commit da ferramenta, instale o Gradle e um JDK apropriado e confira se essas adaptações são necessárias. Essa configuração não foi demonstrada equivalente à configuração histórica do artigo.

Nesta máquina, o wrapper cria entradas e saídas novas e um alias novo para o clone:

```powershell
.\scripts\executar_miningframework.ps1
```

O wrapper não é um instalador portátil. Em outra máquina, ajuste o runtime, o JDK e o Diff conforme a instalação. O resultado esperado para a lista preservada é de cinco merges e seis registros.

## 4. Auditoria dos critérios

Depois de obter o clone completo do Underscore:

```powershell
python scripts/auditar_criterios_mineracao.py
```

O auditor confere pais, ancestral único, data, presença das quatro versões, status de modificação nos dois pais e correspondência com as entradas. Gera `criterios_verificados.csv` e `resumo_mineracao.json` em `resultados/miningframework`.

## 5. Integridade das amostras

```powershell
python scripts/verificar_amostras.py --repo repositorios/underscore --out resultados/underscore_pre2015
```

O verificador compara as quatro versões exportadas com o histórico Git e confere os checksums. Para `.js`, também usa `node --check`, exigindo Node.js. A checagem de sintaxe não executa o programa nem compõe um critério de inclusão.

## 6. Analisar os cenários sem repetir a coleta

Abra `cenarios/piloto_oficial/README.md` ou extraia `entrega/cenarios_merge_piloto.zip`. Cada pasta de merge contém `base/`, `left/`, `right/`, `merge/`, cinco comparações por arquivo e patches de contexto do projeto.

Left é o primeiro pai do merge e Right o segundo. A base é seu ancestral comum único. A pasta `merge/` contém o resultado original do histórico, sem reconstrução ou simulação.

Para conferir todos os arquivos do pacote:

```powershell
python cenarios/piloto_oficial/verificar_pacote.py
```

Para comparar um dos arquivos selecionados no VS Code, a partir da raiz deste repositório:

```powershell
code --diff cenarios/piloto_oficial/a2aab7c6996835d453972b22999b80dbfe125db5/base/underscore.js cenarios/piloto_oficial/a2aab7c6996835d453972b22999b80dbfe125db5/left/underscore.js
code --diff cenarios/piloto_oficial/a2aab7c6996835d453972b22999b80dbfe125db5/base/underscore.js cenarios/piloto_oficial/a2aab7c6996835d453972b22999b80dbfe125db5/right/underscore.js
```

Você também pode abrir os `.diff` em qualquer editor. `base_left` mostra a contribuição Left em relação à base; `base_right` mostra a contribuição Right. `base_merge`, `left_merge` e `right_merge` ajudam a examinar a integração.

Para gerar outra exportação a partir do clone original, use destinos novos:

```powershell
python scripts/exportar_cenarios_piloto.py --out cenarios/nova_exportacao --zip entrega/nova_exportacao.zip
```

A exportação exige Git e o histórico local do Underscore; a leitura e a verificação do pacote entregue não exigem o projeto original. Ela mantém os seis registros do lote oficial, sem adicionar novos cenários.
