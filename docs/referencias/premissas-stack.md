# Premissas da stack

Contrato primeiro, gerador depois. Trocar lib sem mudar a pergunta do case não conta.

## Quem faz o quê

| Papel | Ferramenta | Faz | Não faz |
| --- | --- | --- | --- |
| Esteira com retry | LangGraph | Passar o estado entre nós | Escrever o texto |
| Escrever texto | OpenRouter (LLM) | Adapters e formatos | Dar nota confiável |
| Forma dos dados | Pydantic | JSON obrigatório (persona, âncoras, notas) | Opinião |
| Conta no código | pytest + Flesch + glossário | Legibilidade e jargão | “Infantilizou?” |
| Experimento | Pydantic Evals | Casos de ouro reproduzíveis | Gerar conteúdo |
| Decisão tipada | Jev (TypeSafe AI) | Sim/não, escolha, nota com probabilidade | Gerar parágrafo |
| PDF | pypdf | Ler ata/release | Buscar na web |
| HTML | Scrapling + trafilatura | Baixar e limpar página | Postar em rede social |

## OpenRouter

- Começar com modelo `:free`.
- Se qualidade ou limite falhar, um pago barato (ex. Flash/mini).
- Chave só em `.env` (`OPENROUTER_API_KEY`).

## Jev no avaliador híbrido

Jev não é LLM. É um modelo de **decisão** (System One): recebe o **estado** (fonte + texto gerado + âncoras) e perguntas tipadas:

- **Noul** — sim/não com probabilidade. Ex.: “este número aparece nas âncoras?”
- **Choice** — uma opção. Ex.: “este texto parece iniciante, intermediário ou avançado?”
- **Score** — escala. Ex.: “trivializou de 0 a 2?”

No grafo: métricas determinísticas sempre; Jev nas perguntas subjetivas/baratas; LLM só gera (e, se Jev estiver inseguro, um juiz OpenRouter de fallback).

Se não houver `TYPESAFE_API_KEY`, o pipeline segue com código + Pydantic Evals. Não travar o case na waitlist.

## Fora de escopo

APIs de rede social, avatar em vídeo, cotação em tempo real.
