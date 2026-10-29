# Proposta de extensão: efeito da cobertura na detecção dinâmica de OA

Atualização de escopo: a pesquisadora mencionou posteriormente uma extensão com **dataflow**, a alinhar com o orientador. Essa extensão ainda não foi implementada. A proposta de cobertura abaixo é um desenho anterior e pode servir à avaliação de exercitação; não deve ser apresentada como decisão final sobre a contribuição do mestrado.

Escopo confirmado: replicar o estudo de Moraes, Borba e Da Silva (SBLP 2024) e realizar uma extensão. A direção abaixo é uma proposta de trabalho, ainda não uma escolha confirmada pelo pesquisador. Prazo e contexto acadêmico ainda não informados.

## Motivação e contribuição proposta

O estudo original executa arquivos da versão integrada e reconhece que eles podem não exercitar as funções relevantes. Nas seções 5 e 8, os próprios autores sugerem reaproveitar testes e inserir chamadas, inclusive com fuzzing. Portanto, a contribuição não seria apresentar essa ideia como inédita, mas implementar e avaliar de maneira controlada seu efeito na detecção, no custo e na qualidade dos alertas.

Título provisório: **Impacto da cobertura de execução na detecção dinâmica de conflitos semânticos por sobrescrita em JavaScript**.

Pergunta principal: aumentar a execução de código atribuído às duas branches aumenta a descoberta de conflitos OA confirmados, com qual custo e com quais limitações?

Hipótese a testar, sem antecipar o resultado: exercitar mais operações relevantes às contribuições permite encontrar conflitos que a execução direta não revela. Aumento de cobertura não garante aumento de conflitos confirmados.

## Desenho em duas fases

### Fase 1 — Reprodução

Seguir `PLANO_DE_REPLICACAO.md`: recuperar o pacote, congelar versões, executar suíte, reproduzir Nightmare, executar o dataset original e comparar resultados. Manter todos os resultados e erros, incluindo divergências do ambiente.

Se a implementação ou o dataset não forem recuperados, registrar o bloqueio e reformular explicitamente como reimplementação ou nova avaliação. Não apresentar esse caminho como reprodução exata dos resultados publicados.

### Fase 2 — Extensão com comparação pareada

Usar os mesmos cenários, commits e mapas de origem nas duas condições:

| Condição | Execução | Função na avaliação |
| --- | --- | --- |
| A | Entrada direta do arquivo integrado, conforme o procedimento original recuperado | Referência |
| B | Testes existentes que carreguem o código relevante, executados com a análise OA | Extensão principal proposta |

Começar com um piloto pequeno e declarado, por exemplo 10–20 amostras, para verificar compatibilidade dos testes e instrumentação. O piloto serve para ajustar o protocolo; alterações devem ser congeladas antes da avaliação principal.

Se a maioria dos projetos não tiver testes utilizáveis, considerar uma alternativa B com drivers explícitos. Drivers exigem entradas documentadas e comparação separada; não substituir a condição durante o experimento sem registrar a mudança.

Geração automática de entradas/fuzzing é uma possibilidade posterior, caso o prazo permita. Não incluir simultaneamente modernização de linguagem, novos algoritmos e nova mineração na extensão inicial: cada mudança dificulta atribuir o efeito observado à cobertura.

## Perguntas e medidas

| Pergunta | Medidas |
| --- | --- |
| A condição B executa mais código relevante? | Linhas alteradas executadas por branch e execução de ambas as contribuições por cenário |
| B encontra conflitos adicionais? | Cenários com OA confirmada em A, em B, em ambas, somente em A e somente em B |
| Qual a qualidade dos alertas? | Alertas revisados, conflitos confirmados, falsos positivos e inconclusivos |
| Qual o custo? | Tempo total, tempo por cenário, timeout, falhas de instalação/instrumentação/teste |

Definir a unidade principal como cenário de arquivo-em-merge, consistente com a amostra original, e registrar também a quantidade de merges e projetos únicos. Se testes carregarem vários arquivos, identificar o arquivo-alvo de cada resultado para evitar misturar unidades.

Um mesmo conflito pode gerar muitos eventos. Preservar eventos brutos, mas contar resultados por cenário e por conflito deduplicado. Documentar a chave de deduplicação, por exemplo arquivo-alvo e par de locais de escrita de origens opostas.

Cobertura relevante proposta: para cada branch, número de linhas alteradas executáveis e cobertas dividido pelo número de linhas alteradas executáveis no arquivo integrado. Linhas removidas não existem no merge e não entram nesse denominador. Documentar como linhas executáveis são identificadas; cobertura por linha é uma aproximação e uma linha pode conter várias operações.

## Rótulos e revisão dos alertas

Separar três níveis de evidência:

1. Alerta emitido pela ferramenta.
2. OA confirmada pelo rastreamento: mesmo elemento de estado, contribuições opostas e sequência de escritas compatível com a definição do algoritmo.
3. Conflito semântico confirmado: evidência de comportamento esperado de uma contribuição que deixa de ser preservado na integração.

Para o nível 3, registrar teste testemunha, documentação, histórico ou comparação comportamental das versões quando viável. Uma OA observada pode ser intencional; não classificar automaticamente todo alerta como defeito.

Revisar todos os alertas adicionais. Se viável, usar dois revisores humanos com critérios prévios e resolução de divergências. Se houver apenas um revisor, declarar essa limitação. Não assumir autorização para contatar terceiros.

Quando necessário, executar base e pais para verificar a evidência do conflito. Isso é parte da validação humana/experimental; o detector continua operando sobre o código integrado.

Sem rotulação independente dos negativos, não calcular recall, F1 ou acurácia global. A medida principal viável é quantidade de conflitos adicionais confirmados e proporção de alertas confirmados entre os julgáveis, acompanhada da quantidade de inconclusivos.

## Controle experimental

- Congelar dataset, versões, critérios e orçamento de execução antes da avaliação principal.
- Usar o mesmo detector e o mesmo mapa de branches nas condições A e B.
- Executar cada teste em processo separado ou reiniciar o estado da análise entre testes. A definição adotada não deve permitir que uma escrita de um teste seja comparada indevidamente com uma escrita de outro.
- Verificar suporte do detector ao test runner, carregamento de módulos e eventual assincronia; não presumir que uma pilha síncrona preserve corretamente toda origem em callbacks.
- Registrar separadamente cobertura e tempo se a medição de cobertura adicionar instrumentação. Não atribuir o custo do coletor de cobertura ao detector sem explicitação.
- Adotar orçamento definido por cenário, informar quantos testes executaram e quantos terminaram. Testes que falham podem conter rastros úteis, mas os resultados precisam de marcação própria.
- Reportar todas as tentativas e, em separado, comparações entre os cenários executáveis nas duas condições. Excluir silenciosamente os casos difíceis causa viés.
- Registrar semente e entradas quando houver aleatoriedade. Usar repetições para tempo; não contar repetições do mesmo cenário como novas amostras independentes.

## Análise dos resultados

Apresentar primeiro contagens absolutas e transições entre condições. Se A não confirmar nenhum conflito no subconjunto analisado, relatar o ganho absoluto; não dividir por zero para produzir ganho percentual.

Apresentar distribuição por projeto e a lista dos casos adicionais confirmados. Arquivos do mesmo merge e projeto podem ser dependentes; não tratar automaticamente todos como observações independentes em testes estatísticos.

Se houver amostra suficiente e necessidade de inferência estatística, escolher o procedimento após conhecer a estrutura dos dados, com atenção ao pareamento e ao agrupamento por projeto. Com poucos positivos, priorizar descrição, evidências por caso e incerteza sobre conclusões amplas.

## Entregáveis propostos

- Protocolo e relatório da reprodução com resultados publicados versus obtidos.
- Ambiente e comandos com versões fixadas e logs preservados.
- Adaptação para executar os testes sob o detector, sem modificar silenciosamente seu algoritmo.
- Tabela pareada por cenário, dados de cobertura e duração, e revisão dos alertas.
- Discussão da extensão: ganhos, falhas, custo e ameaças à validade.

## Marco imediato

Recuperar o pacote original e executar a suíte e o caso Nightmare. A extensão deve avançar para o piloto quando houver uma referência executável. A dimensão final depende do prazo, da disponibilidade dos artefatos e da compatibilidade dos testes históricos.
