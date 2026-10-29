# Nova mineração: protocolo em definição

Estado: desenho metodológico inicial. A seleção e o ranking ainda não foram executados. O piloto anterior permanece separado e não integra automaticamente a nova amostra.

## Objetivo

Selecionar projetos JavaScript por volume de histórico, em um universo de candidatos explicitamente registrado, e coletar seus cenários de merge com o MiningFramework oficial.

Mais commits é um critério de atividade e uma estratégia de seleção intencional. Não demonstra, sozinho, qualidade, representatividade ou maior quantidade de conflitos.

## Decisões que precisam ser congeladas antes da seleção

1. Métrica principal: total de commits ou quantidade de merges? Pergunta enviada à pesquisadora. Contar ambas para diagnóstico, mas não trocar a métrica depois de observar o resultado.
2. Universo de candidatos: consulta, fonte, páginas e limites de obtenção. A busca inicial não será tratada como um censo do GitHub.
3. Período: histórico completo ou janela temporal comum? Decidir em função da pergunta da pesquisa e da compatibilidade da análise posterior.
4. Quantidade de projetos e merges por projeto. Não fixar números arbitrários como se fossem requisito do estudo original.
5. Ordenação e desempate: métrica decrescente e, em caso de empate, nome completo do repositório em ordem lexicográfica.
6. Regra de seleção dos merges: todos os elegíveis ou amostra com tamanho e semente previamente definidos. Não repetir a regra de simplesmente pegar os primeiros arquivos exportados.

## Definição reproduzível das contagens

Proposta operacional: usar os ancestrais alcançáveis de um SHA congelado da branch padrão de cada projeto. Registrar data de consulta, branch, SHA, versão Git e condição de histórico completo.

Total de commits, incluindo os nós de merge:

```text
git rev-list --count SHA_CONGELADO
```

Merges de exatamente dois pais, como medida adicional:

```text
git rev-list --count --min-parents=2 --max-parents=2 SHA_CONGELADO
```

Essa definição não conta branches não integradas, pull requests ou todas as referências do servidor. Não deve ser descrita como total absoluto de toda a atividade do projeto.

Se houver janela temporal, usar a mesma para todos os projetos e registrar explicitamente a interpretação de data. O script de inventário adota timestamps de committer em UTC e percorre o histórico inteiro antes de filtrar as datas. Ele não usa o recorte como garantia de compatibilidade da linguagem.

## Critérios propostos para os projetos

- Código público acessível e classificação JavaScript verificável, com a fonte da classificação registrada.
- Não ser um fork duplicado do mesmo histórico na amostra. Manter identificação do repositório e justificativas de exclusão.
- Ser um projeto de software relevante ao objeto da análise; documentações, tutoriais, listas e coleções de exemplos não entram automaticamente por terem a etiqueta JavaScript.
- Histórico completo recuperável e presença de cenários de merge elegíveis.
- Registrar licença e condições de redistribuição antes de publicar snapshots de código.

Não aplicar cortes de estrelas, tamanho ou atividade recente sem justificativa e registro no protocolo. Se houver limite de recursos, registrar os projetos não processados; não tratar a lista restante como ranking global.

## Critérios propostos para os cenários

- Merge de exatamente dois pais.
- Ancestral comum único, distinto dos pais.
- Arquivo `.js` modificado nas duas contribuições em relação à base, com a regra de status do coletor oficial explicitada.
- Quatro versões recuperáveis: base, Left, Right e merge.
- Conservar a ordem dos pais: Left é o primeiro e Right o segundo.
- Separar código-fonte, testes e arquivos gerados/minificados, registrando a regra adotada. Não excluir arquivos apenas porque a execução posterior falhou.
- Documentar se mudanças apenas em comentários ou formatação serão incluídas ou filtradas. Essa decisão ainda está aberta.

## Restrição confirmada da ferramenta original

O README do SCAz.js declara suporte garantido somente até ECMAScript 5.1 e testes em Linux/Ubuntu. O arquivo `.nvmrc` indica Node 18.16.0, e o Jalangi2 é um submódulo que exige a versão especificada pelo projeto.

Consequências para a seleção:

- Criar o repositório antes de 2015 não garante que os arquivos atuais sejam ES5.1.
- Se escolhermos um recorte histórico, a justificativa e as datas devem ser explícitas.
- Se escolhermos código recente, a adaptação da linguagem/ferramenta será uma mudança metodológica a avaliar separadamente.
- Erros de sintaxe, instalação e execução devem aparecer nos resultados e nos denominadores, sem se tornarem resultados negativos de análise.

O clone do Nightmare fornecido pela Amanda é restrito a uso local. Não será tratado como candidato para redistribuição pública nem incluído nos pacotes do GitHub.

## Produtos da nova coleta

- Consulta e inventário bruto dos candidatos, incluindo falhas de obtenção.
- Metadados e contagens no SHA congelado.
- Ranking dentro do universo registrado e lista de selecionados com justificativas.
- Lista de exclusões e razões.
- Entradas e saídas preservadas do MiningFramework oficial.
- Quatro versões e diffs de cada par arquivo–merge, quando a redistribuição for permitida.

## Fontes verificadas em 29/10/2026

- SCAz.js README: https://github.com/amandascm/SCAz.js/blob/main/README.md, blob `977c2643d1bc3f60cfb93cf54730e165d58502a5`.
- Node solicitado pelo projeto: https://github.com/amandascm/SCAz.js/blob/main/.nvmrc, blob `3c79f30eca2530c1f321e82730f392704396ca46`.
- Dependências e comandos: https://github.com/amandascm/SCAz.js/blob/main/package.json, blob `b0658c431190843d4e219d60f1a857422dbbe546`.
- Ordenações e limites da busca GitHub: https://docs.github.com/en/rest/search/search#search-repositories. A ordenação da busca não oferece contagem de commits; a API limita resultados por consulta.
- Contagens Git: https://git-scm.com/docs/git-rev-list.
