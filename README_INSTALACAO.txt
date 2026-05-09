CuidarBem PWA v23 - Supabase Sync automático

Arquivos necessários incluídos:
- index.html
- manifest.webmanifest
- sw.js
- SUPABASE_SETUP.sql
- icon-48.png, icon-72.png, icon-96.png, icon-128.png, icon-144.png, icon-152.png, icon-180.png, icon-192.png, icon-512.png
- favicon.ico

Como publicar no GitHub Pages:
1. Envie TODOS os arquivos desta pasta para a raiz do repositório CuidarBem.
2. Substitua os arquivos antigos.
3. Aguarde o GitHub Pages publicar.
4. Acesse: https://ceducunha-alt0609.github.io/CuidarBem/

Configuração obrigatória no Supabase:
1. Abra o projeto Supabase.
2. Vá em SQL Editor > New query.
3. Cole todo o conteúdo do arquivo SUPABASE_SETUP.sql.
4. Clique em Run.
5. No painel do Supabase, verifique se Realtime está ativo para o projeto.

Como usar o Modo Família:
1. No primeiro celular, abra CuidarBem > Configurações.
2. Em Modo Família Sincronizado, clique em Criar família.
3. Copie o código completo, por exemplo: CUIDAR-4829-ABCD.
4. No celular do familiar/cuidador, cole o mesmo código e clique em Entrar / sincronizar.
5. Ao marcar medicamento tomado, exercício/fisio feito, consulta/exame confirmado, sinais vitais ou dados do paciente, o outro aparelho recebe atualização automaticamente. O botão "Forçar envio" é apenas para emergência/cache.

Importante:
- Compartilhe apenas o código completo com pessoas autorizadas.
- O código completo funciona como chave familiar.
- Não teste instalação abrindo pelo arquivo C:\...\index.html. PWA precisa de HTTPS ou localhost.
- No Android/Chrome e PC/Edge/Chrome deve aparecer instalar app.
- No iPhone/iPad: Compartilhar > Adicionar à Tela de Início.


Correção v22:
- Corrigido erro JavaScript: shouldShowToday is not defined.
- Atualizado cache do Service Worker para forçar recarregamento da versão corrigida.


Atualização v23:
- Sincronização automática reforçada em localStorage.
- Ao marcar remédio tomado, exercício/fisioterapia feito ou compromisso confirmado na tela inicial, o app envia para o Supabase sem precisar clicar em enviar.
- Botão manual renomeado para Forçar envio.
- Cache do Service Worker atualizado para v23.

Atualização v24 — Alerta Inteligente + Limpeza inicial
- Configurações > Dados > Limpeza inicial:
  * Limpar remédios demo
  * Limpar tarefas demo
  * Zerar cuidados
- Alertas inteligentes para remédios, fisioterapia e exercícios:
  * 15 minutos antes
  * no horário
  * 15 minutos depois
  * repetição a cada 5 minutos enquanto estiver pendente (remédios por até 3h; fisio/exercícios por até 1h30)
- Ao confirmar tomado/feito, o app reagenda os alarmes e sincroniza automaticamente com a família.

Observação importante: Android/Chrome e PWAs não garantem toque contínuo infinito como despertador nativo. O app usa notificações persistentes, vibração, renotificação e repetição programada, respeitando as limitações do navegador/sistema.


CuidarBem v25 Premium Layout
- Redesign visual inspirado no mockup premium aprovado.
- Nova camada visual para Home, tarefas, cards, bottom nav/sidebar, perfil, modais e confirmação de medicação.
- Mantém a lógica operacional da v24: Supabase Sync, alertas inteligentes, limpeza de dados demo e PWA.
- Cache atualizado para cuidarbem-pwa-v25-premium-layout.
