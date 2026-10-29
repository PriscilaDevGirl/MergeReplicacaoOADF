# Arquivos do piloto oficial para análise

Este pacote contém 5 cenários de merge do Underscore, 6 pares arquivo–merge e 24 versões de código. Ele deriva da saída preservada do MiningFramework oficial.

## Comece aqui

1. Abra `indice.csv` para localizar um arquivo e seu merge.
2. Entre na pasta identificada pelo SHA completo do merge.
3. Compare `base/` com `left/` para entender a primeira contribuição.
4. Compare `base/` com `right/` para entender a segunda contribuição.
5. Leia `merge/` e as comparações com os pais para analisar o resultado original.

Há 30 diffs dos arquivos selecionados e 15 patches de contexto do projeto. Os patches usam o formato padrão Git: linhas com `-` saem da versão anterior e linhas com `+` entram na seguinte. Os cabeçalhos `@@` informam as posições nas duas versões.

## Estrutura de cada cenário

```text
SHA_DO_MERGE/
  base/caminho/original.js
  left/caminho/original.js
  right/caminho/original.js
  merge/caminho/original.js
  diffs/base_left/caminho/original.js.diff
  diffs/base_right/caminho/original.js.diff
  diffs/base_merge/caminho/original.js.diff
  diffs/left_merge/caminho/original.js.diff
  diffs/right_merge/caminho/original.js.diff
  mudancas_projeto/base_left.patch
  mudancas_projeto/base_right.patch
  mudancas_projeto/base_merge.patch
  metadata.json
  README.md
```

O cenário `a2aab7c6996835d453972b22999b80dbfe125db5` contém dois arquivos selecionados. Os demais contêm um cada. Os caminhos distintos são `underscore.js` e `test/utility.js`.

## Conferir integridade sem clonar o projeto original

Com Python 3, execute dentro desta pasta:

```text
python verificar_pacote.py
```

O verificador confere os checksums e a presença das 24 versões. Não instala dependências nem executa o JavaScript. O arquivo `MANIFESTO.json` registra as contagens e os checksums. `metadata.json` de cada cenário registra os SHAs e as comparações.

## Escopo

Base é o ancestral comum único. Left é o primeiro pai e Right o segundo. As contribuições são diferenças acumuladas da base até cada pai, podendo envolver vários commits.

As pastas de código preservam somente os arquivos selecionados. Os patches de projeto ampliam o contexto, mas não substituem o checkout completo para executar testes. Para recuperar todo o projeto, use os SHAs completos registrados e o repositório https://github.com/jashkenas/underscore.

Os cenários foram selecionados por conveniência para validar a coleta. Sua inclusão não confirma defeito. Os critérios detalhados estão em `CRITERIOS_DE_MINERACAO.md` na raiz do repositório de entrega.

Fontes históricas do Underscore sob licença MIT, preservada em `LICENSE_UNDERSCORE.txt`.
