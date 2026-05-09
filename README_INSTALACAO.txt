CuidarBem PWA - pacote corrigido

Correção aplicada:
- Arquivos renomeados exatamente como o manifest e o service worker procuram.
- icon-144.png incluído na raiz.
- favicon.ico incluído na raiz.
- Cache do Service Worker atualizado para forçar renovação.

Envie TODOS estes arquivos para a raiz do repositório CuidarBem no GitHub Pages:
- index.html
- manifest.webmanifest
- sw.js
- favicon.ico
- icon-48.png
- icon-72.png
- icon-96.png
- icon-128.png
- icon-144.png
- icon-152.png
- icon-180.png
- icon-192.png
- icon-512.png

Depois de subir:
1. Abra o site.
2. No DevTools > Application > Service Workers, clique em Update ou Unregister e recarregue.
3. No celular, limpe cache do site se continuar puxando versão antiga.
4. Teste se estes links abrem diretamente:
   /CuidarBem/icon-144.png
   /CuidarBem/favicon.ico


Atualização v19:
- Dados essenciais do paciente: tipo sanguíneo, peso, altura, médico principal e observações críticas.
- Resumo do cuidador na tela inicial.
- Histórico rápido de eventos/intercorrências.
- Exportação e importação de backup completo em JSON.
- Modo SAMU mostra dados essenciais e observações críticas.


CuidarBem v20 - Modo Família Sincronizado com Firebase

O que foi acrescentado:
- Card "Modo Família Sincronizado" em Perfil > Dados/App.
- Sincronização em tempo real via Firebase Authentication anônimo + Cloud Firestore.
- Código da família, exemplo: CUIDAR-4829.
- Quando um aparelho marca medicamento como tomado, os outros aparelhos da mesma família recebem a atualização.
- Sincroniza medicamentos, confirmações, dados essenciais do paciente, histórico rápido, sinais vitais e preferências.

Configuração no Firebase:
1. Acesse o console do Firebase e crie/abra seu projeto.
2. Em Authentication > Sign-in method, ative "Anonymous/Anônimo".
3. Em Firestore Database, crie o banco em modo production ou test.
4. Em Project settings > General > Your apps, crie um app Web.
5. Copie para o CuidarBem estes campos: apiKey, authDomain, projectId e appId.
6. No app CuidarBem, abra Perfil > Dados > Modo Família Sincronizado.
7. Cole os 4 campos, informe seu nome e toque em "Criar família".
8. No outro celular, cole os mesmos 4 campos, digite o mesmo código da família e toque em "Entrar / sincronizar".

Regras iniciais sugeridas do Firestore para teste controlado:

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /cuidarbem_families/{familyId} {
      allow read, write: if request.auth != null;
      match /state/{docId} {
        allow read, write: if request.auth != null;
      }
    }
  }
}

Observação importante:
- As chaves do Firebase Web são públicas por natureza, mas as regras do Firestore precisam estar corretas.
- Para uso familiar pequeno, o plano gratuito tende a ser suficiente.
- Fotos em base64 podem aumentar o tamanho do documento. Se o app crescer muito, o ideal será separar anexos/imagens em Storage.
