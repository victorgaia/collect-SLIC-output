# SLIC (Security Linter for Infrastructure as Code Scripts) for ansible
 
## Sobre a ferramenta:

Ferramenta que detecta security smells como hard-coded passwords em scripts Ansible. Referente ao trabalho Security Smells in Ansible and Chef Scripts: A Replication Study, dos autores Akond Rahman, Md. Rayhanur Rahman, Chris Parnin e Laurie Williams, disponível em: https://arxiv.org/abs/1907.07159.   
Ferramenta extraída da docker image https://hub.docker.com/r/akondrahman/slic_ansible

## Como usar:
No arquivo **AnsibleSmellDetector.py**:
 - Modificar o valor da variável *repo_dir_*, para o caminho do diretório onde estão localizados todos os projetos ansible
 - Modificar o valor da variável  *output_file_* para o caminho de onde o arquivo .csv de saída deve ser criado.

## Sobre o trabalho em desenvolvimento:
Utilização do SLIC for Ansible para identificar as ocorrências de smells em scrips de projetos particulares, com o intuito de comparar os resultados com os do artigo original supracitado, que analisa scripts de projetos abertos.

##

Favor encaminhar o arquivo de saída para o e-mail: victor.santos@icen.ufpa.br
