# Como reproduzir a mineração do piloto

Requisitos: Python 3, Git e, para o verificador de sintaxe JavaScript, Node.js. O coletor usa apenas a biblioteca padrão Python. Não instala nem executa dependências dos projetos minerados.

Execute a partir da raiz desta pasta de trabalho. Em Windows, use o executável Python disponível na sua máquina. Nesta execução foi utilizado o Python do runtime do Codex.

## Clones e referências

```powershell
git clone https://github.com/AlbertoTrindade/jsFSTMerge.git repositorios/jsFSTMerge
git clone https://github.com/jashkenas/underscore.git repositorios/underscore
git -C repositorios/jsFSTMerge checkout --detach f85afb916754e3fc05636db6dfa2dd652c6508fe
git -C repositorios/underscore checkout --detach 5c1e5f686f8500af9c9d15614ed60289d6d35d6b
```

As operações de checkout acima são para clones novos dedicados à reprodução. Não executá-las sobre um checkout com trabalho em andamento. Não usar histórico raso: o coletor verifica isso e recusa a coleta.

## Coleta

O coletor exige pasta de saída nova para preservar resultados anteriores. Os nomes abaixo são diferentes dos resultados já entregues.

```powershell
python scripts/minerar_merges.py --repo repositorios/jsFSTMerge --out resultados/repro_jsfstmerge --extensions .java .js --export-limit 5
python scripts/minerar_merges.py --repo repositorios/underscore --out resultados/repro_underscore_pre2015 --extensions .js --until 2014-12-31 --export-limit 5
```

O parâmetro `--until` compara a data de calendário registrada no timestamp do committer, inclusive. Não usa a data do autor. A coleta percorre apenas o histórico alcançável do HEAD congelado, não todas as branches ou PRs do servidor.

Saídas por coleta:

- `merges.csv`: cada merge no recorte e sua classificação na seleção;
- `arquivos_candidatos.csv`: cada par de caminho e merge candidato, incluindo versões ausentes;
- `resumo.json`: parâmetros, contagens, HEAD, versão Git e hash do coletor;
- `amostras/`: quádruplas e diffs das primeiras cinco amostras completas.

Os CSVs são UTF-8 com BOM. `semantic_label=unknown` e `dynamic_analysis=not_run` são estados explícitos, não rótulos negativos.

## Verificação

```powershell
python scripts/verificar_amostras.py --repo repositorios/jsFSTMerge --out resultados/repro_jsfstmerge
python scripts/verificar_amostras.py --repo repositorios/underscore --out resultados/repro_underscore_pre2015
```

O arquivo `verificacao.json` confirma pais, base e conteúdo das amostras exportadas. Para `.js`, também registra o resultado de `node --check` da versão integrada. O resultado de sintaxe pode depender da versão do Node; não é um teste de suporte do Jalangi2.

## Contagens esperadas com os commits congelados

jsFSTMerge: 13 merges, 6 merges candidatos, 11 pares arquivo–merge, todos `.java`, dos quais 10 com as quatro versões.

Underscore: 829 merges totais alcançáveis, 509 dentro do recorte, 146 merges candidatos e 184 pares arquivo–merge `.js`, dos quais 181 com as quatro versões.

Horário da execução e caminhos locais podem variar. Para comparar dados, usar os SHAs e os registros, não o timestamp.

## Inventário do MergeDataSet

O catálogo original foi obtido pelo conector GitHub e salvo em `dados/mergedataset/catalogo_original.csv`; o README de origem está em https://github.com/spgroup/mergedataset. O blob do CSV é `e617e0955c12c1563f0112c0bcd750aeeb86e089`. O catálogo normalizado apenas remove espaços no começo e fim de campos; não cria nem altera rótulos científicos.

O inventário não depende do download dos grandes arquivos JAR do MergeDataSet. Ele é complementar à mineração Git dos dois projetos.
