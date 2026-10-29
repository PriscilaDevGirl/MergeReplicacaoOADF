# Protocolo inicial de replicação

Estudo: **Semantic conflict detection via dynamic analysis**, Amanda Moraes, Paulo Borba e Léuson Da Silva, SBLP 2024.

Fonte principal: `C:\Users\Convidado!\Downloads\texto1.pdf`, 9 páginas. Leitura visual das nove páginas realizada em 29/10/2026. O PDF é composto por imagens, sem texto extraível.

Estado atualizado: levantamento concluído; pilotos de mineração executados com Git/Python e depois com o MiningFramework oficial. Jalangi2 executado com cobertura oficial e com analisador OA independente experimental. O mapeador e o núcleo OA passaram por 44 controles; seis arquivos reais foram tentados, com quatro sucessos sem alertas e dois erros. O analisador original e a suíte do artigo ainda não foram recuperados, e não foi demonstrada equivalência. Ver `FERRAMENTAS_OFICIAIS_EXECUTADAS.md` e `RESULTADO_OA.md` para comandos, resultados e limitações. Este documento distingue resultados publicados de decisões propostas para a replicação.

## 1. O que será reproduzido

O detector procura overriding assignments (OA): contribuições de branches diferentes escrevem no mesmo elemento de estado durante a execução do código integrado, sem uma escrita intermediária do código não atribuído às branches que descarte essa associação. A análise acompanha também chamadas de funções para atribuir escritas indiretas à contribuição que as provocou.

A identificação usa a identidade do elemento de estado; nomes de variáveis iguais, isoladamente, não identificam o mesmo alvo. Campos e índices são tratados como elementos independentes dos objetos/arrays que os referenciam.

O código executado é a versão após o merge. Base e pais continuam necessários para recuperar a origem das mudanças e produzir o mapa de linhas para branches.

Há três blocos experimentais:

1. Validação nos casos de teste traduzidos de Java para JavaScript.
2. Avaliação em arquivos de cenários reais de merge.
3. Medição do custo de execução com e sem instrumentação e análise.

## 2. Artefatos e disponibilidade

| Artefato | Fonte | Situação verificada |
| --- | --- | --- |
| Implementação, testes, dataset e resultados | https://github.com/amandascm/SCAz.js | Endereço da referência [19]; retornou 404 na consulta web e nos pedidos de arquivos pelo conector GitHub. Isso não distingue remoção, mudança de nome ou restrição de acesso. |
| Testes Java de origem | https://github.com/spgroup/conflict-static-analysis/tree/2f481eb58b/src/test/java/br/unb/cic/analysis/samples/ioa | Endereço transcrito da referência [14]; conteúdo ainda não auditado. |
| Minerador | https://github.com/spgroup/miningframework | Referência [13]; versão utilizada no estudo ainda precisa ser identificada. |
| Jalangi2 | https://github.com/Samsung/jalangi2 | Referência [25]; commit e dependências do experimento precisam ser recuperados. |
| Ambiente de tutorial da autora | https://github.com/amandascm/jalangi2env | README consultado pelo conector GitHub. Oferece ambiente Docker de tutorial; não foi identificado como o pacote de replicação deste estudo. |

Prioridade: recuperar o pacote original ou um arquivo histórico verificável, incluindo commit, lockfile, instruções e dados. O artigo sozinho não permite garantir que uma nova implementação reproduza todos os detalhes da ferramenta original.

## 3. Resultados publicados a comparar

| Bloco | Resultado de referência | Local no PDF |
| --- | --- | --- |
| Casos Java originais | 71 | Seção 4.1, p. 4–5 |
| Divergências de transpilação | 2 | Tabela 1, p. 5 |
| Casos com adaptação conceitual | 14 | Tabela 1, p. 5 |
| Casos sem essa adaptação | 55 | Tabela 1, p. 5 |
| Casos de teste avaliáveis | 69, relatados como corretos segundo os resultados esperados adotados | Seção 4.1, p. 5 |
| Projetos na lista inicial | 50 | Seção 4.2.1, p. 5 |
| Amostras de arquivos em merges | 452 | Figura 5, p. 6 |
| Erros de execução | 293 | Figura 5, p. 6 |
| Execuções bem-sucedidas | 159 | Figura 5, p. 6 |
| Alertas OA | 1, considerado verdadeiro positivo pelos autores | Seção 4.2.2, p. 6 |
| Execuções sem alerta | 158 | Figura 9, p. 7 |
| Negativos apoiados pela análise auxiliar | 132 sem alvo reatribuído no caminho executado | Seção 4.2.2, p. 6 |
| Negativos não verificados | 26 | Figura 9, p. 7 |

Um cenário empírico é uma amostra de arquivo associada a um merge; não presumir que 452 amostras correspondam a 452 commits de merge distintos.

Caso positivo de referência: projeto Nightmare, merge `3713f3db`, arquivo `lib/actions.js`; contribuições associadas aos commits `9f5ffa73` e `786f978` redefinem `exports.inject`. Os prefixos devem ser resolvidos em SHAs completos antes de executar a réplica.

## 4. Sequência de execução proposta

### Etapa A — Congelar os materiais

- Recuperar implementação OA, `test_cases`, testes Jest, mapas JSON, lista `projects.csv`, dataset de merges, logs e scripts de tempo.
- Registrar URL, commit/tag, data, checksum e licença de cada material obtido.
- Recuperar versões de Node.js, npm, Jalangi2, Jest, minerador e bibliotecas dos projetos. Não escolher versões modernas silenciosamente.
- Registrar limitações de disponibilidade e qualquer mudança em relação ao original.

Critério para avançar: executar um exemplo com a ferramenta original e registrar entrada, mapa de linhas e saída. Se não for possível recuperar a implementação, mudar explicitamente o desenho para uma reimplementação independente.

### Etapa B — Executar a suíte controlada

- Usar os casos JavaScript e os mapas originais, caso disponíveis, evitando uma nova transpilação desnecessária.
- Conferir os 2 casos excluídos e as justificativas dos 14 adaptados; 11 das adaptações são relacionadas à distinção de elementos de estado, segundo o texto.
- Conferir a presença de uma chamada de entrada nos casos; definir funções sem invocá-las pode produzir execução vazia.
- Executar a suíte e salvar resultado esperado, resultado observado, eventos OA, stdout, stderr, duração e código de saída por caso.
- Relatar separadamente os 55 casos sem adaptação e os 14 adaptados. A tabela do artigo chama a medida de “Precision”, mas não fornece nessa tabela uma matriz de confusão completa; não renomeá-la automaticamente como acurácia ou recall.

Critério: obter a mesma classificação esperada para os 69 casos avaliáveis ou explicar cada divergência.

### Etapa C — Reproduzir primeiro o caso Nightmare

- Recuperar base, pais e merge usando os identificadores completos.
- Conferir as duas definições de `exports.inject` na versão integrada.
- Recuperar o mapa de linhas e instalar as dependências compatíveis com o commit histórico em ambiente isolado.
- Executar a versão integrada com Jalangi2 e a análise OA.
- Verificar que o alerta aponta o mesmo alvo e contribuições esperadas.

Critério: reproduzir o alerta positivo publicado antes de iniciar a execução em lote.

### Etapa D — Executar o dataset original

- Priorizar as 452 amostras já coletadas. Uma nova mineração pode alterar a amostra e deve ser tratada separadamente.
- Preservar o filtro temporal relacionado ao lançamento do ES6 em 2015 mencionado na seção 6; recuperar a data exata e as regras nos scripts, pois o texto não basta para determinar a inclusão na fronteira.
- Para cada amostra, verificar que há mudanças atribuíveis a ambas as branches e que as linhas do mapa correspondem à versão pós-merge.
- Separar erro de instalação, erro de instrumentação, erro de execução, timeout e execução válida. Nenhuma dessas falhas conta como negativo.
- Registrar sucesso sem alerta sem inferir automaticamente ausência de conflito.
- Aplicar a análise auxiliar de reatribuições usada pelos autores e manter os 26 casos não verificados em categoria própria.

Critério: comparar as contagens de amostras, falhas, sucessos e alertas com o artigo, além de revisar as divergências individualmente.

### Etapa E — Reproduzir os tempos

O artigo descreve três instâncias Amazon EC2 t2.large, com 8 GiB, 2 vCPUs e Ubuntu 24.04 amd64. Confirmar configurações e scripts antes de contratar infraestrutura. Experimentos locais podem verificar funcionamento; seus tempos não são diretamente equivalentes aos tempos nessa infraestrutura.

Medir separadamente: (a) script original; (b) script instrumentado com infraestrutura nativa; (c) instrumentado com a análise OA. O artigo exclui o tempo de instrumentação das duas últimas categorias.

Proposta adicional de controle, a declarar na réplica: aquecimento, várias repetições, ordem de execução alternada, limites de tempo definidos e registro de carga da máquina. A quantidade de repetições do estudo original precisa ser recuperada.

Calcular por amostra:

`overhead_percentual = 100 * (tempo_analise / tempo_original - 1)`

Também calcular OA sobre instrumentado e instrumentado sobre original. Resumir mediana, média e intervalo interquartil dos valores por amostra. Não substituir a média das razões pela razão das médias.

## 5. Cuidados na interpretação

- 159/452 = aproximadamente 35,18% de execuções bem-sucedidas; 293/452 = 64,82% de erros. A frase com “159 samples executed (65%)” na p. 6 é inconsistente com as contagens e a Figura 5.
- 132/158 = 83,54% dos negativos; 132/159 = 83,02% das execuções. Registrar sempre o denominador. A conclusão menciona 85%, sem suporte claro nas contagens apresentadas.
- Um alerta verificado como verdadeiro e nenhum falso positivo observado não demonstram ausência geral de falsos positivos. Há apenas um positivo observado.
- Os 26 negativos não verificados impedem calcular recall e uma matriz de confusão empírica completa. Não assumir falsos negativos iguais a zero.
- Os 132 casos sem reatribuição sustentam ausência desse padrão no caminho executado; não demonstram ausência de conflito em todos os caminhos ou entradas.
- Na seção 4.2.3 são relatadas médias de 91, 97 e 132 ms; a barra “Original” da Figura 10 parece próxima de 51 ms. Recuperar dados brutos antes de adotar esses valores como referência de desempenho.
- A seção 4.2.3 relata overhead mediano de 164,5%, médio de 172% e IQR de 55%; esses resumos por amostra não precisam coincidir com razões entre médias globais.
- A cobertura dinâmica e a execução de arquivos que podem não ser pontos de entrada são limitações centrais. Reutilizar testes ou inserir chamadas para aumentar cobertura seria uma extensão a medir separadamente.

## 6. Registro mínimo dos resultados

Usar um registro por amostra e execução, com os campos:

`sample_id, project_url, merge_sha, base_sha, left_sha, right_sha, file_path, source_checksum, map_checksum, runtime_version, tool_sha, execution_mode, repetition, status, exit_code, duration_ms, oa_event_count, manual_label, stdout_path, stderr_path`

Valores desconhecidos permanecem desconhecidos; não preencher rótulos com resultados previstos. Manter resultados publicados em tabela distinta dos resultados obtidos.

## 7. Próxima ação e pendências

Recuperar o pacote da referência [19] por endereço atualizado, arquivo histórico ou cópia fornecida pelos autores. Se houver contato com os autores, solicitar: implementação e commit usado no SBLP 2024, suíte e mapas, 452 amostras e resultados, scripts/dados de tempo e configuração do ambiente. Nenhuma mensagem foi enviada.

Escopo confirmado pelo pesquisador: **replicar e fazer uma extensão**. A proposta de extensão está em `PROTOCOLO_DA_EXTENSAO.md`; a escolha específica ainda é uma recomendação a discutir. Preservar os resultados da reprodução original antes de executar qualquer mudança de cobertura ou de amostra.
