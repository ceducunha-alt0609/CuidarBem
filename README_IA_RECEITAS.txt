CuidarBem v45 — Como habilitar IA para ler receitas

IMPORTANTE:
Nunca coloque uma chave secreta de OpenAI/Anthropic direto no index.html do GitHub Pages.
Use uma Supabase Edge Function como ponte segura.

Arquivos incluídos:
- supabase/functions/analisar-receita/index.ts

Passo a passo recomendado:
1. Instale/abra o Supabase CLI no computador.
2. Dentro da pasta deste pacote, rode:
   supabase login
   supabase link --project-ref lwldroopbooeocchgngg
3. Configure sua chave da OpenAI como segredo do Supabase:
   supabase secrets set OPENAI_API_KEY=sua_chave_aqui
   supabase secrets set OPENAI_MODEL=gpt-5.5
4. Publique a função:
   supabase functions deploy analisar-receita
5. Volte ao app, tire/carregue a foto da receita e clique em Analisar com IA.

Se a função não estiver publicada ou a chave não estiver configurada, o app não trava:
ele abre o preenchimento manual seguro.

Atualização v45:
- Medicamentos identificados pela IA agora podem ser editados antes de salvar.
- Medicamento adicionado manualmente também pode ser editado antes de salvar.
- Medicamento já cadastrado pode ser editado na janela de detalhes, sem excluir e cadastrar novamente.
