Coloque aqui o arquivo de fonte 'Grinched' para o logo.

1. Baixe a fonte em: https://www.dafont.com/pt/grinched.font (ou outra fonte de sua preferência).
2. Extraia e renomeie o arquivo TTF para: Grinched-Regular.ttf
3. Coloque o arquivo em: static/fonts/Grinched-Regular.ttf

O template `templates/_base.html` já referencia esta fonte via @font-face e adiciona a classe CSS `.font-grinched`.
Se quiser usar outro nome de arquivo, atualize a chamada em `_base.html` onde `url_for('static', filename='fonts/Grinched-Regular.ttf')` é usado.