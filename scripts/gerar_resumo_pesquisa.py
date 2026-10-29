"""Gera tabelas para apresentacao a partir dos resultados preservados."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
OUT = ROOT / 'dados/apresentacao'
DOCS.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8-sig'))


exploration = read('resultados/underscore_pre2015/resumo.json')
oa = read('resultados/oa_coleta/resumo.json')
validation = read('resultados/oa_validacao/resumo.json')
repeat = read('resultados/miningframework/reproducibilidade.json')
framework = read('resultados/miningframework/ambiente.json')
assert validation['tests'] == validation['passed'] == 44
assert oa['file_merge_pairs'] == framework['collected_file_merge_pairs'] == 6
assert repeat['same_merges_files_and_branch_line_sets']
valid = [r for r in oa['results'] if r['status'] == 'success']
both = [r for r in valid if r['executed_branch_lines']['L'] and r['executed_branch_lines']['R']]
comparison = [
    ('Escopo', 'Estudo publicado em 2024', 'Replicacao metodologica em preparacao; piloto experimental', 'Nao e uma reproducao integral concluida'),
    ('Projetos na avaliacao empirica', '50', '1: Underscore no lote oficial', 'Coleta exploratoria incluiu tambem jsFSTMerge; nao confundir escopos'),
    ('Pares arquivo-merge avaliados/tentados', '452', str(oa['file_merge_pairs']), 'Amostras e criterios nao identicos'),
    ('Execucoes bem-sucedidas', '159', str(len(valid)), 'Original: 35,18%; piloto: 66,67%; nao indica superioridade'),
    ('Erros de execucao', '293', str(oa['status_counts']['execution_error']), 'Piloto: arquivos de teste sem contexto, $ is not defined'),
    ('Alertas OA observados', '1', str(oa['total_events_successful']), 'Zero alerta nao comprova ausencia de conflito'),
    ('Validacao controlada', '69 casos avaliaveis, derivados de 71; 14 adaptados e 55 sem adaptacao conceitual', f"{validation['passed']} controles sinteticos aprovados", 'Suites distintas: nao comparar como precisao ou acuracia'),
    ('Analisador OA', 'Implementacao original da Amanda', 'Reimplementacao independente experimental v0.2', 'Equivalencia com o original nao demonstrada'),
    ('Ferramentas', 'MiningFramework e Jalangi2', 'MiningFramework oficial e Jalangi2 oficial; analisador proprio', 'Versoes do piloto fixadas; versoes originais nao recuperadas'),
    ('Mapas de origem', 'Mapas associados ao dataset original', '6 mapas conservadores gerados a partir do Git', 'Exigem revisao; nao sao os mapas originais'),
    ('Desempenho', 'Experimento de overhead publicado', 'Benchmark comparavel ainda nao realizado', 'Tempos de verificacao locais nao equivalem ao benchmark'),
    ('Extensao com dataflow', 'Fora do nucleo OA aqui reproduzido', 'Ainda nao implementada; desenho a alinhar com orientador', 'Propagacao do contexto de chamadas nao e uma analise geral de dataflow'),
]
with (OUT / 'comparacao_amanda_piloto.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['indicador', 'artigo_amanda', 'trabalho_atual', 'limite_da_comparacao'])
    w.writerows(comparison)

categories = {'positivos': 0, 'negativos': 0, 'avisos_de_limites': 0, 'rejeicoes_de_fontes': 0, 'outros_controles_de_mapeamento_integridade': 0}
for result in validation['results']:
    if result.get('expected_warning'):
        categories['avisos_de_limites'] += 1
    elif result.get('expected_rejection'):
        categories['rejeicoes_de_fontes'] += 1
    elif result.get('expected_events') is not None and result.get('expected_events', 0) > 0:
        categories['positivos'] += 1
    elif result.get('expected_events') == 0:
        categories['negativos'] += 1
    else:
        categories['outros_controles_de_mapeamento_integridade'] += 1
assert sum(categories.values()) == validation['tests']

with (OUT / 'execucoes_oa_para_slide.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['merge', 'arquivo', 'status', 'alertas_oa', 'linhas_com_eventos_L', 'linhas_com_eventos_R'])
    for r in oa['results']:
        w.writerow([r['merge_sha'][:12], r['file_path'], r['status'],
                    r['event_count'] if r['event_count'] is not None else 'NA',
                    r['executed_branch_lines']['L'], r['executed_branch_lines']['R']])

numbers = dict(official_pilot_merges=5, official_file_merge_pairs=6,
              oa_success=len(valid), oa_errors=oa['status_counts']['execution_error'],
              oa_alerts=oa['total_events_successful'], synthetic_controls=validation['tests'],
              synthetic_controls_passed=validation['passed'], controls_by_category=categories,
              successful_cases_observing_both_origins=len(both),
              exploratory_git_python=dict(merges_in_scope=exploration['merges_in_scope'],
                  candidate_merges=exploration['candidate_merges'], candidate_pairs=exploration['candidate_files'],
                  complete_quadruples=exploration['candidate_files_with_four_versions']),
              original_suite_executed=False, original_analyzer_obtained=False,
              semantic_conflicts_confirmed=None, dataflow_extension_implemented=False)
(OUT / 'numeros_verificados.json').write_text(json.dumps(numbers, indent=2, ensure_ascii=False), encoding='utf-8')

text = '''# Comparação para apresentação: artigo da Amanda e trabalho atual

Atualizado em 29/10/2026. Números do piloto lidos dos arquivos de resultados; números do artigo transcritos da leitura do PDF. Fonte bibliográfica: Moraes, Borba e Da Silva, SBLP 2024, [Semantic conflict detection via dynamic analysis](https://doi.org/10.5753/sblp.2024.3471).

## Mensagem central

Foi possível construir e executar um fluxo experimental sem o pacote original: MiningFramework oficial, arquivos históricos, mapas de linhas e Jalangi2 com um analisador OA independente. O resultado é um protótipo validado em controles próprios; a reprodução integral e a extensão com dataflow ainda não estão concluídas.

## Comparação de escopo e resultados

| Indicador | Artigo da Amanda | Trabalho atual | Como interpretar |
| --- | --- | --- | --- |
'''
for metric, original, current, caution in comparison:
    text += f'| {metric} | {original} | {current} | {caution} |\n'
text += '''
No artigo, a Figura 5 informa 452 amostras, 159 execuções bem-sucedidas e 293 erros. A indicação textual de 65% para os 159 casos é inconsistente; 159/452 corresponde a aproximadamente 35,18%. A comparação acima usa as contagens, não esse percentual textual.

## O que foi feito, com evidências

| Entrega | Estado | Arquivo de evidência, a partir da raiz do repositório |
| --- | --- | --- |
| Levantamento do método, resultados e limitações | Documentado | `PLANO_DE_REPLICACAO.md` |
| Mineração exploratória com Git/Python | Executada: 509 merges no recorte, 184 pares candidatos em 146 merges | `resultados/underscore_pre2015/resumo.json` |
| Verificação de quádruplas da coleta exploratória | 181 pares com quatro versões disponíveis; cinco exportados | `resultados/underscore_pre2015/arquivos_candidatos.csv` |
| Mineração com a ferramenta oficial | Executada: cinco merges, seis registros | `resultados/miningframework/saida_oficial/data/results.csv` |
| Repetição do lote oficial | Mesmos seis pares e mesmos conjuntos de linhas por branch | `resultados/miningframework/reproducibilidade.json` |
| Jalangi2 oficial | Instalado e executado em controles e arquivos reais | `resultados/jalangi2/resumo.json` |
| Mapas de linhas da versão integrada | Seis mapas gerados; autoria textual conservadora, revisão pendente | `resultados/oa_coleta/*/line_to_branch_map.json` |
| Analisador OA independente | Protótipo v0.2 executado | `analisador_oa/analysis.js` |
| Validação própria | 44 controles aprovados | `resultados/oa_validacao/resumo.json` |
| Aplicação OA ao lote oficial | Quatro sucessos sem alerta e dois erros | `resultados/oa_coleta/resultados.csv` |
| Recuperação e validação com o pacote original | Pendente | `analisador_oa/README.md` descreve o limite |
| Ampliação com MiningFramework além do piloto | Pendente | Os 509 merges pertencem à coleta Git/Python anterior |
| Extensão com dataflow | Pendente, desenho a alinhar | Não há implementação dessa extensão neste repositório |

## Composição dos 44 controles

'''
for name, count in categories.items():
    text += f'- {name.replace("_", " ")}: {count}.\n'
text += '''
Esses grupos incluem verificações de rejeição e de análise parcial. “44 aprovados” significa que os resultados esperados desses controles foram satisfeitos, não 100% de precisão do detector em software real. Os controles não substituem a suíte original de 69 casos.

## Resultado empírico do piloto

| Merge | Arquivo | Resultado | Alertas | Linhas com eventos L / R |
| --- | --- | --- | ---: | ---: |
'''
for r in oa['results']:
    status = 'Sucesso' if r['status'] == 'success' else 'Erro de execução'
    alerts = r['event_count'] if r['event_count'] is not None else '—'
    lines = r['executed_branch_lines']
    text += f'| `{r["merge_sha"][:12]}` | `{r["file_path"]}` | {status} | {alerts} | {lines["L"]} / {lines["R"]} |\n'
text += '''
As linhas com eventos refletem escritas e invocações rastreadas; não representam cobertura completa de linhas ou caminhos. Somente uma das quatro execuções válidas registrou eventos de ambas as origens. As duas falhas dependem de contexto de testes ausente (`$ is not defined`).

## Sugestão de três slides

1. **Aprofundamento e implementação:** método compreendido; MiningFramework e Jalangi2 oficiais executados; mapeamento e núcleo OA independentes implementados. Mostrar o fluxo e a distinção em relação ao pacote original.
2. **Dados obtidos:** cinco merges oficiais → seis arquivos → quatro sucessos e dois erros; 44 controles próprios aprovados. Mostrar o caso positivo sintético como demonstração de funcionamento, identificado como sintético.
3. **Limites e próximos passos:** sem equivalência demonstrada; baixa exercitação das duas contribuições; revisão dos mapas e validação independente; ampliar coleta oficial; definir extensão com dataflow.

## Texto para apresentar ao professor

“Aprofundei o estudo do algoritmo e avancei do entendimento para um fluxo executável. Configurei as ferramentas oficiais, executei uma mineração piloto de cinco merges e obtive seis arquivos candidatos. Preparei os mapas na versão integrada e implementei um núcleo OA independente, com 44 controles próprios aprovados. No piloto, quatro arquivos executaram sem alertas e dois falharam por falta de contexto de testes. Ainda não considero isso uma reprodução integral: preciso confrontar a implementação com o pacote original e melhorar a exercitação das contribuições antes de avaliar a extensão com dataflow.”

As planilhas CSV para montar os slides estão em `dados/apresentacao/`. Esse material não afirma descoberta de um conflito real nem novidade científica já estabelecida.
'''
(DOCS / 'COMPARACAO_ESTUDO_E_PILOTO.md').write_text(text, encoding='utf-8')
print(json.dumps(numbers, indent=2, ensure_ascii=False))
