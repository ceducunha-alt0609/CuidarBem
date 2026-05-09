CuidarBem PWA v21 - Supabase Sync

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
5. Ao marcar medicamentos, eventos, sinais vitais ou dados do paciente, o outro aparelho recebe atualização.

Importante:
- Compartilhe apenas o código completo com pessoas autorizadas.
- O código completo funciona como chave familiar.
- Não teste instalação abrindo pelo arquivo C:\...\index.html. PWA precisa de HTTPS ou localhost.
- No Android/Chrome e PC/Edge/Chrome deve aparecer instalar app.
- No iPhone/iPad: Compartilhar > Adicionar à Tela de Início.


Correção v22:
- Corrigido erro JavaScript: shouldShowToday is not defined.
- Atualizado cache do Service Worker para forçar recarregamento da versão corrigida.
