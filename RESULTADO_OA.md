# Mapeamento e reimplementação experimental OA executados

Data: 29/10/2026.

## Entregas realizadas

Foi implementado um mapeador de linhas para branches na versão integrada e um analisador OA independente executado no Jalangi2 oficial. O fluxo atual é:

**MiningFramework oficial → arquivo do merge → mapa de origens → Jalangi2 + analisador OA independente → eventos e diagnóstico.**

O analisador é identificado como `independent-oa-v0.2`. O original da Amanda não foi recuperado. Essa distinção faz parte dos resultados e da metodologia da futura dissertação.

## Validação controlada

**44 de 44 controles passaram.** Os controles foram criados nesta pesquisa; não são a suíte original de 69 casos avaliáveis do artigo.

Eles cobrem sobrescritas L→R e R→L, valores iguais, escrita intermediária da base, escopos e closures, aliases, objetos distintos, propriedades distintas, índices, chamadas indiretas e aninhadas, exceções, exclusões, truncamento de array, operações nativas restritas e rejeições/avisos para recursos fora do domínio.

Também foram construídos DAGs Git sintéticos com base, pais e merge para verificar a geração do mapa e sua integração ao detector, incluindo mudanças de posição das linhas, mudanças compartilhadas e alterações exclusivas do merge. Uma cópia modificada depois do mapeamento foi rejeitada pelo checksum.

Exemplo positivo controlado:

```javascript
var x = 0; // base
x = 1;     // L
x = 2;     // R
```

A execução produz um evento `OVERRIDING_ASSIGNMENT` para `var:2:x`, com escrita anterior na linha 2 de L e escrita atual na linha 3 de R. O JSON inclui arquivo, coluna, IID e contexto de chamadas. Esse exemplo é sintético; não é uma descoberta de conflito em software real.

Evidência: `resultados/oa_validacao/variable_overwrite/oa_report.json`.

## Aplicação aos dados coletados pela ferramenta oficial

Foram gerados seis mapas a partir dos seis pares arquivo–merge do lote oficial. As cópias executadas preservaram os bytes da versão integrada; cada mapa registra os SHAs completos e o checksum.

| Merge abreviado / arquivo | Execução | Alertas OA | Linhas com eventos de origem L / R |
| --- | --- | ---: | ---: |
| `a2aab7c69968` / `test/utility.js` | Erro: falta contexto de testes | — | 0 / 0 |
| `a2aab7c69968` / `underscore.js` | Sucesso | 0 | 1 / 24 |
| `b5f111e8d4b3` / `test/utility.js` | Erro: falta contexto de testes | — | 0 / 0 |
| `8c15ae153aae` / `underscore.js` | Sucesso | 0 | 0 / 0 |
| `e863fbf285f7` / `underscore.js` | Sucesso | 0 | 0 / 10 |
| `2b9a011e070b` / `underscore.js` | Sucesso | 0 | 0 / 0 |

As quatro execuções válidas terminaram sem avisos conhecidos da versão final. As duas falhas continuam registradas como erros, com `$ is not defined`, e não como negativos.

A última coluna conta linhas associadas a eventos rastreados de escrita ou invocação, não cobertura completa de linhas. Apenas uma execução registrou eventos atribuídos às duas branches. Isso limita fortemente a interpretação dos quatro resultados sem alerta.

**Nenhum conflito semântico foi confirmado neste lote.** Zero eventos no caminho executado não demonstra ausência de conflito, nem permite estimar recall, acurácia ou falsos negativos.

## Decisões metodológicas e limites

O mapa é textual e conservador, com origens `BASE`, `L`, `R`, `SHARED` e `MERGE_ONLY`. Ele ainda exige revisão; não foi demonstrado que reproduz os mapas manuais da Amanda.

O analisador considera identidade dos ambientes e objetos e propaga contexto em chamadas síncronas. Os modelos nativos de índices são restritos a arrays simples. A associação direta da instrução tem precedência sobre o contexto herdado; propriedades são monitoradas após a escrita, enquanto o pseudocódigo do artigo cita o callback anterior à escrita. Essas são decisões explícitas desta reimplementação a confrontar com o original.

Casos de linguagem e comportamento fora do domínio, incluindo objetos exóticos, mutações nativas não modeladas, inicialização de campos em literais e sombreamento por parâmetros de `catch`, não estão cobertos em geral. A documentação técnica detalha os avisos implementados e suas limitações. Não há garantia geral de que todo recurso fora do domínio seja automaticamente reconhecido.

O resultado atual é um protótipo executável do núcleo OA, não uma reprodução integral validada do estudo publicado.

## Como repetir e inspecionar

```powershell
python scripts/testar_oa.py
python scripts/aplicar_oa_coleta.py
```

Nesta máquina pode ser utilizado o Python do runtime do Codex, caso o comando `python` não encontre o interpretador desejado.

Arquivos principais:

- `analisador_oa/analysis.js`: implementação independente;
- `analisador_oa/README.md`: domínio, decisões e limites;
- `scripts/mapear_origens_oa.py`: construção dos mapas;
- `resultados/oa_validacao/resumo.json`: 44 controles e resultados;
- `resultados/oa_coleta/resultados.csv`: resultado por par arquivo–merge;
- `resultados/oa_coleta/resumo.json`: resumo da aplicação;
- `resultados/oa_coleta/ambiente.json`: versões e hashes do analisador e mapeador;
- subpastas por amostra em `resultados/oa_coleta`: mapa, fonte anotada, configuração, eventos, stdout e stderr.

## Próximo marco científico

Revisar manualmente os mapas e os eventos de um caso real com ambas as contribuições exercitadas; ampliar a validação com a suíte original ou equivalentes rotulados independentemente. Depois, exercitar funções relevantes com drivers/testes, mantendo os resultados separados da execução direta. A evolução dos modelos não deve ser apresentada como equivalência ao original sem essa avaliação.
