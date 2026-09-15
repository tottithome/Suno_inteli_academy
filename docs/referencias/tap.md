# CASE SETEMBRO: SUNO CONTENT

## 1. Contextualização do problema

O mercado financeiro produz um volume diário de comunicados cruciais para a tomada de decisão: atas do Copom, fatos relevantes, relatórios de inflação e releases de resultados trimestrais. Esses documentos são redigidos em linguagem técnica, densa e formal, criando uma barreira de compreensão para investidores iniciantes e intermediários.

A prática comum de usar LLMs para resumir esses documentos enfrenta dois problemas:

1. **Resumo por encurtamento (trivialização):** a IA frequentemente apenas corta frases ou simplifica o vocabulário de forma ingênua, perdendo nuances macroeconômicas críticas ou infantilizando a comunicação.
2. **Avaliação subjetiva (falta de rigor técnico):** a validação costuma depender apenas de outro prompt genérico (LLM-as-a-judge), sujeito a viés de complacência, viés de extensão e incapacidade de quantificar densidade conceitual.

Para que um sistema de IA seja viável em ambientes regulados e profissionais, ele precisa de uma camada de avaliação quantitativa, determinística e baseada em dados (Eval-Driven Development), capaz de aferir adequação do tom, fidelidade factual e densidade de terminologia técnica.

## 2. Objetivo

Desenvolver um sistema inteligente baseado em grafos com estado capaz de receber documentos financeiros públicos densos e gerar conteúdos adaptados para 3 níveis de sofisticação (Iniciante, Intermediário e Avançado) em 3 formatos de mídia (Texto Analítico, Carrossel Informativo e Roteiro de Vídeo Curto).

O principal diferencial é o **Avaliador Híbrido de Calibração e Rigor**: métricas linguísticas determinísticas, extração de entidades financeiras e julgamento estruturado, sem recorrer a simples encurtamento textual.

## 3. Pergunta norteadora

Como desenhar e avaliar um pipeline de IA capaz de adaptar documentos regulatórios e financeiros complexos para diferentes públicos e formatos, garantindo rigor conceitual, adequação de vocabulário e fidelidade factual por meio de métricas objetivas e determinísticas?

## 4. Escopo

### No escopo

- Ingestão de PDFs/texto públicos (atas do Copom, fatos relevantes da CVM, releases da B3).
- Matriz de adaptação: 3 audiências × 3 formatos.
- Framework híbrido de avaliação (legibilidade, densidade de termos, factualidade, reflection loop).
- Interface comparativa da matriz de saídas e relatório de métricas.

### Fora do escopo

- Publicação automática em redes sociais.
- Renderização de vídeo com avatares sintéticos.
- Streaming de cotações em tempo real.

## 5. Arquitetura sugerida

1. Document Extractor & Anchor
2. Audience Adapters (paralelos)
3. Format Synthesizers
4. Hybrid Evaluator Node
5. Conditional Routing / Retry (Reflection Pattern)

## 6. Entregáveis

1. Pipeline de adaptação estruturada + GitHub com contribuições consistentes
2. Suíte de avaliação híbrida
3. Mecanismo de auto-correção (reflection loop)
4. Interface de demonstração e dashboard
5. Vídeo demonstrativo (critério eliminatório)
6. Relatório experimental e documentação
