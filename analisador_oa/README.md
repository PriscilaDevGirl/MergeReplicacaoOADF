# Analisador OA independente para Jalangi2

Versão experimental: `independent-oa-v0.2`. Esta é uma reimplementação do núcleo do algoritmo descrito no artigo, desenvolvida nesta pasta. Não é o código original da Amanda e não foi demonstrada equivalência com ele.

## Componentes

- `analysis.js`: callbacks do Jalangi2, identidade dos alvos, associação a branches e emissão de candidatos OA.
- `preflight.js`: verificação de sintaxe ES5 e rejeição de `with` e de getters/setters definidos no código de entrada. Referências estáticas a APIs dinâmicas são avisos; sua presença em código não executado não prova uso em runtime.
- `../scripts/mapear_origens_oa.py`: mapeamento de linhas preservadas entre base, pais e merge.
- `../scripts/executar_oa.py`: runner com configuração por processo, verificação de checksum e preservação de erros.
- `../scripts/testar_oa.py`: controles sintéticos positivos, negativos, limitações declaradas e DAGs Git controlados.
- `../scripts/aplicar_oa_coleta.py`: aplicação à saída preservada do MiningFramework oficial.

## Regras implementadas

Cada variável é identificada pelo nome e pelo ambiente léxico/ativação de função. Cada propriedade é identificada pela identidade do objeto e sua chave; aliases apontando ao mesmo objeto compartilham o alvo. Índices de array são propriedades distintas. A identidade da variável que referencia um objeto é separada da identidade de seus campos.

Uma escrita atribuída a L seguida por uma escrita atribuída a R no mesmo alvo, ou na ordem inversa, gera um evento. Uma escrita fora das contribuições e fora de contexto herdado descarta o registro anterior desse alvo. Escritas com o mesmo valor também são escritas.

Chamadas síncronas herdam o contexto da contribuição que as provocou. Quando a própria instrução de escrita está explicitamente mapeada para L ou R, essa origem direta tem precedência. Essa escolha de precedência deve ser confrontada com a implementação original quando disponível.

O rastreamento usa `write`, `putField` após a atribuição efetiva, declaração e entrada/saída de funções/scripts, literais de função e callbacks de invocação. `putField` pós-operação é uma escolha deliberada desta implementação para evitar registrar uma atribuição que lançou exceção antes de ocorrer. O pseudocódigo do artigo cita `putFieldPre`; isso é uma diferença a documentar.

As chamadas de array nativas `push`, `pop`, `shift`, `unshift`, `splice` e `reverse` têm modelos de índices para arrays simples. `sort` é modelado somente sem comparador e com valores primitivos. Formas via `call` e `apply` também são reconhecidas. Esses modelos registram índices atribuídos, inclusive se o valor final é igual ao anterior; removem do rastreamento índices apagados. Não são rastreamento das instruções internas do motor JavaScript.

Escritas implícitas em `length` por métodos nativos não têm modelo de origem: se já houver uma escrita rastreada de `length`, ela é invalidada e a execução recebe um aviso de análise parcial. Truncamento explícito via `array.length` invalida os índices removidos.

## Mapeamento e incerteza

O mapa usa hunks Git sem contexto. Primeiro identifica linhas alteradas da base para cada pai; depois projeta somente linhas preservadas de cada pai no merge, verificando igualdade do conteúdo em cada trecho preservado.

As origens possíveis são `BASE`, `L`, `R`, `SHARED` e `MERGE_ONLY`. Uma linha nova só entra como L/R se a contribuição correspondente estiver preservada no merge. Origem compartilhada e mudanças feitas só no merge não são atribuídas arbitrariamente a uma branch.

Esse procedimento é uma heurística textual baseada no alinhamento do Git, não uma prova de autoria semântica. Repetição de texto, movimentação, renomeações e resoluções manuais exigem revisão. Linhas removidas não têm localização executável na versão integrada. Uma única linha pode conter várias operações; o mapa por linha não as distingue.

O analisador utiliza a linha inicial do IID da operação, conforme o source map do Jalangi2. Usa arquivos e linhas, não somente números de linha isolados. Antes de iniciar, exige que o SHA-256 dos bytes executados corresponda ao mapa.

## Limitações da versão

- Subconjunto síncrono ES5; não há suporte geral a escopos ES6, Promises ou propagação de contexto assíncrono.
- `eval`, `Function` dinâmico e agendadores reconhecidos recebem aviso quando invocados. Isso não é um detector exaustivo de toda forma de assincronia ou código dinâmico.
- Getters/setters em fontes configuradas e `with` são rejeitados; proxies e objetos exóticos não fazem parte do domínio assumido.
- Comparadores de `sort`, `fill`, `copyWithin`, chaves com coerção por objetos e outros casos nativos complexos não têm modelo completo. Quando reconhecidos, invalidam o rastreamento afetado e marcam o resultado como parcial.
- Não há suporte geral a mutações ocultas em bibliotecas nativas, monkeypatches de builtins, inicialização de campos dentro de literais de objetos ou sombreamento por parâmetros de `catch`. Uma execução sem avisos não prova ausência de recursos fora do domínio assumido.
- O tratamento de identidade e ordem é experimental; os modelos nativos ainda não foram confrontados com toda a suíte original.
- Resultados do algoritmo indicam candidatos de OA no caminho executado, não conflitos semânticos confirmados. A validação das intenções e do comportamento continua necessária.

`within_declared_subset` significa apenas que o monitor não emitiu avisos conhecidos naquela execução. Não é certificação de completude para JavaScript nem de ausência de conflito.

## Executar

Com o Jalangi2 instalado nesta pasta de trabalho:

```powershell
python scripts/testar_oa.py
python scripts/aplicar_oa_coleta.py
```

Para gerar um mapa para um arquivo de outro cenário:

```powershell
python scripts/mapear_origens_oa.py --repo caminho/do/clone --merge SHA_COMPLETO --path caminho/no/repositorio.js --runtime-path caminho/da/copia/merge.js --out resultados/mapa.json
```

O arquivo executado deve ser uma cópia byte a byte de `git show SHA_COMPLETO:caminho/no/repositorio.js`. Para executar manualmente o controle positivo já gerado:

```powershell
$env:OA_CONFIG = (Resolve-Path resultados/oa_validacao/variable_overwrite/oa_config.json).Path
node ferramentas/jalangi2/src/js/commands/jalangi.js --inlineIID --inlineSource --analysis analisador_oa/analysis.js experimentos/oa_controles/variable_overwrite/program.js
```

Cada processo mantém seu próprio estado de análise. O runner registra saída, erros, configuração e eventos JSON. Em erro ou timeout, o resultado não conta como negativo.
