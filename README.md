# Viral Shop AI — versão inicial

Painel web responsivo para Android com:
- cadastro de produtos e links de afiliado;
- organização de ideias e fila de vídeos;
- registro manual de comissões e status;
- resumo de produtos, vídeos e ganhos.

## Rodar localmente
1. Instale Python 3.10 ou superior.
2. No terminal, entre nesta pasta.
3. Execute: `pip install -r requirements.txt`
4. Execute: `python app.py`
5. Abra `http://127.0.0.1:5000` no navegador.

## Publicar na nuvem (Render)
1. Crie um repositório GitHub e envie estes arquivos.
2. No Render, escolha New > Blueprint e conecte o repositório.
3. O Render lerá `render.yaml` e criará o serviço.
4. No painel do Render, configure `ADMIN_PASSWORD` com uma senha forte e exclusiva.
5. Configure `SECRET_KEY` como variável secreta forte (o Blueprint pode gerar uma automaticamente).
6. Para persistir o banco SQLite entre reinicializações, configure um disco persistente no Render e ajuste `DB_PATH` para o caminho do disco. O plano gratuito pode reiniciar e não é indicado para dados persistentes.

## Limitações e próxima integração
A tela do painel exige senha administrativa (`ADMIN_PASSWORD`). Esta é uma proteção inicial, não substitui controles de segurança profissionais.

Esta versão NÃO entra na conta TikTok, não escolhe produtos diretamente na TikTok Shop, não gera arquivos de vídeo por IA e não publica automaticamente.
Essas funções exigem credenciais, permissões e APIs oficiais apropriadas. A publicação pública depende da aprovação/auditoria do aplicativo e da autorização do criador. O vínculo da sacolinha de afiliado pode exigir uma integração/fluxo separado oferecido pelo TikTok Shop.
Não forneça senha, código SMS, cookies ou tokens da sua conta a terceiros. Não use automação de navegador para simular cliques, visualizações ou compras.
