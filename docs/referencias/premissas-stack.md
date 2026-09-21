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

- Escreve as três personas a partir das âncoras (modelo `:free` primeiro).
- Sem chave ou em pytest, usa rascunho fixo.
- Se qualidade ou limite falhar, um pago barato (ex. Flash/mini).
- Chave só em `.env` (`OPENROUTER_API_KEY`).

## Jev no avaliador híbrido

Jev não é LLM. É um modelo de **decisão** (System One): recebe o **estado** (fonte + texto gerado + âncoras) e perguntas tipadas:

- **Noul** — sim/não com probabilidade. Ex.: “este número aparece nas âncoras?”
- **Choice** — uma opção. Ex.: “este texto parece iniciante, intermediário ou avançado?”
- **Score** — escala. Ex.: “trivializou de 0 a 2?”

No grafo: métricas determinísticas sempre; **Jev está no escopo** para nivel aparente, grounding e trivialização. LLM só gera. Se Jev estiver inseguro, fallback OpenRouter depois.

Chave em `.env` (`TYPESAFE_API_KEY`). Sem chave o nó é pulado para os testes locais, mas a entrega usa Jev.

## Fora de escopo

APIs de rede social, avatar em vídeo, cotação em tempo real.
