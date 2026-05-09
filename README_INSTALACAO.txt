CuidarBem PWA v29 - Refinamento mobile

Alteração desta versão:
- Slogan da topbar em uma única linha: "Cuidado que conecta, saúde que acompanha."
- Cache do PWA atualizado para v29.

CuidarBem PWA v27 - Correção mobile header

Correção: Bom dia/Boa tarde e CuidarBem voltam a aparecer abaixo da topbar fixa. Hamburger removido, título duplicado do topo removido, sininho mantido no canto superior direito.

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


Versão v26 - Refinamento mobile da tela inicial:
- Removido hamburger da topbar mobile.
- Removido nome duplicado no centro da topbar.
- Sininho de alertas alinhado à direita, mais baixo e fixo.
- Topbar da home fixada no topo no mobile.

Versão v28:
- Topbar mobile fixa redesenhada.
- Saudação automática Bom dia/Boa tarde/Boa noite.
- Nome do app Cuidar Bem + slogan.
- Dia, data e horário HH:MM atualizando automaticamente.
- Paciente, botão SAMU e ações Ler resumo / Parar resumo / Modo simples na própria topbar.


Versão v30 - Central de Alertas
- Sininho agora abre a Central de Alertas.
- Ler resumo continua exclusivo para leitura por voz.
- Central mostra atrasados, próximos cuidados, avisos de receita/retirada e sincronização.


Versão v31:
- Central de Alertas do sininho agora abre centralizada no mobile.
- Janela com altura máxima visível, rolagem interna e botão fechar sempre acessível.
- Cache atualizado para v31.


Versão v32:
- Ajuste mobile: primeiro painel da tela inicial foi rebaixado para não ficar encoberto pela topbar fixa.
- Cache PWA atualizado para v32.


Versão v33:
- Ajuste mobile: o primeiro painel da tela inicial foi rebaixado ainda mais para ficar totalmente abaixo da topbar fixa.
- Cache PWA atualizado para v33.


Versão v34:
- Ajuste fino mobile: primeiro painel subiu um pouco, mas ainda com folga da topbar fixa.
- Cache PWA atualizado para v34.


Versão v35:
- Ajuste mobile: o primeiro painel da tela inicial subiu mais dois ajustes visuais, mantendo margem contra a topbar fixa.
- Cache PWA atualizado para v35.


Versão v36:
- Ajuste intermediário da tela inicial: o primeiro painel fica entre a v34 e a v35, subindo apenas um tanto.
- Cache PWA atualizado para v36.


Versão v37:
- Janela de detalhes do medicamento centralizada no mobile.
- Adicionado botão Excluir medicamento dentro dos detalhes.
- Cache PWA atualizado para v37.


Versão v38:
- Corrigido botão Excluir medicamento na janela centralizada.
- Adicionado botão de exclusão para exercícios, fisioterapia, consultas e exames.
- Ao excluir, remove confirmações relacionadas, reagenda alertas e sincroniza com a família.
- Cache PWA atualizado para v38.


Versão v39:
- Substituída a confirmação nativa do navegador ao excluir por uma janela personalizada do app.
- A mensagem agora aparece limpa: Excluir..., sem 'ceducunha-alt0609.github.io diz'.
- Mantida exclusão de medicamentos, exercícios, fisioterapia, consultas e exames com sincronização familiar.
- Cache PWA atualizado para v39.


Versão v40:
- Topbar fixa aplicada em todas as guias no mobile: Calendário, Relatórios, Configurações, Escanear Receita, Saúde e Consultas/Exames.
- Conteúdo das guias rebaixado para não ficar encoberto pela topbar.
- Cache PWA atualizado para v40.


Versão v41:
- Correção mobile na Agenda > Nova tarefa: janela centralizada, com altura controlada e rolagem interna.
- Parte inferior da janela não fica mais escondida atrás da barra inferior.
- Cache PWA atualizado para v41.


Versão v42:
- Ajuste mobile na guia Saúde: os 3 cards iniciais foram rebaixados para aparecerem abaixo da topbar fixa.
- Cache PWA atualizado para v42.


Versão v43:
- Ajuste fino na guia Saúde: os 3 cards iniciais subiram um pouco em relação à v42, mantendo folga da topbar fixa.
- Cache PWA atualizado para v43.


Versão v44:
- Corrigido travamento na guia Escanear Receita quando a IA externa não responde.
- A foto da receita permanece visível e o app abre preenchimento manual seguro para adicionar o medicamento.
- Botão para tentar IA novamente, sem perder a foto carregada.
- Cache PWA atualizado para v44.


Versão v45 — IA/edição de receitas:
- Adicionado README_IA_RECEITAS.txt com o passo a passo para habilitar a leitura por IA via Supabase Edge Function.
- Adicionada pasta supabase/functions/analisar-receita com função segura para OpenAI.
- Medicamentos lidos/preenchidos na receita agora podem ser editados antes de salvar.
- Medicamentos já cadastrados podem ser editados pela janela de detalhes.
- Cache PWA atualizado para v45.


Versão v46:
- Corrigido o botão Editar medicamento na janela de detalhes.
- Agora é possível alterar nome, dose, horário, repetição, observações, validade da receita e próxima retirada.
- Ao salvar, o app atualiza a rotina, reagenda alertas e sincroniza com a família.
- Cache PWA atualizado para v46.


Versão v47:
- Adicionado editar para exercícios, fisioterapia, consultas e exames.
- Mantido editar/excluir medicamentos.
- Edições reagendam alertas, atualizam a tela e sincronizam com a família.
- Cache PWA atualizado para v47.


Versão v48:
- Corrigido tremor/pisca ao editar medicamento no mobile.
- O editor agora abre sozinho, sem a janela de detalhes animando por baixo.
- Ao salvar, atualiza rotina, alertas e sincronização sem reabrir outra janela automaticamente.
- Cache PWA atualizado para v48.


Versão v49:
- Corrigido tremor/pisca na tela inicial após editar medicamento.
- Salvamento agora estabiliza a renderização da home e preserva a posição da tela.
- Cache PWA atualizado para v49.


Versão v50:
- Corrigido pisca/tremor na tela inicial após editar medicamento.
- Removido ícone duplicado de editar no card de medicamento.
- Atualização do medicamento agora altera apenas o card necessário, sem recarregar a lista inteira da home.
- Cache PWA atualizado para v50.
